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


if len(sys.argv) > 1: 

    arg = sys.argv[1]

    if arg == 'mail':
        search_mode = 1
        _myname = 'org.recoll.RecollMail.SearchProvider'

    elif arg == 'news': 
        search_mode = 2
        _myname = 'org.recoll.RecollNews.SearchProvider'

    elif arg == 'notes': 
        search_mode = 3
        _myname = 'org.recoll.RecollNotes.SearchProvider'

    elif arg == 'files': 
        search_mode = 4
        _myname = 'org.recoll.RecollFiles.SearchProvider'

    else:
        search_mode = 0
        _myname = 'org.recoll.Recoll.SearchProvider'


else: 
    search_mode = 0
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
            self.db = recoll.connect()
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

        if search_mode == 1: qr = qs + ' dir:~/Mail'
        elif search_mode == 2: qr = qs + ' dir:~/News'
        elif search_mode == 3: qr = qs + ' dir:~/Notes'
        elif search_mode == 4: qr = qs + ' -dir:~/Mail AND -dir:~/News AND -dir:~/Notes'
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
                    
                elif search_mode == 2: icon = Gio.ThemedIcon(name="application-rss+xml-symbolic")
                elif search_mode == 3: icon = Gio.ThemedIcon(name="gdnote")
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
                if os.path.isfile('/usr/local/bin/mcopen'):
                    debug("GSSPRecoll:ActivateResult: Exec mcopen on %s" % doc.url)
                    proc = subprocess.Popen(['mcopen', '-no-terminal','--', str(doc.url)])
                    #os.system("mcopen -no-terminal -- '%s'" % str(doc.url))
                else:
                    debug("GSSPRecoll:ActivateResult: Exec xdg-open on %s" % doc.url)
                    proc = subprocess.Popen(['xdg-open', str(doc.url)])
                    #os.system("xdg-open '%s'" % str(doc.url))

    def LaunchSearch(self, terms, ts):
        debug("GSSPRecoll:LaunchSearch: terms [%s]" % terms)
        qs = ""
        for term in terms:
            qs += " " + term
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
