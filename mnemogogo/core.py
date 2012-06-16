#
# Copyright (C) 2009 Timothy Bourke
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import sys
import os
import os.path
import shutil
import re
import itertools
import random
import traceback
import time, datetime, calendar
from PyQt4.QtGui import QImage

interface_classes = []

_logger = None
max_config_size = 50
HOUR = 60 * 60
DAY = 24 * HOUR

marked_tag = "Gogomarked"

def set_logger(new_logger):
    global _logger
    _logger = new_logger

def logger():
    global _logger
    return _logger

def phonejoin(paths):
    if len(paths) == 0: return ""

    r = paths[0]
    for p in paths[1:]:
        r = "/".join([r, p])
        if ((len(r) > 0) and ((r[-1] == '/') or r[-1] == '\\')):
            r = r[0:-1]

    return r

class _RegisteredInterface(type):
    def __new__(meta, classname, bases, classdict):
        newClass = type.__new__(meta, classname, bases, classdict)

        if classname != "Interface":
            interface_classes.append(newClass)

        return newClass

learning_data = [
    'grade',
    'easiness',
    'acq_reps',
    'ret_reps',
    'lapses',
    'acq_reps_since_lapse',
    'ret_reps_since_lapse',
    'last_rep',
    'next_rep',
    'unseen',
    ]

learning_data_len = {
    'grade'                 : 1,
    'easiness'              : 4,
    'acq_reps'              : 4,
    'ret_reps'              : 4,
    'lapses'                : 4,
    'acq_reps_since_lapse'  : 4,
    'ret_reps_since_lapse'  : 4,
    'last_rep'              : 8,
    'next_rep'              : 8,
    'unseen'                : 1,
    }

easiness_accuracy = 1000

class Mnemogogo(Exception):

    # Core errors

    ErrInitInterface = 0
    ErrRegInterface  = 1
    ErrAnotherDB     = 2

    # Interface errors
    ErrExportFailed  = 100
    ErrCannotOpen    = 101
    ErrCannotFind    = 102
    ErrShortStats    = 103

    def __init__(self, err, details, iface=None):
        self.err = err
        self.details = details
        self.iface = iface

######################################################################
# Interfaces

class Job:
    learning_data = learning_data
    learning_data_len = learning_data_len

    def __init__(self, interface, sync_path, debug):
        self.interface = interface
        self.sync_path = sync_path
        self.percentage_complete = 0
        self.debug = debug

    # implement in plugin
    def close(self):
        pass

    def error(self, err, details):
        raise Mnemogogo(err, details, iface=self.interface.description)

