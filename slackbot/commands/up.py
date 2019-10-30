#!/usr/bin/python
# -*- coding: utf-8 -*-
from slackbot.utils import getenv
from slackbot.models import Session
from slackbot.models.card import Card
from slackbot.jira.methods import comment_issue
from slackbot.slack.methods import user_info
from slackbot.slack.slackcommand import (
    SlackCommand,
    CmdArgumentParser,
    handle_exceptions
)


class UP(SlackCommand):
    session = Session()

    @handle_exceptions
    def run(self):
        """
        Método de execução das ações da classe
        """
        try:
            pointed_msg = self._get_pointed_up_message()
            pointed_user = pointed_msg.get('user')
            user = user_info(pointed_user).get('user').get('name')
            text = "*{}:* {}".format(user, pointed_msg.get('text'))
        except Exception as e:
            text = "Ops, parece não ter nenhuma mensagem acima dessa. :{}:".format(
                getenv('REACTION_SURPRISE', 'thinking_face')
            )        
        self.text = text 
        self.send()  
