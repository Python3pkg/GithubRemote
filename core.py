#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from github import Github
from github import MainClass
from github.Requester import Requester
import re
import argparse

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

    status, header, message = requester.requestJson(
            "POST", "/authorizations", 
            input={"scopes": scopes, "note": str(user_agent)},
            headers=request_header)

    if status == 401 and re.match(r'.*required.*', header['x-github-otp']):
        raise Require2FAError()
    else:
        return status, header, message
