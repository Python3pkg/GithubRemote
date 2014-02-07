#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from pkg_resources import resource_filename
from .. import TOKEN_PATH
from .tools import waiting_effects
from ..tools import load_token, store_token, generate_tokens
from github import Github
from github.GithubException import GithubException
from github.Authorization import Authorization
from PyQt4.QtCore import QRegExp, QRect, Qt, QPoint, QSize, SIGNAL, SLOT
from PyQt4.QtGui import QWizardPage, QWizard, QRadioButton, QLineEdit, \
    QRegExpValidator, QVBoxLayout, QHBoxLayout, QLabel, QMainWindow, \
    QDialog, QIcon, QAction, QSizePolicy, QPushButton, QWidget, \
    QTableWidget, QTableWidgetItem, QAbstractItemView, QPixmap, \
    QFormLayout, QDialogButtonBox, QValidator, QMenu, QHeaderView, \
    QTabWidget, QTabBar, QStyle, QStylePainter, QStyleOptionTab
from AddRepoWizard import AddRepoWizard
from AddAccountWizard import AddAccountWizard
import urllib
import os

def image_path(image_name):
    return os.path.abspath(resource_filename(
        'GithubRemote.Gui.Images', image_name))

class MainWidget(QMainWindow):


    def __init__(self, parent=None):
        super(MainWidget, self).__init__(
                parent,
                windowTitle='GithubRemote',
                windowIcon=QIcon(image_path('git.png')),
                geometry=QRect(300, 300, 600, 372))

        self.repo_pixmap = QPixmap(image_path('book_16.png'))
        self.big_repo_pixmap = QPixmap(image_path('book_32.png'))
        self.repo_fork_pixmap = QPixmap(image_path('book_fork_16.png'))
        self.star_pixmap = QPixmap(image_path('star_16.png'))
        self.big_star_pixmap = QPixmap(image_path('star_32.png'))
        self.fork_pixmap = QPixmap(image_path('fork_16.png'))
        self.eye_pixmap = QPixmap(image_path('eye_16.png'))

        self.github = None        

        # Actions

        self.repoAddAction = QAction(
                QIcon(image_path('plus_48.png')),
                '&Add Repo', self,
                statusTip='Add a new repo')
        self.repoAddAction.triggered.connect(self.repoAdd)
        
        self.repoRemoveAction = QAction(
                QIcon(image_path('minus.png')),
                '&Remove Repo', self,
                statusTip='Remove repo')
        self.repoRemoveAction.triggered.connect(self.repoRemove)

        self.repoRefreshAction = QAction(
                QIcon(image_path('refresh.png')),
                'Refresh', self,
                statusTip='Refresh list of repos')
        self.repoRefreshAction.triggered.connect(self.reposRefresh)
        self.repoRefreshAction.triggered.connect(self.starsRefresh)

        self.addAccountAction = QAction(
                'Add Account', self,
                statusTip='Add Account')
        self.addAccountAction.triggered.connect(self.addAccount)

        # userPushButton - Displays the current active username and 
        # image on the top right of the toolbar.
        
        self.userButtonMenu = UserButtonMenu(32,32)

        # ToolBar

        self.toolBar = self.addToolBar('Main')
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolBar.addAction(self.repoAddAction)
        self.toolBar.addAction(self.repoRemoveAction)
        self.toolBar.addAction(self.repoRefreshAction)
        self.toolBar.addWidget(spacer)
        self.toolBar.addWidget(self.userButtonMenu)

        # Menu

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        actionMenu = menuBar.addMenu('&Action')
        fileMenu.addAction(self.addAccountAction)
        actionMenu.addAction(self.repoAddAction)
        actionMenu.addAction(self.repoRemoveAction)
        actionMenu.addAction(self.repoRefreshAction)

        # StatusBar

        statusBar = self.statusBar()
        self.setStatusBar(statusBar)

        # reposTableWidget - Displays a list of the users repositories

        self.reposTableWidget = QTableWidget(0, 5,
                selectionBehavior = QAbstractItemView.SelectRows,
                selectionMode = QAbstractItemView.SingleSelection,
                editTriggers = QAbstractItemView.NoEditTriggers,
                itemSelectionChanged = self.actionsUpdate)
        self.reposTableWidget.horizontalHeader().setResizeMode(
                QHeaderView.ResizeToContents)
        self.reposTableWidget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.reposTableWidget.horizontalHeader().setVisible(False)
        self.reposTableWidget.verticalHeader().setVisible(False)
        self.reposTableWidget.setShowGrid(False)
        self.reposTableWidget.verticalHeader().setMinimumSectionSize(25)

        # repoTab - Layout
        reposTab = QWidget()
        reposTabLayout = QVBoxLayout(reposTab)
        reposTabLayout.addWidget(self.reposTableWidget)
        reposTab.setLayout(reposTabLayout)

        # starsTableWidget - Displays a list of the users repositories

        self.starsTableWidget = QTableWidget(0, 5,
                selectionBehavior = QAbstractItemView.SelectRows,
                selectionMode = QAbstractItemView.SingleSelection,
                editTriggers = QAbstractItemView.NoEditTriggers,
                itemSelectionChanged = self.actionsUpdate)
        self.starsTableWidget.horizontalHeader().setResizeMode(
                QHeaderView.ResizeToContents)
        self.starsTableWidget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.starsTableWidget.horizontalHeader().setVisible(False)
        self.starsTableWidget.verticalHeader().setVisible(False)
        self.starsTableWidget.setShowGrid(False)
        self.starsTableWidget.verticalHeader().setMinimumSectionSize(25)

        # repoTab - Layout
        starsTab = QWidget()
        starsTabLayout = QVBoxLayout(starsTab)
        starsTabLayout.addWidget(self.starsTableWidget)
        starsTab.setLayout(starsTabLayout)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabBar(FlippedTabBar(self))
        self.tabs.addTab(reposTab, QIcon(self.big_repo_pixmap), "repos")
        self.tabs.addTab(starsTab, QIcon(self.big_star_pixmap), "stars")
        self.tabs.setTabPosition(QTabWidget.West)

        # Layout

        self.setCentralWidget(self.tabs)
        self.actionsUpdate()
        self.show()
        
        # Update

        self.loadUserMenu()
        self.activeUserAction.setVisible(False)
        self.authenticate()
        self.actionsUpdate()
        self.reposRefresh()
        self.starsRefresh()
        self.updateImage()

    
    @waiting_effects
    def updateImage(self):

        try:
            url = self.github.get_user().avatar_url
        except (GithubException, AttributeError): 
            return 
        data = urllib.urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.activeUserAction.setIcon(QIcon(pixmap))
        self.userButtonMenu.setPixmap(pixmap)
        self.userButtonMenu.setText(self.github.get_user().login)
   
    @waiting_effects
    def loadUserMenu(self):
        
        action = None
        for _, username, token in generate_tokens(TOKEN_PATH, 'github'):
            
            try:
                url = Github(token).get_user().avatar_url
            except (GithubException, AttributeError): 
                action = QAction(username, self, triggered=self.changeActive)
                self.userButtonMenu.addAction(action)
                continue
            data = urllib.urlopen(url).read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            action = QAction(QIcon(pixmap), username, self,
                    triggered=self.changeActive)
            action.setIconVisibleInMenu(True)
            self.userButtonMenu.addAction(action)
        
        self.activeUserAction = action
    
    def changeActive(self):

        sender = self.sender()

        self.activeUserAction.setVisible(True)
        self.activeUserAction = sender
        self.activeUserAction.setVisible(False)
        self.authenticate()
        self.actionsUpdate()
        self.reposRefresh()
        self.starsRefresh()
        self.updateImage()

    @waiting_effects
    def reposRefresh(self):

        self.reposTableWidget.clearContents()

        try:
            repos = self.github.get_user().get_repos()
            self.reposTableWidget.setRowCount(self.github.get_user().public_repos)
        except (GithubException, AttributeError):
            return
        for row, repo in enumerate(repos):
            imageLabel = QLabel()
            if repo.fork:
                imageLabel.setPixmap(self.repo_fork_pixmap)
            else:
                imageLabel.setPixmap(self.repo_pixmap)
            imageLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            imageLabel.setMargin(5)

            self.reposTableWidget.setCellWidget(row, 0, imageLabel)
            label = QLabel('<b>{}</b><br />{}'.format(
                        str(repo.name), str(repo.description)))
            label.setAlignment(Qt.AlignVCenter)
            label.setMargin(5)
            label.setWordWrap(True)
            self.reposTableWidget.setCellWidget(row, 1, label)
            self.reposTableWidget.setItem(row, 2, 
                    QTableWidgetItem(QIcon(self.star_pixmap), str(repo.stargazers_count)))
            self.reposTableWidget.setItem(row, 3, 
                    QTableWidgetItem(QIcon(self.eye_pixmap), str(repo.watchers_count)))
            self.reposTableWidget.setItem(row, 4, 
                    QTableWidgetItem(QIcon(self.fork_pixmap), str(repo.forks_count)))

        self.reposTableWidget.resizeRowsToContents()

    @waiting_effects
    def starsRefresh(self):

        self.starsTableWidget.clearContents()

        try:
            starred = self.github.get_user().get_starred()
            self.starsTableWidget.setRowCount(self.github.get_user().public_repos)
        except (GithubException, AttributeError):
            return
        for row, repo in enumerate(starred):
            imageLabel = QLabel()
            if repo.fork:
                imageLabel.setPixmap(self.repo_fork_pixmap)
            else:
                imageLabel.setPixmap(self.repo_pixmap)
            imageLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            imageLabel.setMargin(5)

            self.starsTableWidget.setCellWidget(row, 0, imageLabel)
            label = QLabel('<b>{}/{}</b><br />{}'.format(
                str(repo.owner.login), str(repo.name), str(repo.description)))
            label.setAlignment(Qt.AlignVCenter)
            label.setMargin(5)
            label.setWordWrap(True)
            self.starsTableWidget.setCellWidget(row, 1, label)
            self.starsTableWidget.setItem(row, 2, 
                    QTableWidgetItem(QIcon(self.star_pixmap), '0'))
            self.starsTableWidget.setItem(row, 3, 
                    QTableWidgetItem(QIcon(self.eye_pixmap), str(repo.watchers_count)))
            self.starsTableWidget.setItem(row, 4, 
                    QTableWidgetItem(QIcon(self.fork_pixmap), str(repo.forks_count)))

        self.starsTableWidget.resizeRowsToContents()

    @waiting_effects
    def authenticate(self):
        
        username = str(self.activeUserAction.text())
        try:
            token = load_token(TOKEN_PATH, 'github', username) 
            self.github = Github(token)
        except IOError, EOFError:
            self.github = None
    
    def actionsUpdate(self):
        # TODO disable if no user is logged in
        if self.github is None:
            self.repoAddAction.setEnabled(False)
            self.repoRemoveAction.setEnabled(False)
            self.repoRefreshAction.setEnabled(False)
        else:
            self.repoAddAction.setEnabled(True)
            self.repoRefreshAction.setEnabled(True)
            if self._isARepoSelected():
                self.repoRemoveAction.setEnabled(True)
            else:
                self.repoRemoveAction.setEnabled(False)

    def addAccount(self):
        wizard = AddAccountWizard(self)
        if wizard.exec_():
            username = str(wizard.field('username').toString())
            token = str(wizard.field('token').toString())
            store_token(TOKEN_PATH, 'github', username, token)
            self.authenticate()
            self.reposRefresh()
            self.updateImage()
            self.actionsUpdate()

    def repoAdd(self):
        wizard = AddRepoWizard(self.github, self)
        if wizard.exec_():
            self.github.get_user().create_repo(
                str(wizard.field('name').toString()),
                description=str(wizard.field('description').toString()),
                private=bool(wizard.field('private').toBool()),
                auto_init=bool(wizard.field('auto_init').toBool()),
                gitignore_template=str(wizard.field('gitignore').toString()),
                homepage=str(wizard.field('homepage').toString()),
                has_wiki=bool(wizard.field('has_wiki').toBool()),
                has_downloads=bool(wizard.field('has_downloads').toBool()),
                has_issues=bool(wizard.field('has_issues').toBool()))
            self.reposRefresh()
    
    def repoRemove(self):
        
        row = self._selectedRepoRow()
        name = self.reposTableWidget.item(row, 0).text()
        dialog = RepoRemoveDialog(self.github, name)
        if dialog.exec_():
            self.github.get_user().get_repo(str(name)).delete()
            self.reposRefresh()

    def _isARepoSelected(self):
        """ Return True if a repo is selected else False """
        if len(self.reposTableWidget.selectedItems()) > 0:
            return True
        else:
            return False

    def _selectedRepoRow(self):
        """ Return the currently select repo """
        # TODO - figure out what happens if no repo is selected
        selectedModelIndexes = \
            self.reposTableWidget.selectionModel().selectedRows()
        for index in selectedModelIndexes:
            return index.row()

