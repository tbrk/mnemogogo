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

def show_card(card, show_content=False):
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
    print "unseen: %d" % (card.active == 1 and card.grade == -1)
    print "tags: %s" % (", ". join(map(lambda t : "'%s'" % t.name, card.tags)))

    if show_content:
        print "question:",
        print card.question(render_chain="default").replace("\n", "\n|") \
                .encode('utf-8')
        print "answer:",
        print card.answer(render_chain="default").replace("\n", "\n|") \
                .encode('utf-8')

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
    (options, args) = parser.parse_args()

    only_tags = set([s.strip() for s in options.only_tags.split(',')])

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

    ms.initialise(data_dir, filename)
    ms.review_controller().reset()

    db = ms.database()
    config = ms.config()

    show_info(ms)

    print "cards due for ret rep:"
    for _card_id, _fact_id in db.cards_due_for_ret_rep(adjusted_now()):
        card = db.card(_card_id, is_id_internal=True)

        if (only_tags is None
                or only_tags.intersection({ t.name for t in card.tags})):
            print "--------------------%s (%s)" % (_card_id, _fact_id)
            show_card(card, show_content=True)

    #db.cards_new_memorising(0)
    #db.cards_new_memorising(1)
    #db.cards_to_relearn(0):
    #db.cards_to_relearn(1):
    #db.cards_unseen():

    ms.finalise()


main()

