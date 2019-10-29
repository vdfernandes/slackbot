#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String
from slackbot.models import Model


class Card(Model):
    __tablename__ = 'mag_t_card'

    slack_ts = Column(String(30), primary_key=True)
    jira_issue = Column(String(30))
    status = Column(String(20))
    channel = Column(String(100))
    requester = Column(String(100))
    executor = Column(String(100))

    def __repr__(self):
        return "<Card: {}>".format(self.__str__())

    def __str__(self):
        return "slack_ts: {} jira_issue: {}".format(
            self.slack_ts, self.jira_issue)