class Export(Job):
    re_img_split = re.compile(r'(<img.*?>)')
    re_img = re.compile( r'(?P<all>(?P<before><img\s+[^>]?)'
                        + '((height|width)\s*=\s*"?[0-9]*"?\s*)*'
                        + 'src\s*=\s*"(file:(\\\\\\\\\\\\|//))?(?P<path>[^"]*)"'
                        + '((height|width)\s*=\s*"?[0-9]*"?)*'
                        + '(?P<after>[^>]*/?>))',
                        re.IGNORECASE + re.MULTILINE + re.DOTALL)

    re_snd_split = re.compile(r'(<audio.*?>)')
    re_snd = re.compile( r'(?P<all>(?P<before><audio\s+[^>]?)'
                        + 'src\s*=\s*"(file:(\\\\\\\\\\\\|//))(?P<path>[^"]*)"'
                        + '(?P<after>[^>]*/?>))',
                        re.IGNORECASE + re.MULTILINE + re.DOTALL)

    ErrExportFailed  = Mnemogogo.ErrExportFailed
    ErrCannotOpen    = Mnemogogo.ErrCannotOpen
    ErrCannotFind    = Mnemogogo.ErrCannotFind

    def __init__(self, interface, sync_path, debug):
        Job.__init__(self, interface, sync_path, debug)

        self.categories = []
        self.imgs = {}
        self.img_cnt = 0
        self.snds = {}
        self.snd_cnt = 0
        self.name_with_numbers = True

        self.dir_indices = {}

        self.img_max_width = None
        self.img_max_height = None
        self.img_to_landscape = False
        self.img_to_ext = None

    # implement in plugin
    def open(self, start_date, num_days, num_cards, params):
        pass

    # implement in plugin
    def write(self, id, q, a, cat, stats, inverse_id, is_overlay):
        pass

    def write_config(self, config):
        pass

    # # # Utility routines # # #

    def tidy_files(self, dst_subdir, list):
        dstpath = os.path.join(self.sync_path, dst_subdir)

        for file in os.listdir(dstpath):
            if phonejoin([dst_subdir, file]) not in list:
                try:
                    os.remove(os.path.join(dstpath, file))
                except:
                    logger().log_warning ("Could not remove: %s" % file)

    def tidy_images(self, dst_subdir):
        self.tidy_files(dst_subdir, self.imgs.values())

    def tidy_sounds(self, dst_subdir):
        self.tidy_files(dst_subdir, self.snds.values())
    
    def add_style_file(self, dstpath):
        shutil.copy(os.path.join(self.gogo_dir, 'style.css'), dstpath)

    def category_id(self, cat):
        try:
            i = self.categories.index(cat)
        except ValueError:
            i = len(self.categories)
            self.categories.append(cat)
        return i

    def map_paths(self, reg, re_split, text, mapping):
        stext = re_split.split(text)
        ntext = []

        for ele in stext:
            r = reg.match(ele)
            if r:
                ele = (r.group('before')
                       + ' src="' + mapping[r.group('path')]
                       + '" ' + r.group('after'))
            ntext.append(ele)

        return ''.join(ntext)

    def convert_img(self, src, dst_subdir, dst_name, dst_ext):
        dst_file = dst_name + '.' + dst_ext
        dst = os.path.join(self.sync_path, dst_subdir, dst_file)

        if not os.path.exists(src):
            logger().log_warning("image not found: %s" % src)
            return (False, 'NOTFOUND.PNG')

        if (os.path.exists(dst) and
                (os.path.getmtime(src) < os.path.getmtime(dst))):
            return (False, dst_file)

        im = QImage(src)
        (width, height) = (im.width(), im.height())

        if (self.img_to_landscape and self.img_max_width
                and float(width) > (height * 1.2)
                and width > self.img_max_width):
            matrix = QWMatrix()
            im = im.xForm(matrix.rotate(90))
            (width, height) = (im.width(), im.height())
        
        (wratio, hratio) = (1.0, 1.0)
        if self.img_max_width and width > self.img_max_width:
            wratio = width / float(self.img_max_width);
        
        if self.img_max_height and height > self.img_max_height:
            hratio = height / float(self.img_max_height);
        
        ratio = max(wratio, hratio)
        if ratio != 1.0:
            im = im.scaled(int(width / ratio), int(height / ratio))
            (width, height) = (im.width(), im.height())
        
        if self.img_max_size:
            tmpdstdir = os.tempnam()
            os.mkdir(tmpdstdir)
            tmpdst = os.path.join(tmpdstdir, '_gogo_scaling.png')

            r = im.save(tmpdst, 'PNG')
            if not r:
                logger().log_warning('unable to export the image: %s' % src)
                return (True, dst_file)

            (nwidth, nheight) = (width, height)
            while (os.path.getsize(tmpdst) > self.img_max_size):
                (owidth, oheight) = (nwidth, nheight)
                scale = 0.9
                while ((nwidth == owidth or nheight == oheight)
                       and scale > 0.0):
                    (nwidth, nheight) = (int(nwidth * scale),
                                         int(nheight * scale))
                    scale = scale - .1

                if nwidth > 0 and nheight > 0:
                    im = im.scaled(nwidth, nheight)
                    im.save(tmpdst, 'PNG')
                else:
                    break;
            shutil.rmtree(tmpdstdir)

        im.save(dst, dst_ext.upper())
        return (True, dst_file)
    
    def directory_index(self, dir_path):

        if self.dir_indices.has_key(dir_path):
            idx = self.dir_indices[dir_path]
        else:
            idx = len(self.dir_indices)
            self.dir_indices[dir_path] = idx
        
        if idx == 0:
            return ""
        else:
            return "_" + str(idx)

    def handle_images(self, dst_subdir, text):
        for r in self.re_img.finditer(text):
            src = r.group('path')

            if not (src in self.imgs):
                self.debug("gogo:img: processing %s" % src)
                (src_dir, src_base) = os.path.split(src)
                (src_root, src_ext) = os.path.splitext(src_base)
                if self.name_with_numbers:
                    name = '%08X' % self.img_cnt
                else:
                    name = src_root.encode('punycode').upper()\
                                .replace(' ', '_')\
                                .replace('?', '_qu-')\
                                .replace('*', '_ast-')\
                                .replace(':', '_col-')
                    name = name + self.directory_index(src_dir)
                self.img_cnt += 1

                (moved, dst) = self.convert_img(src, dst_subdir, name,
                        self.img_to_ext)
                self.debug("gogo:img: moved to %s" % dst)

                self.imgs[src] = phonejoin([dst_subdir, dst])

        return self.map_paths(self.re_img, self.re_img_split, text, self.imgs)

    def handle_sounds(self, dst_subdir, text):
        ntext = []

        for r in self.re_snd.finditer(text):
            src = r.group('path')

            if src in self.snds:
                ntext.append('<sound src="%s" />' % self.snds[src])
            else:
                self.debug("gogo:snd: processing %s" % src)
                (src_dir, src_base) = os.path.split(src)
                (src_root, src_ext) = os.path.splitext(src_base)
                if self.name_with_numbers:
                    name = '%08X' % self.snd_cnt
                else:
                    name = src_root.encode('punycode').upper()\
                                .replace(' ', '_')\
                                .replace('?', '_qu-')\
                                .replace('*', '_ast-')\
                                .replace(':', '_col-')
                    name = name + self.directory_index(src_dir)
                self.snd_cnt += 1

                dst = name + src_ext
                dst_path = os.path.join(self.sync_path, dst_subdir, dst)
                try:
                    shutil.copy(src, dst_path)
                    self.debug("gogo:snd: copied to %s" % dst_path)
                    self.snds[src] = phonejoin([dst_subdir, dst])
                    ntext.append('<sound src="%s" />' % self.snds[src])

                except IOError:
                    logger().log_warning("sound file not found: %s" % src)
        
        ntext.append(self.re_snd_split.sub('', text))
        return '\n'.join(ntext)

