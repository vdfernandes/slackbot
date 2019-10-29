#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from operator import attrgetter


class Attachment(object):
    def __init__(self, fallback, title, color="#36a64f", text=None, fields=[]):
        self.fallback = fallback
        self.color = color
        self.title = title
        self.text = text
        self.fields = fields

    def to_json(self):
        return json.dumps(self, default=attrgetter("__dict__"))


class AttachmentField(object):
    def __init__(self, title, value, short=True):
        self.title = title
        self.value = value
        self.short = short
