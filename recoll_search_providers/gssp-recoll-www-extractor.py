#!/usr/bin/python3
# -*- coding: utf-8 -*-



#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This script extracts Firefox WWW history from SQlite DB and presents it as documents for indexing
# Entries are given a separate mimetype (text/www-hist) for easy lookup


from __future__ import print_function

import sys
import glob
import os
import hashlib

import sqlite3

try:
    from recoll import recoll
except:
    import recoll


CONFIG_FILE = os.path.expanduser("~/.config/gssp-recoll.conf")
CONFIG_FILE_SYS = "/etc/gssp-recoll.conf"



def get_dbs():
    """ Get database list """
    mz_dir = os.path.expanduser("~/.mozilla/firefox")
    return glob.glob(f"{mz_dir}/*/places.sqlite")



def extract_docs():
    """ Extract history items from databases """
    entries = []
    dbs = get_dbs()
    for db in dbs:
        if not os.path.isfile(db): continue
        
        try:
            conn = sqlite3.connect(db)
            curs = conn.cursor()
        except (sqlite3.Error, sqlite3.OperationalError, OSError) as e: 
            print(f'Error connecting to {db}: {e}')
            continue
        
        try:
            results = curs.execute("""select url, title, description, preview_image_url, datetime(round(coalesce(last_visit_date,0)/1000000), 'unixepoch') from moz_places""").fetchall()
        except (sqlite3.Error, sqlite3.OperationalError, OSError) as e:
            print(e)
            continue

        for r in results: entries.append(r)

    return entries



def index_docs(rdb, entries:list):
    """ Index extracted entries """
    for e in entries:
        doc = recoll.Doc()
        doc.mimetype = 'text/www-history'

        url = str(e[0])
        title = str(e[1])
        desc = str(e[2])
        mtime = str(e[4])

        doc.title = title
        if len(url) > 240:
            text = desc
        else:
            text = f"""{title}
{desc}"""

        doc.text = text
        doc.url = url
        doc.mtime = mtime
        doc.date = mtime

        doc.dbytes = str(len(text.encode('UTF-8')))
        doc.fbytes = doc.dbytes

        doc.sig = f'{doc.mtime}:{doc.fbytes}'

        hsh = hashlib.sha1(url.encode())
        udi = hsh.hexdigest()

        rdb.addOrUpdate(udi, doc)
        



def purge_docs(rdb, entries:list):
    """ This one deletes all history entries (in case history item(s) gets deleted in browser """
    for e in entries:
        udi = str(e[0])
        hsh = hashlib.sha1(udi.encode())
        udi = hsh.hexdigest()
        if udi not in (None, ''): rdb.delete(udi)
            


def process():
    """ Main processing sequence """
    entries = extract_docs()

    if entries == []: return -2
    
    try: rdb = recoll.connect(writable=1)
    except Exception as e:
        print(f'Error connecting to Recoll DB: {e}')
        return -1

    purge_docs(rdb, entries)
    index_docs(rdb, entries)

    #rdb.purge()





err = process()
sys.exit(err)

