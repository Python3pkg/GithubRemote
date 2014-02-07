#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from ..tools import gitignore_types
from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QWizardPage, QWizard, QRadioButton, QLineEdit, \
    QRegExpValidator, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QWidget, QSizePolicy, QCheckBox, QComboBox, QFormLayout

class RepoTypeWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(RepoTypeWizardPage, self).__init__(
            parent,
            title="Select Account Type",
            subTitle="Select the type of Repo to create")
        
        # RadioButtons

        self.githubRadioButton = QRadioButton('Github Repo')

        # Layout

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.githubRadioButton)
        self.setLayout(self.mainLayout)
        
        # Setup

        self.githubRadioButton.toggle() 
    
    def nextId(self):
        
        if self.githubRadioButton.isChecked():
            return 1

class GithubRepoWizardPage(QWizardPage):
    def __init__(self, github, parent=None):
        super(GithubRepoWizardPage, self).__init__(
            parent,
            title="Github Repository",
            subTitle="Configure the new Github repository")
        
        self.github = github
        
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
        
        # gitignoreComboBox

        self.gitignoreComboBox = QComboBox(currentIndexChanged=self.update)
        self.gitignoreComboBox.addItem('None')
        for i in gitignore_types(self.github):
            self.gitignoreComboBox.addItem(i)
            
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel(
            'Initialize this repository with a README and .gitignore'))
        hbox2.addWidget(self.initCheckBox)
        
        # Extension Form

        self.form_extension = QFormLayout()
        self.form_extension.addRow("Homepage", self.homepageEdit)  
        self.form_extension.addRow("Has wiki", self.hasWikiCheckBox)
        self.form_extension.addRow("Has issues", self.hasIssuesCheckBox)
        self.form_extension.addRow("Has downloads", self.hasDownloadsCheckBox)

        # Extension

        self.extension = QWidget()
        self.extension.setLayout(self.form_extension)

        # Form

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
        
        # Setup

        self.hasWikiCheckBox.toggle()
        self.hasDownloadsCheckBox.toggle()
        self.hasIssuesCheckBox.toggle()
        if not self.github.get_user().plan:
            self.privateCheckBox.setEnabled(False)
        
        self.extension.hide()

    def update(self):

        if self.initCheckBox.isChecked():
            self.gitignoreComboBox.setEnabled(True)
        else:
            self.gitignoreComboBox.setEnabled(False)

    def more(self):
            
        if self.moreButton.isChecked():
            self.moreButton.setText("Less")
            self.extension.show()
            self.wizard().resize(self.wizard().sizeHint())
        else:
            self.moreButton.setText("More")
            self.extension.hide()
            size = self.sizeHint()
            wizard_size = self.wizard().sizeHint()
            self.wizard().resize(wizard_size.width(), size.height())

class AddRepoWizard(QWizard):

    def __init__(self, github, parent=None):
        super(AddRepoWizard, self).__init__(
                parent,
                windowTitle="Add Repo")
        
        self.setPage(0, RepoTypeWizardPage(self))
        self.setPage(1, GithubRepoWizardPage(github, self))
