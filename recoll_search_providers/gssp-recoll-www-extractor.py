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
import stat 

import hashlib

import sqlite3

try:
    from recoll import recoll
except:
    import recoll


CONFIG_FILE = os.path.expanduser("~/.config/gssp-recoll.conf")
CONFIG_FILE_SYS = "/etc/gssp-recoll.conf"
WWW_DB = os.path.expanduser("~/.recoll_xap_www") # Add this as an external index to Recoll


def get_dbs():
    """ Get database list """
    # Get Firefox Places DB list
    mz_dir = os.path.expanduser("~/.mozilla/firefox")
    #return (os.path.expanduser("~/places.sqlite"),)
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

        hashes = []
        for r in results:
            rr = list(r)
            h = hashlib.sha1(r[0].encode())
            hh = h.hexdigest()
            rr.append(hh)
            hashes.append(hh)
            entries.append(rr)

    return entries, hashes



def index_docs(rdb, entries:list):
    """ Index extracted entries """
    # Touch dummy file
    for e in entries:
        doc = recoll.Doc()
        doc.mimetype = 'text/www-history'

        url = str(e[0])
        title = str(e[1])
        desc = str(e[2])
        date = str(e[4])

        doc.title = title
        if len(url) > 240: text = desc
        else: text = f"""{title}
{desc}"""

        doc.text = text
        doc.url = url
        doc.date = date
        doc.mtime = date
        doc.rclbes = 'WWW'
        doc.dbytes = str(len(text.encode('UTF-8')))
        doc.sig = f'{date}:{doc.dbytes}'

        udi = str(e[5])

        rdb.addOrUpdate(udi, doc)
        



def purge_docs(rdb, hashes):
    """ This one deletes all history entries (in case history item(s) gets deleted in browser )"""
    q = rdb.query()
    q.execute('mimetype:text/www-history') # This mimetype should be exclusive for history entries 

    if q.rowcount == 0: return 0
    for e in q:
        udi = e.udi
        if udi not in (None, '') and udi not in hashes: 
            rdb.delete(udi)
            


def process():
    """ Main processing sequence """
    entries, hashes = extract_docs()

    if entries == []: return -2

    if not os.path.isdir(WWW_DB): os.mkdir(WWW_DB)    

    try: rdb = recoll.connect(confdir=WWW_DB, writable=1)
    except Exception as e:
        print(f'Error connecting to Recoll DB: {e}')
        return -1

    purge_docs(rdb, hashes)
    index_docs(rdb, entries)
    return 0





err = process()
sys.exit(err)

