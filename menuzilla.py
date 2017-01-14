#!/usr/bin/python
# coding: utf-8

import argparse
from ConfigParser import ConfigParser
from glob import glob
import logging as log
import os
import sqlite3
from subprocess import call, check_output
from urllib2 import urlopen
from urlparse import urlparse

from xdg import BaseDirectory


"""menuzilla is a python script that allows you to export your
bookmarks from the firefox toolbar as shortcuts in your Desktop folder
or as menu entries.

menuzilla follows the freedesktop.org requirements.
"""

__author__ = "Stephane Bugat"
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Stephane Bugat"
__email__ = "stephane.bugat@free.fr"
__status__ = "Beta"


menuzilla_desc = """menuzilla is a python script that allows you to 'export'
you bookmarks from the firefox toolbar as entries in your desktop menu,
or in your Desktop folder.

menuzilla is consistent with the freedesktop.org specifications, so it is
supposed to work with recent versions of all Linux desktop environments such
as Xfce, KDE and Gnome.

When installing firefox bookmarks as desktop menu entries, they are available
in a 'Mozbookmarks' directory. On the other side, when installing them in
your Desktop folder, they should appear in $HOME/Desktop (or the translated
version of that directory, as returned by `xdg-user-dir DESKTOP`).
"""

# this request selects only bookmarks located in the toolbar
request = """SELECT mp.id, mp.url, mb.title, mf.url
    FROM moz_places AS mp
    JOIN moz_bookmarks AS mb
    ON mp.id = mb.fk
    JOIN moz_bookmarks_roots AS mbr
    ON mbr.folder_id = mb.parent
    JOIN moz_favicons AS mf
    ON mp.favicon_id = mf.id
    WHERE mbr.root_name = 'toolbar'
"""


desktop_tmpl = u"""[Desktop Entry]
Version=1.0
Type=Link
Name={name}
Comment={comment}
URL={url}
Icon={icon_name}
Categories=Mozbookmarks;
Keywords=Mozbookmarks;
Terminal=false
StartupNotify=false
"""

directory_tmpl = u"""[Desktop Entry]
Version=1.0
Type=Directory
Name=Mozbookmarks
Comment=Created by menuzilla
Icon=user-bookmarks
"""