class Import(Job):
    ErrCannotOpen    = Mnemogogo.ErrCannotOpen
    ErrCannotFind    = Mnemogogo.ErrCannotFind
    ErrShortStats    = Mnemogogo.ErrShortStats

    def __iter__(self):
        self.open()
        self.num_log_entries = 0
        return self

    def next(self):
        r = self.read()

        if r is None:
            self.close()
            raise StopIteration

        return r

    # implement in plugin
    def open(self):
        pass

    # implement in plugin
    def read(self):
        return None

class Interface:
    __metaclass__ = _RegisteredInterface

    # # # Override # # #

    description = 'unknown'
    version = '0.0.0'

    def load(self):
        pass

    def unload(self):
        pass

    def start_export(self, sync_path, debug):
        return Export(self, sync_path, debug)

    def start_import(self, sync_path, debug):
        return Import(self, sync_path, debug)


######################################################################
# Implementation

interfaces = []

def register_interfaces(basedir):
    interface_dir = unicode(os.path.join(basedir,
                            "plugins", "mnemogogo", "interface"))
    
    for file in os.listdir(interface_dir):
        if (not file.endswith(".py")) or file.startswith("_"):
            continue
        
        try:
            __import__("mnemogogo.interface." + file[:-3])
        except: raise Mnemogogo(Mnemogogo.ErrInitInterface, 
                                file + '\n' + traceback.format_exc())

    for iface in interface_classes:
        try:
            obj = iface()
            name = iface.__name__
            desc = obj.description
        except: raise Mnemogogo(Mnemogogo.ErrRegInterface,
                                file + '\n' + traceback.format_exc())

        interfaces.append({ 'name' : name,
                            'description' : desc,
                            'object' : obj })

    return interfaces

