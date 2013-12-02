#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from github import MainClass
from github.Authorization import Authorization
from github.Requester import Requester
import re
import argparse
import json

class Require2FAError(Exception):
    pass

class AuthenticationError(Exception):
    pass

def request_token(
        username, password, scopes, user_agent, code_2fa=None,
        base_url=MainClass.DEFAULT_BASE_URL, 
        timeout=MainClass.DEFAULT_TIMEOUT, 
        client_id=None, client_secret=None,
        per_page=MainClass.DEFAULT_PER_PAGE):
    
    requester = Requester(username, password, base_url, timeout,
            client_id, client_secret, user_agent, per_page)

    if code_2fa:
        request_header = {'x-github-otp': code_2fa}
    else:
        request_header = None
     
    status, headers, data = requester.requestJson(
            "POST", "/authorizations", 
            input={"scopes": scopes, "note": str(user_agent)},
            headers=request_header)
    
    try: 
        if status == 401 and re.match(r'.*required.*', headers['x-github-otp']):
            raise Require2FAError()
        else:
            data = json.loads(data)
            return Authorization(requester, headers, data, True)
    except KeyError:
        raise AuthenticationError()

def store_token(file_path, token):
    
    with open(file_path, 'w+') as f:
        json.dump({'token':token}, f)

def load_token(file_path):

    with open(file_path, 'r') as f:
        try: 
            return json.load(f)['token']
        except KeyError:
            return None

def gitignore_types(github):
    for i in github.get_user('github')\
                   .get_repo('gitignore')\
                   .get_git_tree('master')\
                   .tree:
        t = re.split('.gitignore', i.path)
        if t[0] is not '':
            yield t[0]