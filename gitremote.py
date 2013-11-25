from github import Github
from github import MainClass
from github.Requester import Requester
import re
import argparse

PARSER = argparse.ArgumentParser(description="Control remote git repos")

PARSER.add_argument('--username', '-u', type=str)
PARSER.add_argument('--password', '-p', type=str)
PARSER.add_argument('host', choices=['github'], type=str)

SUBPARSER = PARSER.add_subparsers()

SUBPARSER_LIST = SUBPARSER.add_parser('list')

if __name__ == '__main__':
    ARGS = PARSER.parse_args()

class Require2FAError(Exception):
    pass

def request_token(username, password, 
        scopes, user_agent, code_2fa=None,
        base_url=MainClass.DEFAULT_BASE_URL, 
        timeout=MainClass.DEFAULT_TIMEOUT, 
        client_id=None,
        client_secret=None,
        per_page=MainClass.DEFAULT_PER_PAGE):
    requester = Requester(username, password, base_url, timeout,
            client_id, client_secret, user_agent, per_page)
    request_header = None
    if code_2fa:
        request_header = {'x-github-otp': code_2fa}
    status, header, message = requester.requestJson(
            "POST", "/authorizations", 
            {"scopes":scopes, "note": str(user_agent)},
            request_header)
    if status == 401 and re.match(r'.*required.*', header['x-github-otp']):
        raise Require2FAError()
    else:
        return message
