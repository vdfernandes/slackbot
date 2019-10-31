#!/usr/bin/python
# -*- coding: utf-8 -*-
from slackbot.utils import getenv

DOMAIN = getenv('SLACK_DOMAIN')
TOKEN = getenv('SLACK_TOKEN')
BOT_ID = getenv('SLACK_BOT_ID')
ADMIN = ''
