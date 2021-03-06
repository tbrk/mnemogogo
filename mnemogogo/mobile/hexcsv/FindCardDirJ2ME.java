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

import java.io.IOException;
import java.util.Enumeration;
import java.util.Vector;
import javax.microedition.io.Connector;
import javax.microedition.io.file.FileConnection;
import javax.microedition.io.file.FileSystemRegistry;

public class FindCardDirJ2ME
{
    public static final String[] standard = { "cards/" };
    public static Debug debug = null;

    private static void logInfo(String msg)
    {
        if (debug != null) {
            debug.logInfo(msg);
        }
    }

    private static void logInfo(String msg1, String msg2)
    {
        if (debug != null) {
            debug.logInfo(msg1 + msg2);
        }
    }

    private static void logInfo(String msg1, StringBuffer msg2)
    {
        if (debug != null) {
            debug.logInfo(msg1 + msg2.toString());
        }
    }

    private static boolean canWrite(FileConnection fconn)
    {
        boolean r = fconn.canWrite();
        logInfo("---canwrite=", r ? "true" : "false");
        return r;
    }

    public static boolean isCardDir(FileConnection fconn, Vector subdirs)
    {
        boolean hasStats = false;
        boolean hasCategories = false;
        boolean hasConfig = false;
        boolean hasCards = false;

        try {

            if (!fconn.exists())
            {
                logInfo("---does not exist");
                return false;
            }

            if (!fconn.isDirectory())
            {
                logInfo("---is not a directory");
                return false;
            }

            if (!fconn.canRead())
            {
                logInfo("---cannot read");
                return false;
            }

            Enumeration e = fconn.list();
            while (e.hasMoreElements()) {
                String f = (String)e.nextElement();

                if (f.equals("STATS.CSV")) {
                    logInfo("---found: STATS.CSV");
                    hasStats = true;

                } else if (f.equals("CATS")) {
                    logInfo("---found: CATS");
                    hasCategories = true;

                } else if (f.equals("CONFIG")) {
                    logInfo("---found: CONFIG");
                    hasConfig = true;

                } else if (f.equals("CARDS")) {
                    logInfo("---found: CARDS");
                    hasCards = true;
                }

                if ((subdirs != null) && (f.endsWith("/"))) {
                    subdirs.addElement(f);
                }
            }

        } catch (IOException e) {
            logInfo("---!isCardDir-conn:IOException:", e.toString());
            return false;
        } catch (SecurityException e) {
            logInfo("---!isCardDir-conn:SecurityException:", e.toString());
            return false;
        }

        return (hasStats
                && hasCategories
                && hasConfig
                && hasCards
                && canWrite(fconn));
    }

    public static boolean isCardDir(String path, Vector subdirs)
    {
        boolean r = false;

        try {
            FileConnection fconn =
                (FileConnection)Connector.open(path, Connector.READ);
            r = isCardDir(fconn, subdirs);
            fconn.close();
        } catch (IOException e) {
            logInfo("---!isCardDir-str:IOException:", e.toString());
        } catch (SecurityException e) {
            logInfo("---!isCardDir-str:SecurityException:", e.toString());
        }

        return r;
    }

    private static void doDir(FileConnection fconn,
                              StringBuffer pathbuf, Vector found)
    {
        logInfo("--doDir: ", pathbuf);
        try {
            if (isCardDir(fconn, null)) {
                logInfo("---found!");
                found.addElement(pathbuf.toString());
                fconn.close();

            } else {
                Enumeration e = fconn.list();
                fconn.close();
                fconn = null;
                int orig_len = pathbuf.length();

                while (e.hasMoreElements()) {
                    pathbuf.delete(orig_len, pathbuf.length());
                    pathbuf.append((String)e.nextElement());

                    FileConnection c =
                        (FileConnection)Connector.open(pathbuf.toString(),
                                                       Connector.READ);
                    if (c.isDirectory() && c.canRead()) {
                        doDir(c, pathbuf, found);
                    }
                }
            }
        } catch (IOException e) {
            logInfo("---!IOException:", e.toString());
        } catch (SecurityException e) {
            logInfo("---!SecurityException:", e.toString());
        }

        return;
    }

    public static String[] list()
    {
        Vector paths = new Vector();
        StringBuffer pathbuf = new StringBuffer("file://");

        logInfo("FindCardDirJ2ME.list: starting...");
        Enumeration roots = FileSystemRegistry.listRoots();
        while (roots.hasMoreElements()) {
            try {
                pathbuf.delete(7, pathbuf.length());
                pathbuf.append("/");
                pathbuf.append((String)roots.nextElement());

                FileConnection root =
                    (FileConnection)Connector.open(pathbuf.toString(),
                                                   Connector.READ);
                doDir(root, pathbuf, paths);
                root.close();
            } catch (IOException e) {
                logInfo("!list:IOException:", e.toString());
            } catch (SecurityException e) {
                logInfo("!list:SecurityException:", e.toString());
            }
        }

        if (paths.isEmpty()) {
            logInfo("FindCardDirJ2ME.list: done (none found).");
            return null;
        }

        String r[] = new String[paths.size()];
        paths.copyInto(r);

        logInfo("FindCardDirJ2ME.list: done (some found).");
        return r;
    }

    public static String[] checkStandard()
    {
        Vector paths = new Vector();
        StringBuffer pathbuf = new StringBuffer("file://");

        logInfo("FindCardDirJ2ME.checkStandard: starting...");
        Enumeration roots = FileSystemRegistry.listRoots();
        while (roots.hasMoreElements()) {
            try {
                pathbuf.delete(7, pathbuf.length());
                pathbuf.append("/");
                pathbuf.append((String)roots.nextElement());

                for (int i = 0; i < standard.length; ++i) {
                    int last = pathbuf.length();
                    pathbuf.append(standard[i]);

                    logInfo("--doDir: ", pathbuf);
                    if (isCardDir(pathbuf.toString(), null)) {
                        paths.addElement(pathbuf.toString());
                    }

                    pathbuf.delete(last, pathbuf.length());
                }

            } catch (SecurityException e) {
                logInfo("!checkStandard:SecurityException:", e.toString());
            }
        }

        if (paths.isEmpty()) {
            logInfo("FindCardDirJ2ME.checkStandard: done (none found).");
            return null;
        }

        String r[] = new String[paths.size()];
        paths.copyInto(r);

        logInfo("FindCardDirJ2ME.checkStandard: done (some found).");
        return r;
    }
}

