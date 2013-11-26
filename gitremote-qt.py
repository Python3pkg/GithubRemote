#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

class MainWidget(QMainWindow):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(
                parent,
                windowTitle='GitRemote',
                #windowIcon=QIcon('images/GitRemote.png'),
                geometry=QRect(300, 300, 600, 372))

        self.repoAddAction = QAction(
                #QIcon('images/repoAdd.png'),
                '&Add Repo', self,
                statusTip='Add a new repo')
        
        self.repoRemoveAction = QAction(
                #QIcon('images/repoRemove.png'),
                '&Remove Repo', self,
                statusTip='Remove repo')
       
        self.userSignInAction = QAction(
                'User Sign&in', self,
                statusTip='Sign In')

        self.userSignOutAction = QAction(
                'User Sign&out', self,
                statusTip='Sign Out')

        # ToolBar
        self.toolBar = self.addToolBar('Main')
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.addAction(self.repoAddAction)
        self.toolBar.addAction(self.repoRemoveAction)

        # Menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        actionMenu = menuBar.addMenu('&Action')
        fileMenu.addAction(self.userSignInAction)
        fileMenu.addAction(self.userSignOutAction)
        actionMenu.addAction(self.repoAddAction)
        actionMenu.addAction(self.repoRemoveAction)

        # reposTableWidget
        self.scriptsTableWidgetHeaders = [""]
        self.scriptsTableWidget = QTableWidget(0,
                len(self.scriptsTableWidgetHeaders),
                selectionBehavior = QAbstractItemView.SelectRows,
                editTriggers = QAbstractItemView.NoEditTriggers,
                itemSelectionChanged = self.actionsUpdate)
        self.scriptsTableWidget.setHorizontalHeaderLabels(
                self.scriptsTableWidgetHeaders)

        # Layout
        self.setCentralWidget(self.scriptsTableWidget)
        self.actionsUpdate()
        self.show()
       
    def actionsUpdate(self):
        """ TODO """
        pass

def main():
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
