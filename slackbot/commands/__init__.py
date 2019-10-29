#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

from slackbot.slack.slackcommand import SlackCommand


class Help(SlackCommand):
    """ Answer a message with bot help """
    def run(self):
        msg = "\n".join([
            "-- Pendente implementação --"
        ])
        self.send(text=msg)


class NotFound(SlackCommand):
    """ Answer a message with bot help """
    def run(self):
        msg = "\n".join([
            "Comando não reconhecido"
        ])
        self.send(text=msg)
