#!/usr/bin/python
# -*- coding: utf-8 -*-
from slackbot.slack.slackcommand import SlackCommand
from slackbot.utils import getenv


class Help(SlackCommand):
    """
    Responde com uma mensagem de ajuda
    """
    def run(self):
        msg = "\n".join([
            "-- Pendente implementação --"
        ])
        self.send(text=msg)


class NotFound(SlackCommand):
    """
    Responde com uma mensagem de erro amigável para comando não encontrado
    """
    def run(self):
        msg = "\n".join([
            "Ops! Esse comando não foi reconhecido. :{}:".format(
                getenv('REACTION_SAD', 'disappointed')
            )
        ])
        self.send(text=msg)
