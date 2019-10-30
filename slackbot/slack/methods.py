#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import logging
from functools import reduce
from slackclient import SlackClient
from slackbot.utils import getenv

TOKEN = getenv('SLACK_TOKEN')
DOMAIN = getenv('SLACK_DOMAIN')

slack_cli = SlackClient(TOKEN)


def chat_post_message(
        channel_id,
        message,
        attachments=None,
        thread_id=None,
        thread_reply_broadcast=False
    ):
    logger = logging.getLogger(__name__)
    logger.debug("Realizando chamada para a API: chat.PostMessage")

    # Argumentos Fixos
    pm_args = dict(
        channel=channel_id,
        as_user=True,
        reply_broadcast=thread_reply_broadcast
    )

    # Argumentos Opcionais
    if message:
        pm_args['text'] = message
    if attachments:
        pm_args['attachments'] = attachments
    if thread_id:
        pm_args['thread_ts'] = thread_id

    response = slack_cli.api_call("chat.postMessage", **pm_args)
    return response


def list_channels():
    """
    Relaciona canais disponíveis
    """
    channels_call = slack_cli.api_call("channels.list")
    if channels_call.get('ok'):
        return channels_call['channels']
    return None


def list_private_channels():
    """
    Relaciona canais privados disponíveis
    """
    channels_call = slack_cli.api_call("groups.list")
    if channels_call['ok']:
        return channels_call['groups']
    return None


def list_users():
    """
    Relaciona usuários disponíveis
    """
    users_call = slack_cli.api_call("users.list")
    if users_call['ok']:
        return users_call['members']
    return None


def user_info(user):
    """
    Relaciona dados de um usuário
    """
    return slack_cli.api_call("users.info", user=user)


def channel_info(channel):
    """
    Relaciona dados de um canal
    """
    return slack_cli.api_call("channels.info", channel=channel)


def group_info(channel):
    """
    Relaciona dados de um grupo de usuários
    """
    return slack_cli.api_call("groups.info", channel=channel)


def get_message(channel, ts):
    """
    Busca mensagens
    """
    response = slack_cli.api_call(
        "channels.history",
        channel=channel,
        latest=ts,
        count=1,
        inclusive=True)
    if response.get('ok'):
        msg = response.get('messages')[0]
    else:
        msg = None
    return msg


def message_permalink(channel, ts):
    """
    Busca link direto de mensagens
    """
    permalink = "{}/archives/{}/p{}".format(
        DOMAIN,
        channel,
        ts.replace('.', '')
    )
    return permalink


def find_id(type, name):
    """
    Relaciona ID de um usuário ou canal
    """
    if type == 'channel':
        x = list_channels()
        for channel in x:
            if channel.get('name') == name:
                # print("Channel name: {0} ID: {1}".format(
                #     channel['name'], channel['id']))
                return channel.get('id')
    elif type == 'priv_channel':
        x = list_private_channels()
        for channel in x:
            if channel.get('name') == name:
                # print("Channel name: {0} ID: {1}".format(
                #     channel['name'], channel['id']))
                return channel.get('id')
    elif type == 'user':
        x = list_users()
        for user in x:
            if user.get('name') == name:
                # print("Channel name: {0} ID: {1}".format(
                #     user['name'], user['id']))
                return user.get('id')
    else:
        return None


def for_humans_text(text):
    """
    Processador de mensagens para leitura
    """
    # regex for users mentions
    re_atuser = re.compile(r'<@[A-Z0-9]*>')

    # regex for mentions in general (@channel, @here, @group)
    re_mention = re.compile(r'<![\w]*[\^]*[A-Z0-9]*\|@[\w-]*>')

    # regex for mention name (into a mention)
    re_human_mention = re.compile(r'@[\w-]*')

    # regex for mentions for channels (#channel_name)
    re_sharp_channel = re.compile(r'<#[A-Z0-9]*\|[a-zA-Z0-9_-]*>')

    # regex for mention name (into a mention)
    re_chhuman_mention = re.compile(r'\|[\w_-]*')
    dict_replace = dict()

    # add mentions to dict replace
    mentions = list(set(re_mention.findall(text)))
    for m in mentions:
        dict_replace[m] = re_human_mention.findall(m)[0]

    # add users to dict_replace
    users = list(set(re_atuser.findall(text)))
    tbl = {ord('<'): '', ord('>'): '', ord('@'): ''}
    for u in users:
        user_id = u.translate(tbl)
        user_name = "@{}".format(user_info(user_id).get('user').get('name'))
        dict_replace[u] = user_name

    # add channels to dict_replace
    channels = list(set(re_sharp_channel.findall(text)))
    for ch in channels:
        channel_name = re_chhuman_mention.findall(ch)[0]
        dict_replace[ch] = channel_name.replace('|', '#')

    # perform the replace of the text
    human_text = reduce(lambda x, y: x.replace(y, dict_replace[y]),
                        dict_replace, text)

    return human_text
