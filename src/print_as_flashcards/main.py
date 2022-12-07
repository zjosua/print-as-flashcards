# -*- coding: utf-8 -*-

"""
Anki Add-on: Print as Flashcards

This add-on is a modified version of the basic printing add-on by Damien Elmes.
The file flashcards.html that this version produces will print as double-sided
flashcards in a grid configured by the add-on config.

Authors: Goal Oriented Academics LLC <goalorientedacademics@gmail.com>
         zjosua <https://github.com/zjosua>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import re, urllib
from aqt.qt import *
from anki.utils import is_win
from anki.hooks import runHook, addHook
from aqt.utils import openLink, tooltip
from aqt import mw
from anki.utils import ids2str

from .config import local_conf

CARDS_PER_ROW = local_conf["cards_per_row"]
ROWS_PER_TABLE = local_conf["rows_per_table"]
CARDS_PER_TABLE = CARDS_PER_ROW * ROWS_PER_TABLE

def sortFieldOrderCids(did):
    dids = [did]
    for name, id in mw.col.decks.children(did):
        dids.append(id)
    return mw.col.db.list("""
select c.id from cards c, notes n where did in %s
and c.nid = n.id order by n.sfld""" % ids2str(dids))

def onPrint(cids=None):
    path = os.path.join(mw.pm.profileFolder(), "flashcards.html")
    if cids:
        ids = cids
    else:
        ids = sortFieldOrderCids(mw.col.decks.selected())
    def esc(s):
        # strip off the repeated question in answer if exists
        #s = re.sub("(?si)^.*<hr id=answer>\n*", "", s)
        # remove type answer
        s = re.sub("\[\[type:[^]]+\]\]", "", s)
        return s
    def prefixed_path(path):
        if is_win:
            prefix = "file:///"
        else:
            prefix = "file://"
        return prefix + path
    buf = open(path, "w")
    buf.write("<html>" + mw.baseHTML())
    buf.write("<meta charset=\'utf-8\'><head>")
    buf.write("""<style>
img   {{ max-width: 100%; }}
td    {{ border: 1px solid #ccc;
        padding: 0;
        width: {width:.0f}%; }}
table {{ table-layout: fixed; 
        border-spacing: 0;
	page-break-after: always;
	width: 100%;
	height: 100%; }}
.a td {{ border: none; }}
tr    {{ height: {height:.0f}%; }}
@page {{ size: landscape; }}
</style></head><body>""".format(width = 100 / CARDS_PER_ROW, \
                                height = 100 / ROWS_PER_TABLE))
    ans = []
    que = []
    processed_notes = []
    mw.progress.start(immediate=True)
    for j, cid in enumerate(ids):
        c = mw.col.get_card(cid)
        if c.note().id not in processed_notes:
            q = esc(c.question())
            a = esc(c.answer())
            que.append(q)
            ans.append(a)
            processed_notes.append(c.note().id)
    
    if (len(que) % CARDS_PER_TABLE != 0):
        for i in range(len(que) % CARDS_PER_TABLE):
            que.append("")
            ans.append("")
    
    for i in range((len(que)//CARDS_PER_TABLE)):
        theTable = ["<table>","<table class=\'a\'>"]
        for j in range(ROWS_PER_TABLE):
            theTable[0] += "<tr>"
            theTable[1] += "<tr>"
            for k in range(CARDS_PER_ROW):
                theTable[0] += "<td><center>"+que[CARDS_PER_TABLE * i + \
                                CARDS_PER_ROW * j + k] + "</td></center>"
                theTable[1] += "<td><center>"+ans[CARDS_PER_TABLE * i + \
                                CARDS_PER_TABLE - CARDS_PER_ROW - \
                                CARDS_PER_ROW * j + k] + "</td></center>"
            theTable[0] += "</tr>"
            theTable[1] += "</tr>"
        theTable[0] += "</table>"
        theTable[1] += "</table>"
        buf.write(theTable[0])
        buf.write(theTable[1])
    buf.write("</body></html>")
    mw.progress.finish()
    buf.close()
    tooltip("Creating printable flashcards...", period=3000)
    QDesktopServices.openUrl(QUrl.fromUserInput(prefixed_path(path)))

def addShortcut(browser):
    a = QAction("&Make Flashcards", browser)
    a.setShortcut(QKeySequence("Ctrl+M"))
    a.triggered.connect(lambda : onPrint(browser.selectedCards()))
    browser.form.menuEdit.addAction(a)

addHook("browser.setupMenus", addShortcut)
