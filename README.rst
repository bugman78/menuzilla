menuzilla
=========

menuzilla is a python script that allows you to export your bookmarks from the
firefox toolbar as shortcuts in your Desktop folder or as menu entries.

----

menuzilla is consistent with the freedesktop.org_ specifications, so it is
supposed to work with recent versions of all consistent desktop environments
such as Xfce, KDE and Gnome.

When installing firefox bookmarks as desktop menu entries, they are available
in a 'Mozbookmarks' directory. On the other side, when installing them in your
Desktop folder, they should appear in $HOME/Desktop (or the translated version
of that directory, as returned by ``xdg-user-dir DESKTOP``).  

.. _freedesktop.org: https://www.freedesktop.org/wiki/

Examples of use
---------------

.. code-block:: console

    $ menuzilla install menu

will extract toolbar bookmarks characteristics from you firefox default
profile, create corresponding `.desktop` entries (each of them refering to a
bookmark URL), and install them using the ``xdg-desktop-menu`` command line
tool.

.. code-block:: console

    $ menuzilla install desktop

will also extract toolbar bookmarks characteristics from your firefox default
profile, create correspond `.desktop` entries, and install them in your
``$HOME/Desktop`` directory.

For full documentation, use ``menuzilla --help``.

How it works
------------

menuzilla is a good example of use of many modules from the python standard
library: `argparse`, `ConfigParser`, `glob`, `logging`, `sqlite3`,
`urllib2`, and so on.

`ConfigParser` allows to parse the ``profiles.ini`` file in the
``$HOME/.mozilla/firefox`` directory.  `sqlite3` is used to load and analyse
the ``places.sqlite`` database located in the default mozilla profile, and get
the toolbar bookmarks informations. Favicons of these bookmarks are also
retrieved from their URLs using `urllib2`.

Requirements
------------

``xdg-utils`` package has to be installed as it is used to register menu
entries


