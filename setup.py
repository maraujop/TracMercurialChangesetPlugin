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

from setuptools import find_packages, setup

extra = {}

setup(
    name = 'TracMercurialChangesetPlugin',
    version = "0.3",
    description = "Insert Mercurial's changesets into Trac's DB revision table",
    author = "Miguel Araujo Perez, J. Javier Maestro de la Calle",
    author_email = "miguel.araujo.perez@gmail.com",
    url = "http://github.com/maraujop/TracMercurialChangesetPlugin",
    license = "GPL",
    packages = find_packages(exclude=['tests*']),
    include_package_data = True,

    package_data = { 'mercurialchangeset': [ 
        '*.txt'
        ],
    },

    zip_safe = True,

    keywords = "trac ticket plugin mercurial hg changeset integration",

    classifiers = [
        'Framework :: Trac',
    ],

    install_requires = [],

    entry_points = """
        [trac.plugins]
        mercurialchangeset.admin = mercurialchangeset.admin
    """,

    **extra

    )
