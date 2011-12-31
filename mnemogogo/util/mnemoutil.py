#!/usr/bin/env python

#
# Mnemoutil <tim@tbrk.org>
#
# Parts of this code are taken directly from Peter Bienstman's 2.x codebase.
#

import os, time, datetime, calendar
import types
from optparse import OptionParser
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

version = "0.5.0"

HOUR = 60 * 60  # Seconds in an hour. 
DAY = 24 * HOUR # Seconds in a day.

config = None

class ReviewWdgt(ReviewWidget):
    def redraw_now(self):
        pass

def adjusted_now(now=None):
    global config

    if now == None:
        now = time.time()
    now -= int(config["day_starts_at"]) * HOUR 
    if time.daylight:
        now -= time.altzone
    else:
        now -= time.timezone
    return int(now)

def midnight_UTC(timestamp):        
    date_only = datetime.date.fromtimestamp(timestamp)
    return int(calendar.timegm(date_only.timetuple()))

def next_rep_to_interval(next_rep, now=None):
    if now is None:
        now = adjusted_now()
    return (next_rep - now) / DAY

def last_rep_to_interval(last_rep, now=None):
    global config

    if now is None:
        now = adjusted_now()
    now = midnight_UTC(now)
    last_rep = midnight_UTC(adjusted_now(now=last_rep))
    return (last_rep - now) / DAY

def show_info(ms):
    db = ms.database()
    print "database: %s" % db.path()

    print "data_dir: %s" % ms.config().data_dir

    counters = ms.review_controller().counters()
    print "scheduled: %d; not memorised: %d; active: %d" % counters

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

def show_card_stats(card, unseen_compat):
    stats = {}

    unseen = (card.grade == -1)
    if unseen_compat and unseen:
        card.grade = max(0, card.grade)
        card.acq_reps = max(0, card.acq_reps)
        card.acq_reps_since_lapse = max(0, card.acq_reps_since_lapse)
        card.last_rep = max(0, card.last_rep)
        card.next_rep = max(0, card.next_rep)

    for f in learning_data:
        if f == 'easiness':
            stats[f] = int(round(card.easiness * easiness_accuracy))
        elif f == 'unseen':
            stats[f] = int(unseen)
        elif f == 'last_rep' or f == 'next_rep':
            # Compatibility with Mnemosyne 1.x: last_rep/next_rep in days, not
            # seconds
            stats[f] = int(getattr(card, f) / DAY)
        else:
            stats[f] = int(getattr(card, f))

    for s in learning_data:
        fmt = "%%0%dx," % learning_data_len[s]
        print fmt % stats[s],
    print ("%s/%s (%s)" % (card.id, card._id, [t.name for t in card.tags][0]))

def show_card(card):
    print "id: %s (%s)" % (card.id, card._id)
    for attr in [
            "grade",
            "easiness",
            "acq_reps",
            "ret_reps",
            "lapses",
            "acq_reps_since_lapse",
            "ret_reps_since_lapse"
        ]:
        print "%s: %s" % (attr, getattr(card, attr))

    print "last_rep: %s (%d)" % (card.last_rep,
                                 last_rep_to_interval(card.last_rep))
    print "next_rep: %s (%d)" % (card.next_rep,
                                 next_rep_to_interval(card.next_rep))
    print "unseen: %d" % card.grade == -1
    print "tags: %s" % (", ". join(map(lambda t : "'%s'" % t.name, card.tags)))

def ignore_method(self, *args, **kwargs):
    pass

def main():
    global config

    print "Mnemoutil (%s)" % version

    # Parse options

    parser = OptionParser()
    parser.usage = "%prog [<database_file>]"
    parser.add_option("-d", "--datadir", dest="data_dir",
                      help="data directory", default=None)
    parser.add_option("-t", "--tags", dest="only_tags",
                      help="limit to given tags", default="")
    parser.add_option("-c", "--content", dest="show_content",
                      action="store_true", help="show card content")
    parser.add_option("-s", "--stats", dest="show_stats",
                      action="store_true", help="show stat lines")
    parser.add_option("-u", "--unseen", dest="unseen_compatability",
                      action="store_true", help="unseen stats as in 1.x")
    (options, args) = parser.parse_args()

    only_tags = set([s.strip() for s
                     in options.only_tags.split(',')
                     if s.strip()])
    if options.unseen_compatability: options.show_stats = True

    data_dir = None
    if options.data_dir != None:
        data_dir = os.path.abspath(options.data_dir)
    elif os.path.exists(os.path.join(os.getcwdu(), "mnemosyne")):
        data_dir = os.path.abspath(os.path.join(os.getcwdu(), "mnemosyne"))
            
    filename = None
    if len(args) > 0:
        filename = os.path.abspath(args[0])

    # Start a session

    ms = Mnemosyne(False, True)
    ms.activate_saved_plugins = types.MethodType(ignore_method, ms)

    ms.components.insert(0,
        ("mnemosyne.libmnemosyne.translators.no_translator", "NoTranslator"))

    for c in [
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"),
            (__name__, "ReviewWdgt")
        ]:
        ms.components.append(c)

    ms.initialise(data_dir, filename, automatic_upgrades=False)
    ms.review_controller().reset()

    db = ms.database()
    config = ms.config()

    if not options.show_stats:
        show_info(ms)

    cards = db.all_cards()
    count = 0
    for _card_id, _fact_id in cards:
        card = db.card(_card_id, is_id_internal=True)

        if (not only_tags
                or only_tags.intersection({ t.name for t in card.tags})):

            if options.show_stats:
                show_card_stats(card, options.unseen_compatability)
            else:
                print "--------------------%s (%s)" % (_card_id, _fact_id)
                show_card(card)

            if options.show_content:
                print "question:",
                print card.question(render_chain="default").replace("\n",
                            "\n|").encode('utf-8')
                print "answer:",
                print card.answer(render_chain="default").replace("\n",
                            "\n|").encode('utf-8')

            count += 1

    if not options.show_stats:
        print
        print "total: %d" % count

    #db.cards_due_for_ret_rep(adjusted_now())
    #db.cards_new_memorising(0)
    #db.cards_new_memorising(1)
    #db.cards_to_relearn(0):
    #db.cards_to_relearn(1):
    #db.cards_unseen():

    ms.finalise()


main()

