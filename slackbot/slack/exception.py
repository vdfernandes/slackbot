#!/usr/bin/python
# -*- coding: utf-8 -*-


class RTMNotConnect(Exception):
    pass


class RTMConnectionLost(Exception):
    pass


class RTMThreadNotFound(Exception):
    pass


class CommandNotImplemented(Exception):
    pass


class PlannedException(Exception):
    pass