def list_interfaces():
    return interfaces

# These utility functions were modified from Mnemosyne 2.x code
# originally written by <Peter.Bienstman@UGent.be>.

def midnight_UTC(timestamp):        
    date_only = datetime.date.fromtimestamp(timestamp).timetuple()
    return int(calendar.timegm(date_only))

def adjusted_now(now=None, day_starts_at = 3):
    if now == None:
        now = time.time()
    now -= day_starts_at * HOUR

    if time.localtime(now).tm_isdst and time.daylight:
        now -= time.altzone
    else:
        now -= time.timezone
    return int(now)

# Return enough cards for rebuild_revision_queue on the mobile device to
# work with for the given number of days.
def cards_for_ndays(db, days = 0, extra = 1.00, day_starts_at = 3,
                    grade_0_items_at_once = 5):
            
    end_date = adjusted_now(time.time() + days * DAY, day_starts_at)
    limit = grade_0_items_at_once * (days + 1) * extra

    cards = list(db.cards_due_for_ret_rep(end_date))

    if limit > 0:
        relearn1 = list(db.cards_to_relearn(grade=1, limit=limit))
        limit -= len(relearn1)
        cards.extend(relearn1)

    if limit > 0:
        relearn0 = list(db.cards_to_relearn(grade=0, limit=limit))
        limit -= len(relearn0)
        cards.extend(relearn0)

    if limit > 0:
        newmem0 = list(db.cards_new_memorising(grade=0, limit=limit))
        limit -= len(newmem0)
        cards.extend(newmem0)

    if limit > 0:
        newmem1 = list(db.cards_new_memorising(grade=1, limit=limit))
        limit -= len(newmem1)
        cards.extend(newmem1)

    if limit > 0:
        unseen = list(db.cards_unseen(limit=limit))
        cards.extend(unseen)

    return cards

def card_to_stats(card, unseen_compat=True):
    stats = {}
    for f in learning_data:
        if f == 'easiness':
            stats[f] = int(round(card.easiness * easiness_accuracy))
        elif f == 'unseen':
            stats[f] = int(card.grade == -1)
        elif f == 'last_rep':
            # Compatibility with Mnemosyne 1.x: last_rep in days, not
            # seconds; last_rep is UTC, so we must convert it to local time.
            # Imagine that we last saw a card in Sydney at: 1325807500
            #   UTC:            2012-01-05 23:51    (stored in db)
            #   local (UTC+10): 2012-01-06 10:51
            # When we reduce this time stamp to days since the epoch in local
            # time, we want 0x3bf1 (Jan-6) not 0x3bf0 (Jan-5).
            local = datetime.date.fromtimestamp(getattr(card, f)).timetuple()
            stats[f] = int(calendar.timegm(local) / DAY)
        elif f == 'next_rep':
            # Compatibility with Mnemosyne 1.x: next_rep in days, not
            # seconds; next_rep is always midnight (UTC) of the day when a
            # repetition is due, so we do not convert to local time.
            stats[f] = int(getattr(card, f) / DAY)
        else:
            stats[f] = int(getattr(card, f))

    if unseen_compat and stats['unseen']:
        stats['grade'] = max(0, stats['grade'])
        stats['acq_reps'] = max(0, stats['acq_reps'])
        stats['acq_reps_since_lapse'] = max(0, stats['acq_reps_since_lapse'])
        stats['last_rep'] = max(0, stats['last_rep'])
        stats['next_rep'] = max(0, stats['next_rep'])

    return stats

