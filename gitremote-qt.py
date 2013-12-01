#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import pickle
import urllib

GITHUB = None

def waiting_effects(function):
    def new_function(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        function(self)
        QApplication.restoreOverrideCursor()
    return new_function

class MainWidget(QMainWindow):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(
                parent,
                windowTitle='GitRemote',
                windowIcon=QIcon('images/git.png'),
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
        self.repoRemoveAction.triggered.connect(self.repoRemove)

        self.repoRefreshAction = QAction(
                QIcon('images/refresh.png'),
                'Refresh Repos', self,
                statusTip='Refresh list of repos')
        self.repoRefreshAction.triggered.connect(self.reposRefresh)

        self.userSignInAction = QAction(
                'User Sign&in', self,
                statusTip='Sign In')
        self.userSignInAction.triggered.connect(self.userSignIn)

        self.userSignOutAction = QAction(
                'User Sign&out', self,
                statusTip='Sign Out')
        
        self.userLabel = QLabel(self)
        self.userLabel.setScaledContents(True)
        self.userLabel.setSizePolicy(
                QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.userImageLabel = QLabel(self)
        self.userImageLabel.setScaledContents(True)
        self.userLabel.setSizePolicy(
                QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.userPushButton = QPushButton(self)
        self.userPushButton.setSizePolicy(
                QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        hbox = QHBoxLayout()
        hbox.addWidget(self.userLabel)
        hbox.addWidget(self.userImageLabel)
        self.userPushButton.setLayout(hbox)

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
        self.toolBar.addWidget(self.userPushButton)

        # Menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        actionMenu = menuBar.addMenu('&Action')
        fileMenu.addAction(self.userSignInAction)
        fileMenu.addAction(self.userSignOutAction)
        actionMenu.addAction(self.repoAddAction)
        actionMenu.addAction(self.repoRemoveAction)
        actionMenu.addAction(self.repoRefreshAction)

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
        self.reposTableWidget.horizontalHeader().setStretchLastSection(True)

        # Layout
        self.setCentralWidget(self.reposTableWidget)
        self.actionsUpdate()
        self.show()
        
        self.authenticate()
        self.reposRefresh()
        self.updateImage()
        self.actionsUpdate()
        
    def updateImage(self):

        if not GITHUB:
            return
        url = GITHUB.get_user().avatar_url
        data = urllib.urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.userImageLabel.setPixmap(pixmap)
        self.userImageLabel.setFixedSize(32, 32)
        self.userLabel.setText(GITHUB.get_user().login)
        size = self.userLabel.sizeHint()
        self.userPushButton.setFixedSize(size.width() + 60, 48)
        
    
    @waiting_effects
    def reposRefresh(self):

        if not GITHUB:
            return
        repos = GITHUB.get_user().get_repos()
        self.reposTableWidget.setRowCount(GITHUB.get_user().public_repos)
        for row, repo in enumerate(repos):
            nameTableWidgetItem = QTableWidgetItem(str(repo.name))
            descTableWidgetItem = QTableWidgetItem(str(repo.description))
            self.reposTableWidget.setItem(row, 0, nameTableWidgetItem)
            self.reposTableWidget.setItem(row, 1, descTableWidgetItem)
        for i in range(self.reposTableWidget.columnCount()-1):
            self.reposTableWidget.resizeColumnToContents(i)
        self.reposTableWidget.resizeRowsToContents()

    @waiting_effects
    def authenticate(self):
        
        global GITHUB

        try:
            f = open('authentication.pickle', 'r')
            authentication = pickle.load(f)
            GITHUB = Github(authentication.token)
            f.close()
        except IOError, EOFError:
            GITHUB = None
    
    def actionsUpdate(self):
        if GITHUB is None:
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

    def userSignIn(self):
        wizard = UserSignInWizard(self)
        if wizard.exec_():
            pass
    
    def repoAdd(self):
        wizard = RepoAddWizard(self)
        if wizard.exec_():
            GITHUB.get_user().create_repo(
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
        dialog = RepoRemoveDialog(name)
        if dialog.exec_():
            GITHUB.get_user().get_repo(str(name)).delete()
            self.reposRefresh()

    def _isARepoSelected(self):
            if len(self.reposTableWidget.selectedItems()) > 0:
                return True
            else:
                return False

    def _selectedRepoRow(self):
        selectedModelIndexes = \
            self.reposTableWidget.selectionModel().selectedRows()
        for index in selectedModelIndexes:
            return index.row()

class GithubCredentialsWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(GithubCredentialsWizardPage, self).__init__(
            parent,
            title="Credentials",
            subTitle="Enter your username/password or token")
        
        self.userPassRadioButton = QRadioButton()
        self.userPassRadioButton.toggled.connect(self.changeMode)
        self.userPassRadioButton.toggled.connect(self.completeChanged.emit)
        self.tokenRadioButton = QRadioButton()
        self.tokenRadioButton.toggled.connect(self.changeMode)
        self.tokenRadioButton.toggled.connect(self.completeChanged.emit)

        #  LineEdits

        self.usernameEdit = QLineEdit(
                textChanged=self.completeChanged.emit)
        # Username may only contain alphanumeric characters or dash
        # and cannot begin with a dash
        self.usernameEdit.setValidator(
            QRegExpValidator(QRegExp('[A-Za-z\d]+[A-Za-z\d-]+')))

        # passwordEdit
        self.passwordEdit = QLineEdit(
                textChanged=self.completeChanged.emit)
        self.passwordEdit.setValidator(
            QRegExpValidator(QRegExp('.+')))
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        # token may only contain alphanumeric characters
        self.tokenEdit = QLineEdit(
                textChanged=self.completeChanged.emit)
        self.tokenEdit.setValidator(
            QRegExpValidator(QRegExp('[A-Za-z\d]+')))
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
        
        # Fields
        self.registerField("username", self.usernameEdit)
        self.registerField("password", self.passwordEdit)
        self.registerField("token", self.tokenEdit)

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
            return 2 # TODO
        elif self.tokenRadioButton.isChecked():
            return 2 # TODO
    
    def isComplete(self):
        
        if self.userPassRadioButton.isChecked():
            usernameValidator = self.usernameEdit.validator()
            usernameText = self.usernameEdit.text()
            usernameState = usernameValidator.validate(usernameText, 0)[0]
            passwordValidator = self.passwordEdit.validator()
            passwordText = self.passwordEdit.text()
            passwordState = passwordValidator.validate(passwordText, 0)[0]
            if usernameState == QValidator.Acceptable and \
                    passwordState == QValidator.Acceptable:
                return True

        elif self.tokenRadioButton.isChecked():
            tokenValidator = self.tokenEdit.validator()
            tokenText = self.tokenEdit.text()
            tokenState = tokenValidator.validate(tokenText, 0)[0]
            if tokenState == QValidator.Acceptable:
                return True

        return False

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

class Github2FAWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(Github2FAWizardPage, self).__init__(
                parent,
                title="Two-Factor Authentication",
                subTitle="Enter required authentication code")
        
        self.codeEdit = QLineEdit()
        self.codeEdit.setValidator(QRegExpValidator(QRegExp(r'[\d]+')))

        self.form = QFormLayout()
        self.form.addRow("Code: ", self.codeEdit)

        self.setLayout(self.form)

        # Fields
        self.registerField('2fa_code*', self.codeEdit)

class UserSummaryWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(UserSummaryWizardPage, self).__init__(
                parent,
                title="Summary",
                subTitle="Summary of new user account")
        
        self.usernameLabel = QLabel()

        self.form = QFormLayout()
        self.form.addRow("username: ", self.usernameLabel)

        self.setLayout(self.form)
    
    def initializePage(self):
         
        self.usernameLabel.setText(self.field('username').toString())

class UserSignInWizard(QWizard):

    def __init__(self, parent=None):
        super(UserSignInWizard, self).__init__(
                parent,
                windowTitle="Sign In")

        self.setPage(0, AccountTypeWizardPage())
        self.setPage(1, GithubCredentialsWizardPage())
        self.setPage(2, Github2FAWizardPage())
        self.setPage(3, UserSummaryWizardPage())

class RepoTypeWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(RepoTypeWizardPage, self).__init__(
            parent,
            title="Select Account Type",
            subTitle="Select the type of Repo to create")
    
        self.githubRadioButton = QRadioButton('Github Repo')

        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.githubRadioButton)
        self.setLayout(self.mainLayout)

        self.githubRadioButton.toggle()
    
    def nextId(self):
        
        if self.githubRadioButton.isChecked():
            return 1

class GithubRepoWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(GithubRepoWizardPage, self).__init__(
            parent,
            title="Github Repository",
            subTitle="Configure the new Github repository")
        
        self.parent = parent
        
        # moreButton
        self.moreButton = QPushButton(
                "More",
                checkable=True,
                clicked=self.more)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        moreButtonHBox = QHBoxLayout()
        moreButtonHBox.addWidget(spacer)
        moreButtonHBox.addWidget(self.moreButton)

        #  LineEdits
        self.nameEdit = QLineEdit(textChanged=self.update)
        self.nameEdit.setValidator(QRegExpValidator(
                QRegExp(r'[a-zA-Z0-9-_]+[a-zA-Z0-9-_]*')))
        self.descriptionEdit = QLineEdit(textChanged=self.update)
        self.homepageEdit = QLineEdit(textChanged=self.update)
        
        # CheckBox
        self.privateCheckBox = QCheckBox(stateChanged=self.update)
        self.initCheckBox = QCheckBox(stateChanged=self.update)
        self.hasWikiCheckBox = QCheckBox(stateChanged=self.update)
        self.hasDownloadsCheckBox = QCheckBox(stateChanged=self.update)
        self.hasIssuesCheckBox = QCheckBox(stateChanged=self.update)

        self.gitignoreComboBox = QComboBox(currentIndexChanged=self.update)
        self.gitignoreComboBox.addItem('None')
        for i in gitignore_types(GITHUB):
            self.gitignoreComboBox.addItem(i)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel(
            'Initialize this repository with a README and .gitignore'))
        hbox2.addWidget(self.initCheckBox)

        self.form_extension = QFormLayout()
        self.form_extension.addRow("Homepage", self.homepageEdit)  
        self.form_extension.addRow("Has wiki", self.hasWikiCheckBox)
        self.form_extension.addRow("Has issues", self.hasIssuesCheckBox)
        self.form_extension.addRow("Has downloads", self.hasDownloadsCheckBox)

        # Extension
        self.extension = QWidget()
        self.extension.setLayout(self.form_extension)

        # Form1
        self.form = QFormLayout()
        self.form.addRow("Name: ", self.nameEdit)
        self.form.addRow("Description: ", self.descriptionEdit)
        self.form.addRow('Private', self.privateCheckBox)
        self.form.addRow(hbox2)
        self.form.addRow('Add .gitignore', self.gitignoreComboBox)
        self.form.addRow(moreButtonHBox)
        self.form.addRow(self.extension)
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.form)
        self.setLayout(self.mainLayout)
    
        # Fields
        self.registerField('name*', self.nameEdit)
        self.registerField('description', self.descriptionEdit)
        self.registerField('private', self.privateCheckBox)
        self.registerField('auto_init', self.initCheckBox)
        self.registerField('gitignore', self.gitignoreComboBox, 'currentText')
        self.registerField('homepage', self.homepageEdit)
        self.registerField('has_issues', self.hasIssuesCheckBox)
        self.registerField('has_downloads', self.hasDownloadsCheckBox)
        self.registerField('has_wiki', self.hasWikiCheckBox)
        
        self.hasWikiCheckBox.toggle()
        self.hasDownloadsCheckBox.toggle()
        self.hasIssuesCheckBox.toggle()
        if not GITHUB.get_user().plan:
            self.privateCheckBox.setEnabled(False)
        
        self.extension.hide()

    def update(self):

        sender = type(self.sender()) 
        
        if self.initCheckBox.isChecked():
            self.gitignoreComboBox.setEnabled(True)
        else:
            self.gitignoreComboBox.setEnabled(False)

    def more(self):
            
        if self.moreButton.isChecked():
            self.moreButton.setText("Less")
            self.extension.show()
            self.parent.resize(self.parent.sizeHint())
        else:
            self.moreButton.setText("More")
            self.extension.hide()
            size = self.sizeHint()
            parent_size = self.parent.sizeHint()
            self.parent.resize(parent_size.width(), size.height())

class RepoAddWizard(QWizard):

    def __init__(self, parent=None):
        super(RepoAddWizard, self).__init__(
                parent,
                windowTitle="Add Repo")
        
        self.setPage(0, RepoTypeWizardPage(self))
        self.setPage(1, GithubRepoWizardPage(self))

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

class RepoRemoveDialog(QDialog):
    def __init__(self, name, parent=None):
        super(RepoRemoveDialog, self).__init__(
            parent,
            windowTitle="Remove Repo")
        
        self.login = GITHUB.get_user().login
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

def main():
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
