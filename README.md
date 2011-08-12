# Trac Mercurial Changeset Plugin

Trac plugin that inserts Mercurial repository information into Trac's database, thus integrating Mercurial and Trac to a fuller extend than the default Trac support. It enables ticket search, ticket changelogs, etc. 100% compatible with TracMercurial plugin. It actually solves TracMercurial <a href="http://trac.edgewall.org/ticket/8417">issue #8417</a>. TracMercurial is using this code to solve the issue, till they integrate it, you can use this.

## Prerequisites

 * Mercurial
 * Trac (tested on v0.12, might work on others)

## Installation

You can install this software as a normal Trac plugin.

1. First uninstall former MercurialChangesetPlugin version, if you have installed it before.
2. Change directory to Trac's plugin's directory containing ``setup.py``.
3. Clone this repository:

<code>
git clone git://github.com/maraujop/TracMercurialChangesetPlugin.git
</code>

4. Install it:

<code>
python setup.py install
</code>

5. If you want to install this plugin to your trac instance only, create the egg from the repo running:

<code>
python setup.py bdist_egg
</code>

Then, copy the generated egg file to the trac instance's plugin directory:

<code>
cp dist/*.egg /srv/trac/env/plugins
</code>

## Setup

1. Enable plugin in config trac.ini:

<code>
[components]
mercurialchangeset.* = enabled
</code>

2. Then sync your repository into Trac by running:

</code>
trac-admin /srv/trac/env/ mercurial sync repository_name
</code>

``repository_name`` can be default or a repository defined in Trac's repository table

3. Now you can keep your repository permanently synchronized in Trac by configuring a post-commit hook. If you are not familiar with Mercurial hooks, you can read <a href="http://www.selenic.com/mercurial/hgrc.5.html#hooks">official docs</a> about them.

In the server running Trac and the Mercurial repository, you should add the following to the hooks section of your global or personal hgrc:

<code>
[hooks]
changegroup.TracMercurialChangeset = /path/to/hook_script.sh
</code>
	
Your hook_script.sh should at least have something like this (example uses ``default`` repository):

<code>
trac-admin /srv/trac/env/ mercurial afterRevision $HG_NODE `pwd`
</code>

If you rather have a commit hook, you can set it like this:

<code>
[hooks]
commit.TracMercurialChangeset = /path/to/hook_script.sh
</code>

Your ``hook_script.sh`` should then look like this:

<code>
trac-admin /srv/trac/env/ mercurial revision $HG_NODE `pwd`
</code>

This will keep synced with Trac every Mercurial's repository that you have configured within Trac. Thanks to the way the path is checked, if the repository is NOT controlled by Trac, it will let you commit or push withouth failing. This way you can keep all your Trac's repositories synced with only one hook_script.

## How-To use it
 
This plugin adds five trac-admin commands that will let you synchronize your Mercurial repository with Trac. These are: ``lastRevision``, ``sync``, ``afterRevision``, ``revision`` and ``syncAll``

You can access the help for each command by doing:

<code>
trac-admin /srv/trac/env/ help mercurial <command> (e.g. lastRevision)
</code>

* **lastRevision**: Synchronize the last changeset in Mercurial repository into Trac's DB revision table. 
    
<code>
trac-admin /srv/trac/env/ mercurial lastRevision <repository>
</code>

* **sync**: Synchronize the whole Mercurial repository changelog into Trac's DB revision table. 

<code>
trac-admin /srv/trac/env/ mercurial sync <repository>
</code>

* **afterRevision**: Synchronize all changesets in Mercurial repository greater than the given revision into Trac's DB revision table.
    
<code>
trac-admin /srv/trac/env/ mercurial afterRevision <revision> <repository>
</code>

* **revision**: Synchronize the given revision from Mercurial's repository into Trac's DB revision table.
    
<code>
trac-admin /srv/trac/env/ mercurial revision <revision> <repository>
</code>

* **syncAll**: Synchronize all hg repositories under Trac's control into Trac's DB revision table.

<code>
trac-admin /srv/trac/env/ mercurial syncAll
</code>

* ``<revision>`` can be a revision number or a revision hash
* ``<repository>`` can be a repository name within Trac or the path to the root of the repository controlled by Trac


## Troubleshooting

1. If the hook is giving you an ``Error: Command not found`` that's because you don't have the right privileges. The user or role that executes the script should have read and write privileges in you Trac ENV. If this is not the case, you can fix it running trac-admin inside the hook script as sudo:

<code>
echo "yourpassword" | sudo -S trac-admin /srv/trac/env/ mercurial afterRevision $HG_NODE default
</code>

Of course this is neither an elegant fix, nor a very secure, but it certainly is a very easy one :) 

2. You can report bugs you find at the Project's Github, filling an issue. Please activate logging in Trac, so you can send as much information as possible. Please paste the traceback you will find at ``log/trac.log`` within your issue. This way it will be easier to fix any error. 

## Contributors

* Boris Kocherov (bkcocherov) http://github.com/bkocherov

## License

    Copyright (c) 2011
    Miguel Araujo Perez <miguel.araujo.perez@gmail.com>
    J. Javier Maestro de la Calle <jjmaestro@ieee.org>

    GNU General Public Licence (GPL)

    This work is free software; you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free Software
    Foundation; either version 2 of the License, or any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    GNU GPL v2: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
    GNU GPL v3: http://www.gnu.org/copyleft/gpl-3.0.html
