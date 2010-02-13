/*
 * Copyright (C) 2009 Timothy Bourke
 * 
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 2 of the License, or (at your option)
 * any later version.
 * 
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc., 59
 * Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */

package mnemogogo.mobile.hexcsv;

import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.DataInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.util.Date;
import java.util.Calendar;
import java.util.TimeZone;

abstract class HexCsv
    implements CardList, CardDataSet
{
    private Card cards[];
    private RevQueue q;
    private int days_left;
    private Config config;
    private Progress progress;

    public long days_since_start;
    public OutputStreamWriter logfile;
    public String categories[];

    public int cards_to_load = 50;

    public static final String ascii = "US-ASCII";
    public static final String utf8 = "UTF-8";

    public static final String readingStatsText = "Loading statistics";
    public static final String writingStatsText = "Writing statistics";
    public static final String loadingCardsText = "Loading cards";

    private StringBuffer pathbuf;
    private int path_len;

    public HexCsv(String path, Progress prog)
        throws Exception, IOException
    {
        path_len = path.length();
        pathbuf = new StringBuffer(path_len + 20);
        pathbuf.append(path);

        progress = prog;

        readConfig(pathbuf);

        days_left = daysLeft(config.lastDay());
        days_since_start = daysSinceStart(config.startDay());

        truncatePathBuf();
        readCards(pathbuf);

        truncatePathBuf();
        readCategories(pathbuf);

        if (config.logging()) {
            truncatePathBuf();
            pathbuf.append("PRELOG");

            try {
                OutputStream outs = openAppend(pathbuf.toString());
                try {
                    logfile = new OutputStreamWriter(outs, ascii);
                } catch (UnsupportedEncodingException e) {
                    logfile = new OutputStreamWriter(outs);
                }
            } catch (Exception e) {
                logfile = null;
            }
        }
    }

    void truncatePathBuf()
    {
        pathbuf.delete(path_len, pathbuf.length());
    }

    public String getCategory(int n) {
        if (0 <= n && n < categories.length) {
            return categories[n];
        } else {
            return null;
        }
    }

    public Card getCard() {
        return q.getCard();
    }

    public Card getCard(int serial) {
        if (0 <= serial && serial < cards.length) {
            return cards[serial];
        } else {
            return null;
        }
    }

    private void readConfig(StringBuffer path)
        throws IOException
    {
        InputStreamReader in;

        try {
            in = new InputStreamReader(openIn(path.append("CONFIG").toString(), ascii));
        } catch (UnsupportedEncodingException e) {
            in = new InputStreamReader(openIn(path.append("CONFIG").toString()));
        }

        config = new Config(in);
        in.close();
    }

    private long nowInDays()
    {
        Date now = new Date(); // UTC (millisecs since 01/01/1970, 00:00:00 GMT)

        // hours since epoch in UTC
        long hours = now.getTime() / 3600000;

        // offset from UTC to local in hours
        Calendar cal = Calendar.getInstance();
        TimeZone tz = cal.getTimeZone();
        long tzoff = tz.getRawOffset() / 3600000;

        // e.g.
        // for day_starts_at = 3 (0300 local time)
        // and UTC +8
        // the next day should start at UTC 1900
        // (not at UTC 0000)
        // because 1900 + 8 - 3 = 0000

        return (hours + tzoff - config.dayStartsAt()) / 24;
    }

    private long daysSinceStart(long start_days)
    {
        long now_days = nowInDays();
        return now_days - start_days;
    }

    public int daysLeft() {
        return days_left;
    }

    private int daysLeft(long last_day)
    {
        return (int)(last_day - nowInDays());
    }

    private void readCards(StringBuffer path)
        throws IOException
    {
        InputStreamReader in;

        try {
            in = new InputStreamReader(openIn(path.append("STATS.CSV").toString(), ascii));
        } catch (UnsupportedEncodingException e) {
            in = new InputStreamReader(openIn(path.append("STATS.CSV").toString()));
        }

        int ncards = StatIO.readInt(in);
        progress.startOperation(ncards * 3, readingStatsText);

        cards = new Card[ncards];
        Card.cardlookup = this;

        for (int i=0; i < ncards; ++i) {
            cards[i] = new Card(in, i);
            if (i % 10 == 0) {
                progress.updateOperation(10);
            }
        }
        progress.stopOperation();

        in.close();

        q = new RevQueue(ncards, days_since_start, config, progress, days_left);
        q.buildRevisionQueue(cards);
    }

    public void writeCards(StringBuffer path, String name, Progress progress)
        throws IOException
    {
        OutputStreamWriter out;

        try {
            out = new OutputStreamWriter(openOut(path.append(name).toString(), ascii));
        } catch (UnsupportedEncodingException e) {
            out = new OutputStreamWriter(openOut(path.append(name).toString()));
        }

        StatIO.writeInt(out, cards.length, "\n");

        if (progress != null) {
            progress.startOperation(cards.length, writingStatsText);
        }
        for (int i=0; i < cards.length; ++i) {
            cards[i].writeCard(out);

            if (i % 10 == 0 && progress != null) {
                progress.updateOperation(10);
            }
        }
        if (progress != null) {
            progress.stopOperation();
        }

        out.flush();
        out.close();
    }

    public void writeCards(StringBuffer path, Progress progress)
        throws IOException
    {
        writeCards(path, "STATS.CSV", progress);
    }

    public void backupCards(StringBuffer path, Progress progress)
        throws IOException
    {
        writeCards(path, "STATS.BKP", progress);
    }

    private void readCategories(StringBuffer path)
        throws IOException
    {
        InputStreamReader in;

        try {
            in = new InputStreamReader(openIn(path.append("CATS").toString(), utf8));
        } catch (UnsupportedEncodingException e) {
            in = new InputStreamReader(openIn(path.append("CATS").toString()));
        }

        int n = StatIO.readInt(in);
        StatIO.readInt(in); // skip the size in bytes

        categories = new String[n];
        for (int i=0; i < n; ++i) {
            categories[i] = StatIO.readLine(in);
        }

        in.close();
    }

    public void setCardData(int serial, String question, String answer,
                boolean overlay)
    {
        cards[serial].setOverlay(overlay);
        cards[serial].setQuestion(question);
        cards[serial].setAnswer(answer);
    }

    public boolean cardDataNeeded(int serial)
    {
        return ((cards[serial].isDueForRetentionRep(days_since_start)
                            || cards[serial].isDueForAcquisitionRep())
                && q.isScheduledSoon(serial, cards_to_load));
    }

    public void setProgress(Progress new_progress) {
        progress = new_progress;
    }

    private void readCardText(StringBuffer path)
        throws IOException
    {
        DataInputStream is = openDataIn(path.append("CARDS").toString());

        // the new object is not needed, rather just that its constructor
        // updates this object.
        new CardData(is, progress, this);
        is.close();
    }

    public void loadCardData()
        throws IOException
    {
        // clear any existing questions and answers
        for (int i=0; i < cards.length; ++i) {
            cards[i].setQuestion(null);
            cards[i].setAnswer(null);
        }

        // load them again
        truncatePathBuf();
        progress.startOperation(cards.length, loadingCardsText);
        readCardText(pathbuf);
        progress.stopOperation();
    }

    public int numScheduled() {
        return q.numScheduled();
    }

    public void updateFutureSchedule(Card card) {
        q.updateFutureSchedule(card);
    }

    public int[] getFutureSchedule() {
        return q.futureSchedule;
    }

    public String toString() {
        return q.toString();
    }

    public void dumpCards() {
        System.out.println("----Cards:");
        for (int i=0; i < cards.length; ++i) {
            System.out.print("  ");
            System.out.println(cards[i].toString());
        }
    }

    public void close() {
        if (logfile != null) {
            try {
                logfile.close();
            } catch (IOException e) { }
            logfile = null;
        }
    }

    abstract protected OutputStream openAppend(String path)
        throws IOException;
    abstract protected OutputStream openOut(String path)
        throws IOException;
    abstract protected InputStream openIn(String path)
        throws IOException;
    abstract protected DataInputStream openDataIn(String path)
        throws IOException;
}

