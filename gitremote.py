#!/usr/bin/env python
# -*- coding: utf-9 -*-
# Copyright (C) 2013, Cameron White
from core import *
import json
import getpass
import os


PARSER = argparse.ArgumentParser(description="Control remote git repos")

PARSER.add_argument('--username', '-u', type=str)
PARSER.add_argument('--password', '-p', type=str)
PARSER.add_argument('host', choices=['github'], type=str)

SUBPARSER = PARSER.add_subparsers()

SUBPARSER_LIST = SUBPARSER.add_parser('list')


if __name__ == '__main__':

    ARGS = PARSER.parse_args()

    if not ARGS.username:
        ARGS.username = input("username: ")
    
    if os.path.exists('./loggins.json'):
        loggin_info = open('./loggins.json', 'r+')    
    else:
        loggin_info = open('./loggins.json', 'w+')    
    
    try:
        loggin_info_json = json.load(loggin_info)
    except ValueError:
        loggin_info_json = json.loads('{}')
    
    try:
        token = loggin_info_json[ARGS.host][ARGS.username]['token']
    except KeyError:

        if not ARGS.password:
            ARGS.password = getpass.getpass()

        try:
            status, header, message = request_token(
                    ARGS.username, ARGS.password, ['repo'], 'TESTTEST')

        except Require2FAError:
            code = input("Enter code: ")
            status, header, message = request_token(
                    ARGS.username, ARGS.password, ['repo'], 'TESTTEST', code)

            message_json = json.loads(message)
          
            if not ARGS.host in loggin_info_json:
                loggin_info_json[ARGS.host] = {}
            if not ARGS.username in loggin_info_json[ARGS.host]:
                loggin_info_json[ARGS.host][ARGS.username] = {}

            loggin_info_json[ARGS.host][ARGS.username]['token'] = message_json['token']

    json.dump(loggin_info_json,loggin_info)