class UserButtonMenu(QPushButton):
    def  __init__(self, image_width, image_height, parent=None):
        super(UserButtonMenu, self).__init__(parent)
        
        self.image_width = image_width
        self.image_height = image_height

        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setSizePolicy(
                QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))

        self.imageLabel = QLabel(self)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setSizePolicy(
                QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.setSizePolicy(
                QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.userMenu = QMenu('user accounts menu') # TODO Remove magic

        hbox = QHBoxLayout()
        hbox.addWidget(self.imageLabel)
        hbox.addWidget(self.label)
        self.setLayout(hbox)
        self.setMenu(self.userMenu)

    def addAction(self, action):

        self.userMenu.addAction(action)

    def setPixmap(self, pixmap):
        
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setFixedSize(
                self.image_width, self.image_height)
    
    def setText(self, text):

        self.label.setText(text)
        self.adjustSize()

    def adjustSize(self):
        # TODO - Remove magic numbers
        label_size = self.label.sizeHint()
        image_size = self.imageLabel.sizeHint()
        self.setFixedSize(label_size.width() + 70, 48)
        self.userMenu.setFixedWidth(label_size.width() + 70)

class RepoRemoveDialog(QDialog):
    def __init__(self, github, name, parent=None):
        super(RepoRemoveDialog, self).__init__(
            parent,
            windowTitle="Remove Repo")

        self.github = github 
        self.login = self.github.get_user().login
        self.name = name

        self.label = QLabel('''
        <p>Are you sure?</p>

        <p>This action <b>CANNOT</b> be undone.</p>
        <p>This will delete the <b>{}/{}</b> repository, wiki, issues, and
        comments permanently.</p>

        <p>Please type in the name of the repository to confirm.</p>
        '''.format(self.login, self.name))
        self.label.setTextFormat(Qt.RichText)
       
        validator = QRegExpValidator(
                QRegExp(r'{}/{}'.format(self.login, self.name)))
        self.nameEdit = QLineEdit(textChanged=self.textChanged)
        self.nameEdit.setValidator(validator)

        # Form

        self.form = QFormLayout()
        self.form.addRow(self.label)
        self.form.addRow(self.nameEdit)
        
        # ButtonBox

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            accepted=self.accept, rejected=self.reject)
        
        # Layout

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.form)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        
        self.textChanged()

    def textChanged(self):
        
        if self.nameEdit.validator().validate(self.nameEdit.text(), 0)[0] \
                == QValidator.Acceptable:
            b = True
        else:
            b = False
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(b)

class FlippedTabBar(QTabBar):
    def __init__(self, parent=None):
        super(FlippedTabBar, self).__init__(parent)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            tabRect.setLeft(0)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            self.tabIcon(index).paint(painter, tabRect)
        painter.end()
