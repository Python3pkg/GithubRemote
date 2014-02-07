#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014, Cameron White
import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="GithubRemote",
        version='0.1.0',
        description="Access remote github repos",
        license="BSD",
        author="Cameron Brandon White",
        author_email="cameronbwhite90@gmail.com",
        url="https://github.com/cameronbwhite/GithubRemote",
        provides=[
            "GithubRemote",
        ],
        packages=[
            "GithubRemote",
            "GithubRemote.Gui",
        ],
        scripts = [
            "githubremote-qt",
            "githubremote"
        ],
        package_data={
            'GithubRemote': ["LICENSE", "README.md"],
            'GithubRemote.Gui.Images': [
                'git.png', 'book_16.png', 'book_32.png',
                'book_fork_16.png', 'star_16.png', 'star_32.png',
                'fork_16.png', 'eye_16.png', 'plus_48.png',
                'minus.png', 'refresh.png',
            ]
        },
        install_requires=[
            'PyGithub',
        ],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "License :: OSI Approved :: BSD License",
            "Intended Audience :: End Users/Desktop",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
        ],
        include_package_data=True,
    )