def stats_to_card(stats, card, day_starts_at=3):
    for f in learning_data:
        if f == 'easiness':
            card.easiness = float(stats[f]) / easiness_accuracy
        elif f == 'unseen':
            pass
        elif f == 'last_rep':
            # Compatibility with Mnemosyne 1.x: last_rep in days, not seconds.
            # The value being imported is the number of days since 1970-01-01.
            # We assume that the review took place at the time of import.
    
            if time.daylight:
                tzoff = -time.altzone
            else:
                tzoff = -time.timezone
            timestamp = stats[f] * DAY + tzoff + day_starts_at * HOUR
            setattr(card, f, timestamp)

        elif f == 'next_rep':
            if card.grade < 2:
                # Satisfy an assert in schedulers/SM2_mnemosyne
                setattr(card, f, card.last_rep)
            else:
                # Compatibility with Mnemosyne 1.x: next_rep in days, not seconds.
                # Multiplying by DAY gives midnight UTC on the scheduled day as
                # required.
                setattr(card, f, stats[f] * DAY)
        else:
            setattr(card, f, int(stats[f]))

def dictlist(keyvals):
    r = {}
    for k, v in keyvals:
        if k in r:
            r[k].append(v)
        else:
            r[k] = [v]
    return r

def do_export(interface, num_days, sync_path, mnemodb, mnemoconfig, debug_print,
              progress_bar=None, extra = 1.00, max_width = 240,
              max_height = 300, max_size = 64):

    basedir = mnemoconfig.data_dir

    exporter = interface.start_export(sync_path, debug_print)
    exporter.gogo_dir = unicode(os.path.join(basedir, "plugins", "mnemogogo"))
    exporter.progress_bar = progress_bar

    grade_0_at_once = mnemoconfig["non_memorised_cards_in_hand"]
    day_starts_at = mnemoconfig["day_starts_at"]

    config = {
            'log_format' : '2',
            'day_starts_at' : day_starts_at,
            'grade_0_items_at_once' : grade_0_at_once,
            'logging' : "1",
            'database'
                : get_database(mnemoconfig).encode('punycode')[-max_config_size:],
        }

    params = {
            'max_width' : max_width,
            'max_height' : max_height,
            'max_size' : max_size,
        }

    cards = cards_for_ndays(mnemodb, num_days, extra,
                            int(mnemoconfig["day_starts_at"]), grade_0_at_once)
    card_ids = [ card_id for card_id, fact_id in cards ]
    card_to_fact = dict(cards)
    fact_to_card = dictlist((v, k) for k, v in cards)

    total = len(cards)
    current = 0

    exporter.open(datetime.date.fromtimestamp(0), num_days, total, params)
    exporter.id_to_serial = dict(zip((str(i) for i in card_ids),
                                 range(0, total)))
    exporter.write_config(config)
    for card_id in card_ids:
        card = mnemodb.card(card_id, is_id_internal=True)
        stats = card_to_stats(card, unseen_compat=True)
        stats['marked'] = len([tag.name for tag in card.tags
                                        if tag.name == marked_tag]) != 0

        q = card.question(render_chain="mnemogogo")
        a = card.answer(render_chain="mnemogogo")
        is_overlay = card.fact_view.a_on_top_of_q

        try:
            inverse_id = [ i for i in fact_to_card[card_to_fact[card_id]]
                             if i != card_id ][0]
        except KeyError: inverse_id = None
        except IndexError: inverse_id = None

        try:
            category = [t.name for t in card.tags
                               if t.name != marked_tag
                                    and t.name != "__UNTAGGED__"][0]
        except IndexError:
            category = 'None'

        exporter.write(str(card_id), q, a, category, stats,
                       str(inverse_id), is_overlay)

        if progress_bar:
            progress_bar.setProperty("value", exporter.percentage_complete)

    exporter.close()

