#!/usr/bin/python
# -*- coding: utf-8 -*-
from jira import JIRA
from slackbot.utils import getenv

# JIRA Credentials
user = getenv('JIRA_USER')
passwd = getenv('JIRA_PASSWORD')
server = getenv('JIRA_SERVER')

# JIRA Client
client = JIRA(
    server=server,
    basic_auth=(
        user,
        passwd
    )
)