class Mozbookmarks(object):
    _mozdir = os.path.join(os.getenv('HOME'), '.mozilla', 'firefox')
    _mozprofile = os.path.join(_mozdir, 'profiles.ini')
    _cache_dir = BaseDirectory.save_cache_path('menuzilla')
    _icon_dir = os.path.join(_cache_dir, 'icons')
    _desktop_dir = check_output(['xdg-user-dir', 'DESKTOP']).strip()
    _directory = os.path.join(_cache_dir, 'menuzilla-dir.directory')

    def __init__(self):
        self.bookmarks = []
        self.entries = []
        self.icons = []
        if not os.path.exists(self._icon_dir):
            log.debug("Icon cache directory does not exist. Creating it.")
            os.makedirs(self._icon_dir)

    def get_bookmarks(self):
        config = ConfigParser()
        config.readfp(open(self._mozprofile))
        log.debug("Successfully read mozilla profile.")
        bookmark_db = sqlite3.connect(os.path.join(
            self._mozdir,
            config.get('Profile0', 'Path'),
            'places.sqlite'
        ))
        log.debug("Successfully opened bookmarks database.")
        data = bookmark_db.execute(request)
        for this_bookmark in data:
            this_dict = {
                'id': unicode(this_bookmark[0]),
                'url': unicode(this_bookmark[1]),
                'name': unicode(this_bookmark[2]),
                'icon_url': unicode(this_bookmark[3]),
                'icon_name': u'user-bookmarks',
                'comment': unicode(this_bookmark[1][:255]),
            }
            self.bookmarks.append(this_dict)
        log.info("Mozilla bookmarks grabed.")

    def treat_favicon(self, bookmark):
        icon_url = bookmark['icon_url']
        path = urlparse(icon_url).path
        icon_ext = os.path.splitext(os.path.basename(path))[1]
        if icon_ext not in ('.png', '.xpm'):
            log.warn('Favicon {} not in a recognised format for icons'.format(
                icon_url))
            return None
        icon_file = "menuzilla-bookmark{}{}".format(bookmark['id'], icon_ext)
        try:
            data = urlopen(icon_url).read()
            fullname = os.path.join(self._icon_dir, icon_file)
            with open(fullname, 'wb') as iconfile:
                iconfile.write(data)
            log.debug('Successfully created {} icon file'.format(icon_file))
            return icon_file
        except:
            log.warn('Unable to create icon file from {}'.format(icon_url))
            return None

    def write_entries(self):
        self.entries = []
        self.icons = []
        # first write the directory desktop file
        with open(self._directory, 'w') as xdir:
            xdir.write(directory_tmpl)
        #self.entries.append(directory)
        if not self.bookmarks:
            self.get_bookmarks()
        for bookmark in self.bookmarks:
            ret = self.treat_favicon(bookmark)
            if ret:
                bookmark['icon_name'] = 'menuzilla-bookmark{}'.format(
                    bookmark['id'])
                self.icons.append(ret)
            entry_name = 'menuzilla-bookmark{}.desktop'.format(
                bookmark['id'])
            fullname = os.path.join(self._cache_dir, entry_name)
            with open(fullname, 'w') as df:
                content = desktop_tmpl.format(**bookmark)
                df.write(content.encode('utf8'))
            self.entries.append(fullname)

    def register_entries(self, target='menu'):
        if not self.entries:
            return
        if target not in ('desktop', 'menu'):
            raise KeyError
        if target == 'desktop':
            # put .desktop files in $HOME/Desktop or equivalent
            for entry in self.entries:
                args = ['install', '-m', 'u=rwx', entry, self._desktop_dir]
                call(args)
        elif target == 'menu':
            args = ['xdg-desktop-menu', 'install', self._directory]
            args += self.entries
            call(args)
        # then install also icon files
        for icon in self.icons:
            args = ['xdg-icon-resource', 'install', '--size', '16',
                    os.path.join(self._icon_dir, icon)]
            call(args)

    def unregister_entries(self, target='menu'):
        directory = glob(os.path.join(self._cache_dir, '*.directory'))
        entries = glob(os.path.join(self._cache_dir, '*.desktop'))
        icons = glob(os.path.join(self._icon_dir, '*.*'))
        if not entries:
            return
        if target=='menu':
            # calling the uninstall action of xdg-desktop-menu
            args = ['xdg-desktop-menu', 'uninstall'] + directory + entries
            call(args)
            log.debug('Unregistering directory desktop file {}'.format(
                directory))
        elif target=='desktop':
            # simply removes all desktop files
            for entry in glob(os.path.join(self._desktop_dir,
                                           'menuzilla-*.desktop')):
                log.debug('Removing entry {}'.format(entry))
                os.remove(entry)
        for icon in icons:
            # In all cases: uninstall icon files
            args = ['xdg-icon-resource', 'uninstall', '--size', '16', icon]
            log.debug('Unregistering icon file {}'.format(icon))
            call(args)
        log.info('{} entries unregistered'.format(target))

    def clear_cache(self):
        log.debug('Clearing the cache...')
        directory = glob(os.path.join(self._cache_dir, 'menuzilla-*.directory'))
        entries = glob(os.path.join(self._cache_dir, 'menuzilla-*.desktop'))
        icons = glob(os.path.join(self._icon_dir, 'menuzilla-*.*'))
        for desktop_file in directory+entries+icons:
            os.remove(desktop_file)
        log.debug('{} desktop files removed.'.format(len(entries)))
        log.debug('{} icon files removed.'.format(len(icons)))
        log.debug('Cache cleared.')

    def install(self, target='menu'):
        """(re-)installs everything. If some previous desktop files where
        installed, unregisters them and cleans the cache."""
        self.clean(target=target)
        self.update(target=target)

    def update(self, target='menu'):
        """installs everything without previous cleaning, so that registered
        desktop files are overriden or left."""
        self.write_entries()
        self.register_entries(target=target)

    def uninstall(self, target='menu'):
        """uninstalls the desktop files"""
        log.debug('Unregistering {} entries'.format(target))
        self.unregister_entries(target=target)

    def clean(self, target='menu'):
        """unregisters any desktop files and cleans the cache"""
        self.uninstall(target=target)
        self.clear_cache()
        log.info('Cleaning performed')



# ------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=menuzilla_desc)
    parser.add_argument('action',
                        help='one of "install", "update", "uninstall", "clean"',
                        type=str)
    parser.add_argument('target',
                        help='one of "menu", "desktop"',
                        type=str)
    parser.add_argument('-v', '--verbosity',
                        help='set verbosity level (default="info")',
                        action="store")
    args = parser.parse_args()
    if args.verbosity:
        log.basicConfig(level=getattr(log, args.verbosity.upper()))
    if args.action not in ('install', 'update', 'uninstall', 'clean'):
        raise KeyError, args.action
    if args.target not in ('menu', 'desktop'):
        raise KeyError, args.target
    bookmarks = Mozbookmarks()
    getattr(bookmarks, args.action).__call__(target=args.target)

# EOF
