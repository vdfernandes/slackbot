#!/usr/bin/python
# -*- coding: utf-8 -*-

from websocket._exceptions import WebSocketConnectionClosedException as WSocketError
import re
from socket import error as SocketError
from slackclient import SlackClient

from ..slack import TOKEN
from ..slack.methods import get_message  # , for_humans_text
from ..slack.slackbot import SlackBot
from ..slack.slackcommand import SlackCommand
from ..slack.exception import RTMNotConnect, RTMConnectionLost

from ..utils import getenv

ECHO_COMMAND = getenv('RTM_STATUS')
ECHO_SUBTYPE = ['file_share', 'file_comment', 'none']


class RTMSlackBot(SlackBot):
    """ Class for RealTimeMessage """
    def __init__(self, channel=None, text=None, logger=None):
        SlackBot.__init__(self, channel, text, logger)
        self._client = SlackClient(TOKEN)
        self.connected = False

    def connect(self, retry=1):
        """ Connect to RTM api. Retry = -1 to infinite retrys """
        if retry == -1:
            while not self.connected:
                self.logger.info("trying...")
                self.connected = self._client.rtm_connect()
        else:
            for i in range(0, retry):
                self.logger.info("trying...")
                self.connected = self._client.rtm_connect()
                if self.connected:
                    break

        if not self.connected:
            raise RTMNotConnect("Impossível se conectar a api RTM")

    def read(self):
        """ Read a message from slack """
        try:
            data = self._client.rtm_read()
        except (WSocketError, SocketError) as e:
            raise RTMConnectionLost("Conexão com slack perdida: {}".format(e))
        return data

    def bulk_read(self):
        """ Read a serie of messages until an empty return """
        messages = []
        while True:
            data = self.read()
            if data:
                messages.append(data[0])
            else:
                break
        if messages:
            self.logger.log(5, "bulk_read: {}".format(messages))
        return messages

    def read_commands(self):
        """ Return parsed commands """
        at_bot = "<@{}>".format(self.bot_id)
        re_botid = re.compile(r'(^|\n){}'.format(at_bot))
        datalist = self.bulk_read()
        commands = []

        def handle_thread(thread):
            """ Return a dict with thread info """
            dthread = dict(
                thread_ts=thread.get('ts'),
                thread_from=thread.get('user'),
                thread_text=thread.get('text')
                #  thread_text=for_humans_text(thread.get('text'))
            )
            self.logger.debug("dthread: {}".format(dthread))
            return dthread

        def handle_message(msg):
            text = msg.get('text')
            # se for chamado via mensagem direta, irá dar erro no split
            try:
                # captura a linha de comando
                cmdline = text.split(at_bot)[1].strip().split('\n')[0]
                # captura as linhas abaixo do comando
                cmd_text = "\n".join(text.split(at_bot)[1].split('\n')[1:])
            except IndexError:
                cmdline = text.split('\n')[0].strip()
                cmd_text = "\n".join(text.split('\n')[0].split('\n')[1:])

            cmd = cmdline.split(' ')[0].strip()

            # arguments = cmdline.strip().split(' ')[1:]
            re_wspaces = re.compile(r'[\s]*')
            arguments = re_wspaces.split(cmdline.strip())[1:]

            dmessage = dict(
                channel=msg.get('channel'),
                ts=msg.get('ts'),
                from_user=msg.get('user'),
                text=text,
                # text=for_humans_text(text),
                command=cmd,
                arguments=arguments,
                cmd_text=cmd_text,
                # cmd_text=for_humans_text(cmd_text),
                raw=msg
            )
            self.logger.debug("dmessage: {}".format(dmessage))

            # se, mensagem e em uma thread, busca informcoes da thread
            if msg.get('thread_ts'):

                thread_ts = msg.get('thread_ts')
                ch = msg.get('channel')
                dt = get_message(channel=ch, ts=thread_ts)
                # se retornou infos da thread, incrementa dmessage
                if dt:
                    dthread = handle_thread(thread=dt)
                    dmessage.update(dthread)
                    self.logger.debug("dmessage + dthread: {}".format(dmessage))
                else:
                    self.logger.error("threah nao localizada")

            return dmessage

        while True:
            try:
                data = datalist.pop(0)
                # if tipo = mensagem e não venha de um bot e contenha texto
                if data.get('type') == 'message' and \
                   not data.get('bot_id') and \
                   data.get('text'):

                    msg_text = data.get('text')
                    # if data.get('channel').startswith('D') or at_bot in msg_text:
                    if data.get('channel').startswith('D') or \
                       re_botid.search(msg_text):
                        dict_cmd = handle_message(msg=data)
                        commands.append(
                            SlackCommand(logger=self.logger, **dict_cmd))
                    elif ECHO_COMMAND and not data.get('thread_ts') and \
                            data.get('subtype', 'none') in ECHO_SUBTYPE:
                        dict_cmd = handle_message(msg=data)
                        dict_cmd['command'] = 'echo'
                        commands.append(
                            SlackCommand(logger=self.logger, **dict_cmd))
            except IndexError:
                break

        return commands
