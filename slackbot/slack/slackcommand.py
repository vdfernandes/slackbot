#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from slackbot.slack.slackbot import SlackBot
from slackbot.slack.exception import CommandNotImplemented, PlannedException
from slackbot.slack.methods import for_humans_text, get_message
from slackbot.jira.exception import (
    JIRAError,
    CreateIssueError,
    JIRAUserNotFound,
    AssignError
)


class SlackCommand(SlackBot):
    """
    Classe de comandos Slack
    """
    def __init__(self, logger=None, **kwargs):
        SlackBot.__init__(self, channel=kwargs.get('channel'), logger=logger)

        self.msg_channel = kwargs.get('channel')
        self.msg_ts = kwargs.get('ts')
        self.msg_from = kwargs.get('from_user')
        self.msg_text = kwargs.get('text')
        self.mthread_ts = kwargs.get('thread_ts')
        self.mthread_from = kwargs.get('thread_from')
        self.mthread_text = kwargs.get('thread_text')
        self.command = kwargs.get('command')
        self.arguments = kwargs.get('arguments')
        self.cmd_text = kwargs.get('cmd_text')
        self.raw = kwargs.get('raw')

        if kwargs.get('thread_ts'):
            self.thread_ts = kwargs.get('thread_ts')
        elif self.channel.startswith('D'):
            self.thread_ts = None
        else:
            self.thread_ts = kwargs.get('ts')

    def _get_pointed_up_message(self):
        """
        Busca a mensagem acima à mensagem de solicitação do bot.
        """
        replies = get_message(self.channel, self.thread_ts).get('replies')
        '''
        quantity = len(replies)
        for x in range(quantity):
            pointed = replies[x].get('ts')
            message = get_message(channel=self.channel, ts=pointed) 
            self.text = message.get('text')
            self.send()
        '''            
        pos = len(replies) - 2
        ts_pointed = replies[pos].get('ts')
        return get_message(channel=self.channel, ts=ts_pointed)      

    def __str__(self):
        s = "Channel: {}, TS: {}, From: {}, Command: {}, Text: {}".format(
            self.msg_channel,
            self.msg_ts,
            self.msg_from,
            self.command,
            self.msg_text
        )
        if self.mthread_ts:
            s = "{}, TS: {}, Thread From: {}".format(
                s,
                self.mthread_ts,
                self.mthread_from
            )
        return s

    def __repr__(self):
        return "<SlackCommand: {} >".format(self.__str__())

    def run(self):
        raise CommandNotImplemented(
            "This method (run) needs to be implemented by {}".format(self)
        )


class ArgumentParserError(Exception):
    pass


class CmdArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


def handle_exceptions(f):
    def wrapper(*args, **kw):
        self = args[0]
        try:
            return f(*args, **kw)
        except ArgumentParserError:
            self.logger.info(
                "Parâmetros não reconhecidos. Comando: {}, Argumentos: {}".format(
                    self.command,
                    self.arguments
                )
            )
            msg = "Parâmetros não reconhecidos para o comando `{}`\n```{}```".format(
                self.command,
                self.usage
            )
            self.send(text=msg)
        except PlannedException as err:
            self.logger.error("Error in {} run(). Error: {}".format(
                self.__class__, err))
        except (
            JIRAError,
            CreateIssueError,
            JIRAUserNotFound,
            AssignError
        ) as err:
            self.logger.error(
                "Error in {} run(). Error: {}".format(
                    self.__class__,
                    err
                )
            )
            self.send(
                text="\n".join([
                    "Ops, alguma coisa errada não está certa! :bomb:",
                    "`Erro na requisição à api do JIRA`"
                ])
            )
        except Exception as err:
            self.logger.error(
                "Error in {} run(). Error: {}".format(
                    self.__class__,
                    err
                )
            )
            self.send(
                text="\n".join([
                    "Ops, alguma coisa errada não está certa! :bomb:",
                    "`Impossivel processar o comando.`"
                ])
            )
    return wrapper
