#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import time
from slackbot.utils import getenv
from slackbot.slack.methods import channel_info
from slackbot.slack.slackcommand import (
    SlackCommand,
    handle_exceptions
)

TARGET = getenv('ECHO_TARGET')
SOURCE_LIST = getenv('ECHO_SOURCE')


class Echo(SlackCommand):
    @handle_exceptions
    def run(self):
        """
        Processador de mensagens echoadas
        """
        self.thread_ts = None
        self.channel = TARGET
        if self.msg_channel in SOURCE_LIST:
            self._echo()

    def _echo(self):
        channel_name = channel_info(self.msg_channel).get('channel').get('name')
        if self.raw.get('subtype') == 'file_comment':
            re_url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            url = re.findall(re_url, self.msg_text)[0]
            self.msg_text = self.msg_text.replace(url, '')

        echo_fulltext = [
            "*Echo:* _Channel:_ <#{}|{}>, _User:_ <@{}>".format(
                self.msg_channel, channel_name, self.msg_from),
            self.msg_text
        ]

        self.text = "\n".join(echo_fulltext)
        time.sleep(1)
        self.send()
