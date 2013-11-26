from github import Github
from github import MainClass
from github.Requester import Requester
import re
import argparse
import json
import getpass
import os

class Require2FAError(Exception):
    pass

PARSER = argparse.ArgumentParser(description="Control remote git repos")

PARSER.add_argument('--username', '-u', type=str)
PARSER.add_argument('--password', '-p', type=str)
PARSER.add_argument('host', choices=['github'], type=str)

SUBPARSER = PARSER.add_subparsers()

SUBPARSER_LIST = SUBPARSER.add_parser('list')

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