# Some of this code was adapted from Peter Bienstman's
# ScienceLogParser.parse_repetition in Mnemosyne 2.x.
def log_repetition(mnemodb, repetition_chunk, rep_data={}, to_user={}):

    # Parse chunk.
    blocks = repetition_chunk.split(" | ")
    logtype, card_id, grade, easiness = blocks[0].split(" ")
    if not to_user.has_key(card_id): return

    grade = int(grade)
    easiness = float(easiness)

    acq_reps, ret_reps, lapses, acq_reps_since_lapse, \
        ret_reps_since_lapse = blocks[1].split(" ")
    acq_reps, ret_reps = int(acq_reps), int(ret_reps)
    lapses = int(lapses)
    acq_reps_since_lapse = int(acq_reps_since_lapse)
    ret_reps_since_lapse = int(ret_reps_since_lapse)  

    scheduled_interval, actual_interval = blocks[2].split(" ")
    scheduled_interval = int(scheduled_interval)
    actual_interval = int(actual_interval)
    new_interval, noise = blocks[3].split(" ")
    new_interval = int(float(new_interval)) + int(noise)

    thinking_time = round(float(blocks[4]))

    if logtype == 'S': # 'S': updated 2.x style log entry
        timestamp, last_rep, next_rep = blocks[5].split(" ")
        timestamp = long(timestamp)

        # long(last_rep) is the number of days since the epoch, but the number
        # of seconds is needed, so just use the timestamp.
        last_rep = timestamp # long(last_rep)
        next_rep = long(next_rep) * DAY

    else: # 'R': 1.x style log entry, daily accuracy
          # see also: cards_to_stats
        actual_interval    *= DAY
        scheduled_interval *= DAY
        new_interval       *= DAY

        if acq_reps == 1 and ret_reps == 0: # first repetition of new card
            timestamp = time.time()
            actual_interval = 0

            # these values are wrong, but it's not clear how to do anything
            # better in general (maybe keep the timestamp of the previous card?)
            last_rep = 0
            next_rep = timestamp + new_interval

        else:
            try:
                last_rep, next_rep = rep_data[card_id]

                if next_rep - last_rep != scheduled_interval:
                    logger().log_info(
                        "Invalid scheduled_interval: %s next=%d last=%d interval=%d" % (
                            card_id, next_rep, last_rep, scheduled_interval))
                    raise Exception

                else:
                    timestamp = last_rep + actual_interval

                    last_rep = timestamp
                    next_rep = timestamp + new_interval
                    rep_data[card_id] = (last_rep, next_rep)

            except:
                timestamp = time.time()
                actual_interval = 0
                last_rep = 0
                next_rep = 0

    # Note: we bypass the Logger.repetition() interface because that routine
    #       does not allow us to pass a timestamp.
    mnemodb.log_repetition(timestamp, to_user[card_id], grade,
        easiness, acq_reps, ret_reps, lapses,
        acq_reps_since_lapse, ret_reps_since_lapse,
        scheduled_interval, actual_interval,
        thinking_time, next_rep, scheduler_data=0)

