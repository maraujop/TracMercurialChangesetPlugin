# Copyright (c) 2010
# Miguel Araujo Perez <miguel.araujo.perez@gmail.com>
# J. Javier Maestro de la Calle <jjmaestro@ieee.org>
#
# GNU General Public Licence (GPL)
#
# This work is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
#  GNU GPL v2: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#  GNU GPL v3: http://www.gnu.org/copyleft/gpl-3.0.html

++++++++++++++++++++++++++++
MercurialChangesetPlugin 0.1
++++++++++++++++++++++++++++

+++++++++++++++++++++
 About this software 
+++++++++++++++++++++
Latest branch at http://github.com/maraujop/TracMercurialChangesetPlugin

MercurialChangesetPlugin is a Trac plugin that inserts Mercurial repository
information into Trac's database, thus integrating Mercurial and Trac to a
fuller extend that the default Trac support.

++++++++++++++
 Installation 
++++++++++++++
You can install this software as a normal Trac plugin.

 1. First uninstall former MercurialChangesetPlugin version, if you have
    installed it before.

 2. Change directory to Trac's plugin's directory containing setup.py.

 3. If you want to install this plugin globally, you will have to install this
    plugin to the python path:

    $ python setup.py install

 4. If you want to install this plugin to your trac instance only, create the
    egg from the repo running:

    $ python setup.py bdist_egg

	  Then, copy the generated egg file to the trac instance's plugin directory

		$ cp dist/*.egg /srv/trac/env/plugins

 5. Enable plugin in config trac.ini:

	  [components]
	  mercurialchangeset.* = enabled

 6. Then sync your repository into Trac by running:

	  trac-admin /srv/trac/env/ mercurial sync <repository name>

		<repository name> can be default or a repository defined in Trac's
		repository table

 6. Now you can keep your repository permanently synchronized in Trac by
	configuring a post-commit hook. It's highly recommended that you read
	http://www.selenic.com/mercurial/hgrc.5.html#hooks

	In the server running Trac and the Mercurial repository, you should add the
    following to the hooks section of your global or personal hgrc:

	  [hooks]
	  changegroup.TracMercurialChangeset = /path/to/hook_script.sh
	
	Your hook_script.sh should at least have something like this
	(example uses default repository):

	  trac-admin /srv/trac/env/ mercurial afterRevision $HG_NODE `pwd`


    If you rather have a commit hook, you can set it like this:

	  [hooks]
	  commit.TracMercurialChangeset = /path/to/hook_script.sh

    Your hook_script.sh should then look like this:

	  trac-admin /srv/trac/env/ mercurial revision $HG_NODE `pwd`

	This will keep synced with Trac every Mercurial's repository that you have
	configured within Trac. Thanks to the way the path is checked, if the 
	repository is NOT controlled by Trac, it will let you commit or push
	withouth failing. This way you can keep all your Trac's repositories
	synced with only one hook_script

+++++++++++++++
 Prerequisites
+++++++++++++++
 * Mercurial
 * Trac (tested on v0.12, might work on others)

+++++++++++++++
 How-To use it
+++++++++++++++
 This plugin adds four trac-admin commands that will let you synchronize your
 Mercurial repository with Trac.
 
 These are: lastRevision, sync, afterRevision and revision.

 You can access the help for each command by doing:

 $ trac-admin /srv/trac/env/ help mercurial <command> (e.g. lastRevision)

 1. trac-admin /srv/trac/env/ mercurial lastRevision <repository>
	Synchronize the last changeset in Mercurial repository into Trac's DB
	revision table. 

 2. trac-admin /srv/trac/env/ mercurial sync <repository>
	Synchronize the whole Mercurial repository changelog into Trac's DB
	revision table. 

 3. trac-admin /srv/trac/env/ mercurial afterRevision <revision> <repository>
	Synchronize all changesets in Mercurial repository greater than the given
	revision into Trac's DB revision table.

 4. trac-admin /srv/trac/env/ mercurial revision <revision> <repository>
	Synchronize the given revision from Mercurial's repository into Trac's DB
	revision table.

	<revision> can be a revision number or a revision hash
	<repository> can be a repository name within Trac or the path to the root
	of the repository controlled by Trac

+++++++++++++++++
 Troubleshooting
+++++++++++++++++

 1. If the hook is giving you an "Error: Command not found" that's because you
	don't have the right privileges. The user or role that executes the script
	should have read and write privileges in you Trac ENV.
		
	If this is not the case, you can fix it running trac-admin inside the hook
	script as sudo:
		
	echo "yourpassword" | sudo -S trac-admin /srv/trac/env/ mercurial afterRevision $HG_NODE default

	Of course this is neither an elegant fix, nor a very secure, but it
	certainly is a very easy one :) 

 2. You can report bugs you find at the Project's Github, filling an issue.
	Please activate logging in Trac, so you can send as much information as
	possible. Please paste the traceback you will find at log/trac.log within
	your issue. This way it will be easier to fix any error. 
