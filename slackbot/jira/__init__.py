#!/usr/bin/python
# -*- coding: utf-8 -*-
from jira import JIRA
from ..utils import getenv

# load credentials
user = getenv('JIRA_USER')
passwd = getenv('JIRA_PASSWORD')
server = getenv('JIRA_SERVER')

# instantiate jira client
client = JIRA(server=server, basic_auth=(user, passwd))
