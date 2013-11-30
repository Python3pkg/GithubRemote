#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from core import *
import json
import getpass
import os
import pickle

PARSER = argparse.ArgumentParser(description="Control remote git repos")

PARSER.add_argument('--username', '-u', default=None, type=str)
PARSER.add_argument('--password', '-p', default=None, type=str)
PARSER.add_argument('host', choices=['github'], type=str)

SUBPARSER = PARSER.add_subparsers()

SUBPARSER_LIST = SUBPARSER.add_parser('list')

ARGS = PARSER.parse_args()

def get_token():
    try:
        f = open('authentication.pickle', 'r+')
    except IOError:
        f = open('authentication.pickle', 'w+')

    try:
        authentication = pickle.load(f)
    except EOFError:

        if not ARGS.username:
            ARGS.username = raw_input("username: ")

        if not ARGS.password:
            ARGS.password = getpass.getpass()

        try:
            authenticaiton = request_token(
                    ARGS.username, ARGS.password, ['repo'], 'TESTTEST')
            pickle.dump(authentication, f)
            return authentication
        except Require2FAError:
            pass
    
        try:
            code = raw_input("Enter code: ")
            authentication = request_token(
                    ARGS.username, ARGS.password, ['repo'], 'TESTTEST', code)
            pickle.dump(authentication, f)
            return authentication
        except None:
            return None


if __name__ == '__main__':

    get_token()

