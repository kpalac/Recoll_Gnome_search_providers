#!/usr/bin/python3
# Copyright (C) 2017-2019 J.F.Dockes
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation; either version 2.1 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


# https://developer.gnome.org/shell/stable/gdbus-org.gnome.Shell.SearchProvider2.html

import sys
import subprocess
import os

from gi.repository import GLib
from gi.repository import Gio
from pydbus.generic import signal
from pydbus import SessionBus


from recoll import recoll



# Read Configuration
CONFIG_FILE=f'{os.environ["HOME"]}/.config/gssp-recoll.conf'
CONFIG_FILE_SYS=f'/etc/gssp-recoll.conf'

mail_dir = ''
www_dir = ''
www_db = ''
open_command = ''
excluded_dirs = []

if os.path.isfile(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r') as f: config = f.readlines()
    except OSError as e: config = ('',)
elif os.path.isfile(CONFIG_FILE_SYS):
    try:
        with open(CONFIG_FILE_SYS, 'r') as f: config = f.readlines() 
    except OSError as e: config = ('',)
    
else: config = ('',)



# Parse config srings
for line in config:
    line = line.strip()
    if line.startswith('#'): continue
    if line.startswith('mail_dir='): mail_dir = line.split('=')[1].lstrip()
    if line.startswith('www_dir='): www_dir = line.split('=')[1].lstrip()
    if line.startswith('www_db='): www_db = line.split('=')[1].lstrip()
    if line.startswith('open_command='): open_command = line.split('=')[1].lstrip()
    if line.startswith('excluded_dirs='):
        excl_line = line.split('=',1)[1]
        for ed in excl_line.split('///'):
            ed = ed.lstrip()
            excluded_dirs.append(ed)

# Sanitize configuration parameters
if not os.path.isdir(os.path.expanduser(mail_dir)): mail_dir = ''
if not os.path.isdir(os.path.expanduser(www_dir)): www_dir = ''
if not os.path.isdir(os.path.expanduser(www_db)): www_db = ''
if open_command == '': open_command = 'xdg-open %f'

excluded_dirs_str = ''
for s in excluded_dirs:
    s = s.replace('"','\"')
    excluded_dirs_str = f'{excluded_dirs_str} AND -dir:"{s}"'

mail_dir = mail_dir.replace('"','\"')
www_dir = www_dir.replace('"','\"')

excl_dirs_f = ''
if mail_dir != '': excl_dirs_f = f'{excl_dirs_f} AND -dir:"{mail_dir}"'
if www_dir != '': excl_dirs_f = f'{excl_dirs_f} AND -dir:"{www_dir}"'




# Setup query strings according to command-line parameters
if len(sys.argv) > 1: 

    arg = sys.argv[1]
    
    if arg == 'other':
        search_mode = 0
        _myname = 'org.recoll.RecollOther.SearchProvider'
        search_str = f'({excl_dirs_f} AND -rclcat:book AND -rclcat:media AND -rclcat:docs AND -rclcat:code AND -rclcat:table AND -rclcat:image AND -rclcat:message AND -rclcat:www)'

    elif arg == 'mail':
        search_mode = 1
        _myname = 'org.recoll.RecollMail.SearchProvider'
        if mail_dir == '': search_str = f'rclcat:message{excluded_dirs_str}'
        else: search_str = f'dir:"{mail_dir}"{excluded_dirs_str}'

    elif arg == 'www':
        search_mode = 11
        _myname = 'org.recoll.RecollWWW.SearchProvider'
        if www_dir == '': search_str = f'rclcat:www{excluded_dirs_str}'
        else: search_str = f'dir:"{www_dir}"{excluded_dirs_str}'


    elif arg == 'docs': 
        search_mode = 2
        _myname = 'org.recoll.RecollDocs.SearchProvider'
        search_str = f'{excl_dirs_f} AND rclcat:docs{excluded_dirs_str}'

    elif arg == 'media': 
        search_mode = 3
        _myname = 'org.recoll.RecollMedia.SearchProvider'
        search_str = f'{excl_dirs_f} AND rclcat:media{excluded_dirs_str}'

    elif arg == 'books':
        search_mode = 4
        _myname = 'org.recoll.RecollBooks.SearchProvider'
        search_str = f'{excl_dirs_f} AND rclcat:book{excluded_dirs_str}'

    elif arg == 'code': 
        search_mode = 5
        _myname = 'org.recoll.RecollCode.SearchProvider'
        search_str = f'{excl_dirs_f} AND rclcat:code{excluded_dirs_str}'

    elif arg == 'data': 
        search_mode = 5
        _myname = 'org.recoll.RecollData.SearchProvider'
        search_str = f'{excl_dirs_f} AND rclcat:table{excluded_dirs_str}'

    elif arg == 'images': 
        search_mode = 5
        _myname = 'org.recoll.RecollImages.SearchProvider'
        search_str = f'{excl_dirs_f} AND rclcat:image{excluded_dirs_str}'

    else:
        search_mode = 0
        search_str = ''
        _myname = 'org.recoll.Recoll.SearchProvider'


else: 
    search_mode = 0
    search_str = ''
    _myname = 'org.recoll.Recoll.SearchProvider'


_defxmlfile = '/usr/share/dbus-1/interfaces/org.gnome.ShellSearchProvider2.xml'

def debug(s):
    print("%s"%s, file=sys.stderr)

# debug("GSSPRecoll:recoll-search.py LOADED")

class RecollSearchProvider(object):
    def __init__(self):
        self.results = []
        self.proc = None
        self.db = None
        try:
            if search_mode == 11 and www_db != '': 
                self.db = recoll.connect(confdir=os.path.expanduser(www_db))
            else: self.db = recoll.connect()
        except:
            pass
            
    def GetInitialResultSet(self, terms):
        debug("GSSPRecoll:GetInitialResultSet: terms: %s" % terms)
        qs = ""
        for term in terms:
            if qs:
                qs += " "
            qs += term
        if len(qs) < 2:
            return []
        if not self.db:
            # No index yet
            try:
                self.db = recoll.connect()
            except:
                return []

        if search_str != '': qr = qs + ' ' + search_str
        else: qr = qs

        q = self.db.query()
        q.execute(qr)
        self.results = {}
        outlist = []
        if q.rowcount == 0:
            # There is a bug in the current module (1.25.4), and the 'for' line will throw if the
            # result set is empty. For now:
            return outlist
        for doc in q:
            doc.abstract = q.makedocabstract(doc)
            if doc.abstract is None:
                doc.abstract = ''
            key = str(doc.xdocid)
            self.results[key] = doc
            outlist.append(key)
            if len(outlist) >= 10:
                break
        debug("GSSPRecoll:GetInitialResultSet: %d results: %s" % (len(outlist),outlist))
        return outlist
    
    def GetSubsearchResultSet(self, prevres, terms):
        # As far as I can see, terms includes the terms from the original query, so we can just run
        # the initial search again. Not sure that we can do anything better
        #debug("GSSPRecoll:GetSubsearchResultSet: prevres: %s terms: %s" % (prevres,terms))
        return self.GetInitialResultSet(terms)

    def GetResultMetas(self, idents):
        #debug("GSSPRecoll:GetResultMetas: idents %s " % idents)
        out = []
        for key in idents:
            if key in self.results:
                doc = self.results[key]
                entry = {}
                entry['id'] = GLib.Variant('s', key)
                # "name": the display name for the result
                #if search_mode == 1: name = doc.author + ': ' + doc.title
                #else: 
                name = doc.title if doc.title else doc.filename
                if not name:
                    name = "No title or file name?"
                entry['name'] = GLib.Variant('s', name)
                # "icon": a serialized GIcon (see g_icon_serialize()), or alternatively, "gicon": a
                # textual representation of a GIcon (see g_icon_to_string()), or alternativly,
                # "icon-data": a tuple of type (iiibiiay) describing a pixbuf with width, height,
                # rowstride, has-alpha, bits-per-sample, and image data
                if search_mode == 1:
                    mt = doc.mimetype
                    if mt.startswith('message/'): 
                        icon = Gio.ThemedIcon(name="applications-internet-mail")
                    else:
                        ct = Gio.content_type_from_mime_type(mt)
                        icon = Gio.content_type_get_icon(ct)
                
                elif search_mode == 11:
                    mt = 'text/html'
                    icon = Gio.ThemedIcon(name="www-symbolic")

                else:
                    mt = doc.mimetype
                    ct = Gio.content_type_from_mime_type(mt)
                    icon = Gio.content_type_get_icon(ct)
                entry['icon'] = icon.serialize()
                # "description": an optional short description (1-2 lines)
                entry['description'] = GLib.Variant('s', doc.abstract)
                out.append(entry)
            else:
                debug("GSSPRecoll: GetResultMetas: %s not found" % key)
                out.append({'name':'empty', 'icon':None, 'description':'empty'})
        #debug("GSSPRecoll:GetResultMetas: return %s" % out)
        return out



    def ActivateResult(self, ident, terms, ts):
        debug("GSSPRecoll:ActivateResult: id %s terms %s"%(ident, terms))
        if ident in self.results:
            doc = self.results[ident]
            if doc.ipath:
                debug("GSSPRecoll:ActivateResult: ipath[%s]" % doc.ipath)
                url = doc.url + "#" + doc.ipath
                proc = subprocess.Popen(["recoll", url])
            else:
                comm_lst = open_command.split(' ')
                if '%f' not in comm_lst or '%F' not in comm_lst or '%u' not in comm_lst or '%F' not in comm_lst: comm_lst.append('%f')
                for i,c in enumerate(comm_lst):
                    if c in ('%f','%F','%u','%U'): comm_lst[i] = str(doc.url)

                debug("GSSPRecoll:ActivateResult: Exec " + ' '.join(comm_lst) + " on %s" % doc.url)
                proc = subprocess.Popen(comm_lst)



    def LaunchSearch(self, terms, ts):
        debug("GSSPRecoll:LaunchSearch: terms [%s]" % terms)
        qs = ""
        for term in terms:
            qs += " " + term
        if search_str != '': qs = qs + ' ' + search_str
        proc = subprocess.Popen(["recoll", "-q", qs])

    def XUbuntuCancel(self):
        # This interface is not documented in the SearchProvider2 document (URL above).
        #
        # After experimenting, and as far as I can see, if the search is slow (ex: left-hand
        # wildcard), and Esc is typed while the desktop is displaying "Searching", the desktop
        # interface gets out of search mode, and XUbuntuCancel() is called after the search is
        # actually done (after the GSSPRecoll:GetInitialResultSet: x results: line is
        # printed). Meaning, that, for this to make sense, the search should actually be
        # asynchronous internally, but the GetInitialResultSet() call is synchronous, so this makes
        # no sense. The concurrency model is not explained in the doc. The lengthy part of a
        # Xapian search is not cancellable anyway, so there is not much we could do (except
        # exiting/killing the process maybe ? Would this is result in a clean restart later on ?).
        debug("GSSPRecoll:XUbuntuCancel")
        pass


_defxml = open(_defxmlfile, 'r').read()
RecollSearchProvider.dbus = _defxml

mainloop = GLib.MainLoop()

session_bus = SessionBus()

session_bus.publish(_myname, RecollSearchProvider())

mainloop.run()
