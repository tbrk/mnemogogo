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

import java.io.DataInputStream;
import java.io.OutputStream;
import java.io.InputStream;
import java.io.IOException;
import javax.microedition.io.Connector;
import javax.microedition.io.file.FileConnection; /*JSR-75*/

public class HexCsvJ2ME
    extends HexCsv
{
    public HexCsvJ2ME(String path, Progress prog)
        throws Exception, IOException
    {
        super(path, prog, true, false);
    }

    protected OutputStream openAppend(String path)
        throws IOException
    {
        FileConnection file =
            (FileConnection)Connector.open(path, Connector.READ_WRITE);
        if (!file.exists()) {
            file.create();
        }

        return file.openOutputStream(file.fileSize() + 1);
    }

    protected InputStream openIn(String path)
        throws IOException
    {
        return Connector.openInputStream(path);
    }

    protected OutputStream openOut(String path)
        throws IOException
    {
        return Connector.openOutputStream(path);
    }

    protected DataInputStream openDataIn(String path)
        throws IOException
    {
        return Connector.openDataInputStream(path);
    }
}

