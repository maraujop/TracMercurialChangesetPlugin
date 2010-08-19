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

from trac.admin import IAdminCommandProvider
from trac.core import *
from trac.util.text import printout
from mercurial import ui, hg, context
from mercurial.node import short
import sys, re, os

class MercurialChangesetAdmin(Component):
	"""trac-admin command provider for mercurialchangesets plugin"""

	implements(IAdminCommandProvider)

	def __init__ (self):
		# Trac's Database connection
		self.db = self.env.get_db_cnx()
		self.cursor = self.db.cursor()

	# IAdminCommandProvider methods
	# ---------------------------------------

	def get_admin_commands(self):
		yield ('mercurial lastRevision', '<repository>',
				"""Insert Mercurial's last changeset into Trac's DB revision table.\n
					Example: mercurial lastRevision default\n
					Example: mercurial lastRevision Important-project\n
					Example: mercurial lastRevision /path/to/repo
				""",
				None, self.sync_last_revision)

		yield ('mercurial sync', '<repository>',
				"""Synchronize the whole Mercurial's repository changelog into Trac's DB revision table.\n
					Example: mercurial sync default\n
					Example: mercurial sync Important-project\n
					Example: mercurial sync /path/to/repo
				""",
				None, self.sync_repository)

		yield ('mercurial afterRevision', '<revision> <repository>',
				"""Synchronize all changesets from Mercurial's repository greater than the given revision into Trac's DB revision table.\n
					Example: mercurial afterRevision 43 default\n
					Example: mercurial afterRevision 3ece62c442a6f3d5dc20b2b9a9fc779 default\n
					Example: mercurial afterRevision 3ece62c442a6f3d5dc20b2b9a9fc779 /path/to/repo
				""",
				None, self.sync_after_revision)

		yield ('mercurial revision', '<revision> <repository>',
				"""Synchronize the given revision from Mercurial's repository into Trac's DB revision table.\n
					Example: mercurial revision 33 default\n
					Example: mercurial revision 3ece62c442a6f3d5dc20b2b9a9fc779 Important-project\n
					Example: mercurial revision 3ece62c442a6f3d5dc20b2b9a9fc779 /path/to/repo
				""",
				None, self.sync_specific_revision)

	# Internal methods
	# ---------------------------------------
	def get_repository_id(self, repository):
		"""
		Returns the repository id inside Trac. This is needed to support
		multi-repository since v0.12. However, in lower versions of Trac, by simply
		using 'default' as repository name it should work just fine :)
		"""
		if (repository == "default"):
			return 1

		# The repository can be a path to the root of the repository
 	 	if os.path.isdir(repository):
			# The default repository is not in the repository table
			# We need to check it apart, against the Trac's config file
			default_repository_path = self.config.get("trac", "repository_dir", False) 
			contains = re.compile(repository)
			if contains.match(default_repository_path):
				return 1

			sql_string = """
				SELECT id
 	 	 	 	 FROM repository
 	 	 	 	 WHERE name = 'dir' AND value LIKE %s
 	 	 	"""
 	 	 	self.cursor.execute(sql_string, ("%%%s%%" % repository,))
 	 	 	row = self.cursor.fetchone()
			
			# If the repository is not controlled by Trac
			# We exit with successful execution. This way we can make a generic 
			# Mercurial hook that will work with all repositories in the machine
			if not row:
				printout("[E] Path",repository,"was not found in repository table, neither in Trac's config. Sync will not be executed")
				sys.exit(0)

		# Otherwise it's the name of the repository
		else:
			sql_string = """
				SELECT id
				 FROM repository
				 WHERE name = 'name' AND value LIKE %s
			"""
			self.cursor.execute(sql_string, (repository,))
			row = self.cursor.fetchone()
		
			if not row:
				printout("[E] Sorry, repository name or path not found")
				sys.exit(1)
		
		return row[0]
	
	def get_mercurial_repository(self, repository, repository_id):
		"""
		Returns a Mercurial repository API object pointing at the repository
 	 	given by the trac-admin parameter
		"""
		try:
			if (repository == "default"):
				repository_dir = self.config.get("trac", "repository_dir", False)
			else:
				if os.path.isdir(repository):
					repository_dir = repository
				else:
					sql_string = """
						SELECT value
			 	 	   	 FROM repository
			 		 	 WHERE name = 'dir' AND id = %s
					"""
					self.cursor.execute(sql_string, (repository_id,))
					row = self.cursor.fetchone()
					if not row:
						printout("[E] Sorry, but repository name is not defined in repository table")
						sys.exit(1)

					repository_dir = row[0]

			return hg.repository(ui.ui(), repository_dir)
	
		except repo.RepoError:
			printout("[E] Impossible to connect to Mercurial repository at", repository_dir)
			sys.exit(1)

	def initialize_repository(self, repository):
		"""
		As the repository name is not known till a trac-admin command is called,
 	 	we cannot initialize the repository in the constructor. Thus, we must
 	 	call this method before performing any action on the repository.
		"""
		self.repository_id = self.get_repository_id(repository)
		self.repository = self.get_mercurial_repository(repository, self.repository_id)	

	def check_revision(self, rev, rev_hash):
		"""
		Checks if the revision is already in Trac's revision table. If it exists
		returns True, False otherwise
		"""
		sql_string = """
			SELECT rev, author, time, message
			 FROM revision
			 WHERE rev LIKE %s
		"""
		self.cursor.execute(sql_string, (rev + ":" + rev_hash,))
		rows = self.cursor.fetchall()
		
		return len(rows) == 1

	def insert_revision(self, repository_id, rev, rev_hash, time, author, description):
		"""
		Inserts the changeset information into Trac's revision table.
		"""
		sql_string = """
			INSERT INTO revision (repos, rev, time, author, message)
			 VALUES (%s, %s, %s, %s, %s)
		"""
		# We insert only the first line of the commit description (the summary)
		# TODO: think of having a config flag to choose from saving summary or the
		# whole commit message
		eol = re.compile(r'\r?\n')
		first_line = eol.split(description.strip())[0]
		
		self.cursor.execute(sql_string, (repository_id, rev + ":" + rev_hash, time, author, first_line))
		self.db.commit()
	
	def sync_revision(self, revision):
		"""
		Receives a revision number (or revision hash) and an already-initialized
		repository environment (that's why you cannot call this method directly
		from a yield command). Then, it gets the revision information from
		Mercurial repository and inserts it into Trac's revision table if it's
 	 	not already present.
		"""
		# Let's get Mercurial commit information
		node = self.repository.lookup(revision)
		# Let's get its change context object from the repository
		ctx = self.repository.changectx(node)
		rev = str(ctx.rev())
		rev_hash = short(ctx.node())	
		
		# If revision is not already in Trac's revision table, insert it
		if not(self.check_revision(rev, rev_hash)):
			description = ctx.description()
			time = ctx.date()[0]
			author = ctx.user()
			#self.log.debug("Inserting revision %s" % rev + ":" + rev_hash)
			self.insert_revision(self.repository_id, rev, rev_hash, time, author, description)	   
		#else:
			#self.log.debug("Revision %s already present in Trac" % rev + ":" + rev_hash)

	def sync_last_revision(self, repository):
		"""
		Synchronize the last changeset in Mercurial repository into Trac's DB
		revision table. 
		"""
		self.initialize_repository(repository)
		self.sync_revision(self.repository['tip'].rev())

	def sync_repository(self, repository):
		"""
		Synchronize the whole Mercurial repository changelog into Trac's DB
		revision table. 
		"""
		self.initialize_repository(repository)

		for change in self.repository.changelog:
			self.sync_revision(change.real)

	def sync_after_revision(self, revision, repository):
		"""
		Synchronize all changesets in Mercurial's repository greater than the
 	 	given revision into Trac's DB revision table.
		"""
		self.initialize_repository(repository)

		# We don't know if revision is a number or a hash. Therefore, we have
		# to get the related change context to get the number of the revision
		node = self.repository.lookup(revision)
		ctx = self.repository.changectx(node)
		initial_revision = ctx.rev()
		until = len(self.repository.changelog)
		
		for rev in range(initial_revision, until):
			self.sync_revision(rev)

	def sync_specific_revision(self, revision, repository):
		"""
		Synchronize the given revision from Mercurial's repository into Trac's
 	 	DB revision table.
		"""
		self.initialize_repository(repository)
		self.sync_revision(revision)
