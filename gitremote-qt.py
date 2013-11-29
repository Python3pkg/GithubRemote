#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import pickle
import urllib

class MainWidget(QMainWindow):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(
                parent,
                windowTitle='GitRemote',
                #windowIcon=QIcon('images/GitRemote.png'),
                geometry=QRect(300, 300, 600, 372))

        self.repoAddAction = QAction(
                QIcon('images/plus_48.png'),
                '&Add Repo', self,
                statusTip='Add a new repo')
        self.repoAddAction.triggered.connect(self.repoAdd)
        
        self.repoRemoveAction = QAction(
                QIcon('images/minus.png'),
                '&Remove Repo', self,
                statusTip='Remove repo')
       
        self.userSignInAction = QAction(
                'User Sign&in', self,
                statusTip='Sign In')
        self.userSignInAction.triggered.connect(self.userSignIn)

        self.userSignOutAction = QAction(
                'User Sign&out', self,
                statusTip='Sign Out')
        
        self.userLabel = QLabel(self)
        self.userAction = QAction('', self)
        self.userAction.setCheckable(False)

        # ToolBar
        self.toolBar = self.addToolBar('Main')
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolBar.addAction(self.repoAddAction)
        self.toolBar.addAction(self.repoRemoveAction)
        self.toolBar.addWidget(spacer)
        self.toolBar.addWidget(self.userLabel)
        self.toolBar.addAction(self.userAction)

        # Menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        actionMenu = menuBar.addMenu('&Action')
        fileMenu.addAction(self.userSignInAction)
        fileMenu.addAction(self.userSignOutAction)
        actionMenu.addAction(self.repoAddAction)
        actionMenu.addAction(self.repoRemoveAction)

        # reposTableWidget
        self.reposTableWidgetHeaders = ["Name", "Description"]
        self.reposTableWidget = QTableWidget(0,
                len(self.reposTableWidgetHeaders),
                selectionBehavior = QAbstractItemView.SelectRows,
                selectionMode = QAbstractItemView.SingleSelection,
                editTriggers = QAbstractItemView.NoEditTriggers,
                itemSelectionChanged = self.actionsUpdate)
        self.reposTableWidget.setHorizontalHeaderLabels(
                self.reposTableWidgetHeaders)

        # Layout
        self.setCentralWidget(self.reposTableWidget)
        self.actionsUpdate()
        self.show()
        
        self.authenticate()
        self.reposRefresh()
        self.updateImage()
        
    def updateImage(self):

        if not self.github:
            return
        url = self.github.get_user().avatar_url
        data = urllib.urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.userAction.setIcon(QIcon(pixmap))
        name = self.github.get_user().name
        self.userLabel.setText(name)

    def reposRefresh(self):

        if not self.github:
            return
        repos = self.github.get_user().get_repos()
        self.reposTableWidget.setRowCount(self.github.get_user().public_repos)
        for row, repo in enumerate(repos):
            nameTableWidgetItem = QTableWidgetItem(str(repo.name))
            descTableWidgetItem = QTableWidgetItem(str(repo.description))
            self.reposTableWidget.setItem(row, 0, nameTableWidgetItem)
            self.reposTableWidget.setItem(row, 1, descTableWidgetItem)
        for i in range(self.reposTableWidget.columnCount()-1):
            self.reposTableWidget.resizeColumnToContents(i)
        self.reposTableWidget.resizeRowsToContents()

    def authenticate(self):

        try:
            f = open('authentication.pickle', 'r')
            authentication = pickle.load(f)
            self.github = Github(authentication.token)
            f.close()
        except IOError, EOFError:
            self.github = None

    def actionsUpdate(self):
        """ TODO """
        pass

    def userSignIn(self):
        wizard = userSignInWizard(self)
        if wizard.exec_():
            pass
    
    def repoAdd(self):
        wizard = RepoAddWizard(self.github, self)
        if wizard.exec_():
            self.github.get_user().create_repo(
                wizard.repo_details['name'],
                description=wizard.repo_details['description'],
                private=wizard.repo_details['private'],
                auto_init=wizard.repo_details['init'],
                gitignore_template=wizard.repo_details['gitignore'])

class GithubCredentialsWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(GithubCredentialsWizardPage, self).__init__(
            parent,
            title="Credentials",
            subTitle="Enter your username/password or token")
        
        self.userPassRadioButton = QRadioButton(toggled=self.changeMode)
        self.tokenRadioButton = QRadioButton(toggled=self.changeMode)

        #  LineEdits
        self.usernameEdit = QLineEdit()
        self.passwordEdit = QLineEdit()
        self.tokenEdit    = QLineEdit()
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.tokenEdit.setEchoMode(QLineEdit.Password)
      
        # Form
        form = QFormLayout()
        form.addRow("<b>username/password</b>", self.userPassRadioButton)
        form.addRow("username: ", self.usernameEdit)
        form.addRow("password: ", self.passwordEdit)
        form.addRow("<b>token</b>", self.tokenRadioButton)
        form.addRow("token: ", self.tokenEdit)
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(form)
        self.setLayout(self.mainLayout)
        
        self.userPassRadioButton.toggle()

    def changeMode(self):
        
        if self.userPassRadioButton.isChecked():
            self.usernameEdit.setEnabled(True)
            self.passwordEdit.setEnabled(True)
            self.tokenEdit.setEnabled(False)
        elif self.tokenRadioButton.isChecked():
            self.usernameEdit.setEnabled(False)
            self.passwordEdit.setEnabled(False)
            self.tokenEdit.setEnabled(True)

    def nextId(self):

        if self.userPassRadioButton.isChecked():
            return 
        elif self.tokenRadioButton.isChecked():
            return 

class AccountTypeWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(AccountTypeWizardPage, self).__init__(
            parent,
            title="Select Account Type",
            subTitle="Select the type of account to create")
    
        self.githubRadioButton = QRadioButton("Github account")
        self.githubRadioButton.toggle()

        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.githubRadioButton)
        self.setLayout(self.mainLayout)
    
    def nextId(self):
        
        if self.githubRadioButton.isChecked():
            return 1

class userSignInWizard(QWizard):

    def __init__(self, parent=None):
        super(userSignInWizard, self).__init__(
                parent,
                windowTitle="Sign In")

        self.setPage(0, AccountTypeWizardPage())
        self.setPage(1, GithubCredentialsWizardPage())


class RepoTypeWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(RepoTypeWizardPage, self).__init__(
            parent,
            title="Select Account Type",
            subTitle="Select the type of Repo to create")
    
        self.githubRadioButton = QRadioButton("Github Repo")
        self.githubRadioButton.toggle()

        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.githubRadioButton)
        self.setLayout(self.mainLayout)
    
    def nextId(self):
        
        if self.githubRadioButton.isChecked():
            return 1

class GithubRepoWizardPage(QWizardPage):
    def __init__(self, github, parent=None):
        super(GithubRepoWizardPage, self).__init__(
            parent,
            title="Github Repository",
            subTitle="Configure the new Github repository")
        
        self.parent = parent
        self.github = github

        #  LineEdits
        self.nameEdit = QLineEdit(textChanged=self.update)
        self.descriptionEdit = QLineEdit(textChanged=self.update)
        self.privateCheckBox = QCheckBox(toggled=self.update)
        self.initCheckBox = QCheckBox(stateChanged=self.update)
        self.gitignoreComboBox = QComboBox(currentIndexChanged=self.update)
        self.gitignoreComboBox.addItem('None')
        for i in gitignore_types(self.github):
            self.gitignoreComboBox.addItem(i)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(
            'Initialize this repository with a README and .gitignore'))
        hbox.addWidget(self.initCheckBox)

        # Form 
        form = QFormLayout()
        form.addRow("Name: ", self.nameEdit)
        form.addRow("Description: ", self.descriptionEdit)
        form.addRow('Private', self.privateCheckBox)
        form.addRow(hbox)
        form.addRow('Add .gitignore', self.gitignoreComboBox)
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(form)
        self.setLayout(self.mainLayout)
    
        if not github.get_user().plan:
            self.privateCheckBox.setEnabled(False)

    def update(self):

        sender = type(self.sender()) 
        
        if self.initCheckBox.isChecked():
            self.gitignoreComboBox.setEnabled(True)
        else:
            self.gitignoreComboBox.setEnabled(False)

        self.parent.repo_details['name'] = \
                str(self.nameEdit.text())
        self.parent.repo_details['description'] = \
                str(self.descriptionEdit.text())
        self.parent.repo_details['private'] = \
                True if self.privateCheckBox.isChecked() else False
        self.parent.repo_details['init'] = \
                True if self.initCheckBox.isChecked() else False
        self.parent.repo_details['gitignore'] = \
                str(self.gitignoreComboBox.currentText())

class RepoAddWizard(QWizard):

    def __init__(self, github, parent=None):
        super(RepoAddWizard, self).__init__(
                parent,
                windowTitle="Add Repo")
        
        self.repo_details = {}

        self.setPage(0, RepoTypeWizardPage(self))
        self.setPage(1, GithubRepoWizardPage(github,self))

class user2FADialog(QDialog):
    def __init__(self, parent=None):
        super(ScriptAddDialog, self).__init__(
            parent,
            windowTitle="2FA Required")

        # Form
        self.form = QFormLayout()
        
        # ButtonBox
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            accepted=self.accept, rejected=self.reject)
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.form)
        self.mainLayout.addWidget(buttonBox)
        self.setLayout(self.mainLayout)

class repoAddDialog(QDialog):
    def __init__(self, parent=None):
        super(ScriptAddDialog, self).__init__(
            parent,
            windowTitle="Add Repo")

        # Form
        self.form = QFormLayout()
        
        # ButtonBox
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            accepted=self.accept, rejected=self.reject)
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.form)
        self.mainLayout.addWidget(buttonBox)
        self.setLayout(self.mainLayout)

class repoRemoveDialog(QDialog):
    def __init__(self, parent=None):
        super(ScriptAddDialog, self).__init__(
            parent,
            windowTitle="Remove Repo")

        # Form
        self.form = QFormLayout()
        
        # ButtonBox
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            accepted=self.accept, rejected=self.reject)
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.form)
        self.mainLayout.addWidget(buttonBox)
        self.setLayout(self.mainLayout)

def main():
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
