#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import pickle

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
        self.userSignInAction.triggered.connect(self.userSignIn)

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
        self.reposTableWidgetHeaders = ["Name"]
        self.reposTableWidget = QTableWidget(0,
                len(self.reposTableWidgetHeaders),
                selectionBehavior = QAbstractItemView.SelectRows,
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

    def reposRefresh(self):

        if not self.github:
            return
        repos = self.github.get_user().get_repos()
        self.reposTableWidget.setRowCount(self.github.get_user().public_repos)
        for row, repo in enumerate(repos):
            nameTableWidgetItem = QTableWidgetItem(str(repo.name))
            self.reposTableWidget.setItem(row, 0, nameTableWidgetItem)
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
