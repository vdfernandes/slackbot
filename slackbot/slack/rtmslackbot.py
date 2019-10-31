#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from socket import error as SocketError
from slackclient import SlackClient
from websocket._exceptions import WebSocketConnectionClosedException

from slackbot.slack import TOKEN
from slackbot.slack.methods import get_message
from slackbot.slack.slackbot import SlackBot
from slackbot.slack.slackcommand import SlackCommand
from slackbot.slack.exception import RTMNotConnect, RTMConnectionLost
from slackbot.utils import getenv

# Variáveis de ambiente
SLACK_CHANNEL = getenv('SLACK_CHANNEL')
ECHO_COMMAND = getenv('RTM_STATUS')
ECHO_SUBTYPE = ['file_share', 'file_comment', 'none']


class RTMSlackBot(SlackBot):
    """
    Classe de RealTimeMessage
    """
    def __init__(self, channel=None, text=None, logger=None):
        SlackBot.__init__(self, channel, text, logger)
        self._client = SlackClient(TOKEN)
        self.connected = False

    def connect(self, retry=1):
        """
        Conexão com a RTM API (Retry = -1 para retry infinito)
        """
        if retry == -1:
            while not self.connected:
                self.logger.info("Trying...")
                self.connected = self._client.rtm_connect()
        else:
            for i in range(0, retry):
                self.logger.info("Trying...")
                self.connected = self._client.rtm_connect()
                if self.connected:
                    break

        if not self.connected:
            raise RTMNotConnect("Impossível se conectar a API RTM")

    def read(self):
        """
        Lê uma mensagem vinda do Slack
        """
        try:
            data = self._client.rtm_read()
        except (WebSocketConnectionClosedException, SocketError) as e:
            raise RTMConnectionLost("Conexão com slack perdida: {}".format(e))
        return data

    def bulk_read(self):
        """
        Lê uma série de mensagens até um retorno vazio
        """
        messages = []
        while True:
            data = self.read()
            if data:
                messages.append(data[0])
            else:
                break
        if messages:
            self.logger.log(5, "Bulk Read: {}".format(messages))
        return messages

    def read_commands(self):
        """
        Retorna os comandos parseados
        """
        at_bot = "<@{}>".format(self.bot_id)
        re_botid = re.compile(r'(^|\n){}'.format(at_bot))
        datalist = self.bulk_read()
        commands = []

        def handle_thread(thread):
            """
            Return a dict with thread info
            """
            dthread = dict(
                thread_ts=thread.get('ts'),
                thread_from=thread.get('user'),
                thread_text=thread.get('text')
            )
            self.logger.debug("dthread: {}".format(dthread))
            return dthread

        def handle_message(msg):
            text = msg.get('text')
            try:
                cmdline = text.split(at_bot)[1].strip().split('\n')[0] # Comando                
                cmd_text = "\n".join(text.split(at_bot)[1].split('\n')[1:]) # Abaixo do comando
            except IndexError:
                cmdline = text.split('\n')[0].strip()
                cmd_text = "\n".join(text.split('\n')[0].split('\n')[1:])

            # Parseamento
            cmd = cmdline.split(' ')[0].strip()
            re_wspaces = re.compile(r'[\s]*')
            arguments = re_wspaces.split(cmdline.strip())[1:]

            message = dict(
                channel=msg.get('channel'),
                ts=msg.get('ts'),
                from_user=msg.get('user'),
                text=text,
                command=cmd,
                arguments=arguments,
                cmd_text=cmd_text,
                raw=msg
            )
            self.logger.debug("Message: {}".format(message))

            # Se a mensagem é em uma thread, busca informações da thread
            if msg.get('thread_ts'):
                thread_ts = msg.get('thread_ts')
                ch = msg.get('channel')
                dt = get_message(channel=ch, ts=thread_ts)
                if dt:
                    dthread = handle_thread(thread=dt)
                    message.update(dthread)
                    self.logger.debug("Message + Thread: {}".format(message))
                else:
                    self.logger.error("Thread não localizada.")

            return message

        while True:
            try:
                data = datalist.pop(0)
                # full_message = data.get('message').get('text')                
                is_message = True if data.get('type') == 'message' else False
                is_bot = True if data.get('bot_id') else False
                if is_message and not is_bot and data.get('text'):
                    msg_text = data.get('text')
                    # if data.get('channel').startswith('D') or re_botid.search(msg_text):
                    if data.get('channel') == SLACK_CHANNEL:
                        dict_cmd = handle_message(msg=data)
                        commands.append(SlackCommand(logger=self.logger, **dict_cmd))
            except IndexError:
                break

        return commands
