#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import logging
from copy import copy

from slackbot.slack import BOT_ID
from slackbot.slack.methods import chat_post_message


class SlackBot(object):
    """
    Classe inicial de instanciamento do Slack
    """
    def __init__(self, channel=None, text=None, logger=None):
        self.channel = channel
        self.bot_id = BOT_ID
        self.text = text
        self.thread_ts = None
        self.attachments = None
        self.broadcast = False
        self.logger = logger or logging.getLogger(__name__)
        self._except_queue = None
        self._send_error = False
        self._with_errors = False

    def attach(self, a):
        """
        Adiciona os anexos ja em formato JSON
        """
        if not self.attachments:
            self.attachments = []
        self.attachments.append(a.to_json())

    def get_attachments(self):
        """
        Retorna lista de anexos no format JSON, que e reconhecida pela api chat.PostMessage
        """
        if self.attachments:
            pre_format = ", ".join(self.attachments)
            attach_list_json = "{0} {1} {2}".format("[", pre_format, "]")
            return attach_list_json
        else:
            return None

    def _add_except(self):
        """
        Adiciona instance da propria classe, na fila de exceções
        """
        if not self._except_queue:
            self._except_queue = []
        m = copy(self)
        m._except_queue = None
        m._send_error = True
        m.text = "Mensagem de `{0}` \n>{1}".format(time.asctime(), m.text)
        self._except_queue.append(m)
        self._with_errors = True

    def run_except_queue(self):
        there_msg = True
        while there_msg:
            try:
                self.logger.debug("Inicio de tentativas, {0} mensagens".format(
                    len(self._except_queue))
                )
                i = self._except_queue.pop(0)
                i.send()
                self.logger.debug("Mensagem enfileirada enviada com sucesso.")
                self.logger.debug("Realizada remoção.")
                self.logger.debug("Fim de tentativas, {0} mensagens".format(len(self._except_queue)))
                time.sleep(2)
            except IndexError:
                there_msg = False
                break
            except:
                self.logger.warning("Impossível reenviar mensagem para o Slack.")
                self._except_queue.insert(0, i)
                break
        self._with_errors = False

    def start_thread(self):
        """
        Inicia uma nova thread, alimentando o atributo thread_ts
        """
        try:
            response = chat_post_message(
                channel_id=self.channel,
                message=self.text,
                attachments=self.get_attachments())
            if response.get('ok'):
                self.thread_ts = response.get('message').get('ts')
                self.logger.debug("Thread {0} iniciada".format(self.thread_ts))
                self.attachments = None
            else:
                self.logger.error('Erro ao iniciar thread: {0}'.format(response))
                raise Exception(
                    'Erro ao iniciar thread',
                    'Response retornou ok != True: {0}'.format(response)
                )
        except Exception as e:
            self.logger.error("Erro ao iniciar thread: {0}".format(e))
            raise

    def send(self, text=None, broadcast=False):
        """
        Envia mensagem utilizando como parâmetro os valores da instância
        """
        self.logger.debug("Iniciando envio de mensagem para o Slack.")
        try:
            if text:
                self.text = text
            if broadcast:
                self.broadcast = broadcast

            response = chat_post_message(
                channel_id=self.channel, message=self.text,
                attachments=self.get_attachments(),
                thread_id=self.thread_ts,
                thread_reply_broadcast=self.broadcast)

            self.text = None
            if self.attachments:
                self.attachments = None

            if broadcast:
                self.broadcast = False

            if response.get('ok'):
                self.logger.debug("Mensagem enviada: {0}".format(self.text))
            else:
                self.logger.error('Erro ao enviar mensagem: {0}'.format(response))
                raise Exception(
                    'Erro ao iniciar thread',
                    'Response retornou ok != True: {0}'.format(response)
                )
        except Exception as e:
            if not self._send_error:
                self.logger.warning(
                    "\r\n".join([
                        "Erro ao requisitar a api chat.PostMessage.",
                        "Adicionando a mensagem na fila de exceções.",
                        "Exception: {}".format(e)
                    ])
                )
                self._add_except()
            else:
                raise
