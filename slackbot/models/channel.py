#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from slackbot.models import Model


class Channel(Model):
    __tablename__ = 'mag_t_channel'

    channel = Column(String(20), primary_key=True)
    project = Column(String(10))
    issuetype = Column(String(10))
    priority = Column(String(20))
    id_tr_close = Column(Integer)
    id_tr_reopen = Column(Integer)

    @property
    def priorities(self):
        aux = ChannelPriority.qry.filter(
            ChannelPriority.channel == self.channel)
        pri_list = list()
        for p in aux:
            pri_list.append(p.slack_priority)
        return pri_list

    @property
    def dict_priorities(self):
        aux = ChannelPriority.qry.filter(
            ChannelPriority.channel == self.channel)
        pri_dict = dict()
        for p in aux:
            pri_dict[p.slack_priority] = p.jira_priority
        return pri_dict

    @property
    def issue_types(self):
        aux = ChannelIssueType.qry.filter(
            ChannelIssueType.channel == self.channel)
        itypes_list = list()
        for p in aux:
            itypes_list.append(p.slack_issuetype)
        return itypes_list

    @property
    def dict_issuetypes(self):
        aux = ChannelIssueType.qry.filter(
            ChannelIssueType.channel == self.channel)
        itypes_dict = dict()
        for p in aux:
            itypes_dict[p.slack_issuetype] = p.jira_issuetype
        return itypes_dict

    def find(self, channel):
        return self.sess.query(Channel).filter_by(channel=channel).first()

    def __repr__(self):
        return "<{} >".format(self.__str__)

    def __str__(self):
        return "Channel chn: {}".format(self.channel)


class ChannelPriority(Model):
    __tablename__ = 'mag_t_channel_priority'

    channel = Column(String(20), primary_key=True)
    slack_priority = Column(String(20), primary_key=True)
    jira_priority = Column(String(20))

    def find(self, channel):
        return self.sess.query(ChannelPriority).filter_by(channel=channel)

    def __repr__(self):
        return "<{} >".format(self.__str__)

    def __str__(self):
        return "ChannelPriority= chn: {} slack_pri: {} jira_pri: {}".format(
            self.channel, self.slack_priority, self.jira_priority)


class ChannelIssueType(Model):
    __tablename__ = 'mag_t_channel_issuetype'

    channel = Column(String(20), primary_key=True)
    slack_issuetype = Column(String(20), primary_key=True)
    jira_issuetype = Column(String(20))

    def find(self, channel):
        return self.sess.query(ChannelIssueType).filter_by(channel=channel)

    def __repr__(self):
        return "<{} >".format(self.__str__)

    def __str__(self):
        return "ChannelIssueType= chn: {} " \
               "slack_issuetype: {} jira_issuetype: {}" \
               "".format(self.channel, self.slack_issuetype, self.jira_issuetype)
