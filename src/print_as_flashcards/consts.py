# -*- coding: utf-8 -*-

"""
This file is part of the Print as Flashcards add-on for Anki.

Global variables

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import re
import sys
import os
from anki import version

version_re = re.compile(r"^(\d*)\.(\d*)(\.(\d*))?$")
mo = version_re.search(version)
anki21 = version.startswith("2.1.") or int(mo.group(1)) >= 23
sys_encoding = sys.getfilesystemencoding()

if anki21:
    addon_path = os.path.dirname(__file__)
else:
    addon_path = os.path.dirname(__file__).decode(sys_encoding)