def do_import(interface, sync_path, mnemodb, mnemoconfig, mnemoscheduler,
              debug_print, progress_bar=None):
    importer = interface.start_import(sync_path, debug_print)
    importer.progress_bar = progress_bar

    import_config = importer.read_config()
    if (import_config.has_key('database')):
        curr_database = get_database(mnemoconfig).encode('punycode')[-max_config_size:]
        load_database = import_config['database']
        if load_database != curr_database:
            raise Mnemogogo(Mnemogogo.ErrAnotherDB,
                            (load_database, curr_database))
                    
 
    if import_config.has_key('day_starts_at'):
        day_starts_at = int(import_config['day_starts_at'])
    else:
        day_starts_at = int(mnemoconfig['day_starts_at'])

    new_stats = []
    to_user = {}
    rep_data = {}
    count = 0
    for (card_id, stats) in importer:
        count = count + 1
        try:
            card = mnemodb.card(card_id, is_id_internal=True)

            to_user[str(card._id)] = card.id
            rep_data[str(card._id)] = (card.last_rep, card.next_rep)
        except:
            card = None

        if card is not None:
            new_stats.append((card, stats))
        else:
            logger().log_error("Quietly ignoring card with missing id: %s" % card_id)

        if (progress_bar and (count % 50 == 0)):
            progress_bar.setProperty("value", importer.percentage_complete / 3)

    log_total = importer.num_log_entries

    # Only update the database if the entire read is successful
    marked_cards   = []
    unmarked_cards = []

    cards_done = 0
    cards_total = len(new_stats) 
    for (card, stats) in new_stats:
        cards_done = cards_done + 1
        if stats['unseen']: continue

        stats_to_card(stats, card, day_starts_at)

        if ('marked' in stats) and (stats['marked']):
            marked_cards.append(card._id)
        else:
            unmarked_cards.append(card._id)

        mnemoscheduler.avoid_sister_cards(card)
        mnemodb.update_card(card, repetition_only=True)

        if (progress_bar and (cards_done % 50 == 0)):
            progress_bar.setProperty("value",
                 33 + ((cards_done * 100) / cards_total / 3))

    shutil.move(os.path.join(sync_path, 'STATS.CSV'),
                os.path.join(sync_path, 'OLDSTATS.CSV'))

    # Update cards tagged as 'marked'
    if unmarked_cards:
        tags = [ tag for tag in mnemodb.tags() if tag.name == marked_tag]
        if tags:
            mnemodb.remove_tag_from_cards_with_internal_ids(tags[0], unmarked_cards)

    if marked_cards:
        tag = mnemodb.get_or_create_tag_with_name(marked_tag)
        mnemodb.add_tag_to_cards_with_internal_ids(tag, marked_cards)
    elif tags:
        mnemodb.delete_tag_if_unused(tags[0])

    # Import logging details
    logpath = os.path.join(sync_path, 'LOG')
    if os.path.exists(logpath):
        log = open(logpath)

        logger().log_info('starting log import')
        log_done = 0
        line = log.readline()
        while line != '':
            log_done = log_done + 1
            log_repetition(mnemodb, line.rstrip('\n'), rep_data, to_user)
            line = log.readline()
            if (progress_bar and (log_done % 50 == 0)):
                progress_bar.setProperty("value",
                     66 + ((log_done * 100) / log_total / 3))

        logger().log_info('finished log import')

        log.close()
        os.remove(logpath)

    # Save the database
    mnemodb.save()

def get_database(config):
    try:
        mempath =  config["path"]
    except KeyError:
        mempath = "default.mem"

    return mempath[:-4]

def get_config_key(config):
    mempath = get_database(config)

    if mempath == "default":
        config_key = "mnemogogo"
    else:
        config_key = "mnemogogo:" + mempath

    return config_key

class Logger:
    logfile = None
    read_logfile = False

    def __init__(self, basedir):
        logname = os.path.join(basedir, "gogolog.txt")

        try:
            size = os.path.getsize(logname) 
        except:
            size = 0

        if size > 32768:
            self.logfile = file(logname, "w")
        else:
            self.logfile = file(logname, "a")

    def log_info(self, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print >> self.logfile, "%s : mnemogogo: %s" % (timestamp,
                                                       msg.encode('utf-8'))
        self.logfile.flush()

    def log_warning(self, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print >> self.logfile, "%s : mnemogogo: %s" % (timestamp,
                                                       msg.encode('utf-8'))
        self.logfile.flush()

    def log_error(self, msg):
        self.read_logfile = True
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print >> self.logfile, "%s : mnemogogo: %s" % (timestamp,
                                                       msg.encode('utf-8'))
        self.logfile.flush()

    def check_log_status(self):
        return self.read_logfile

    def clear_log_status(self):
        self.read_logfile = False

