#!/usr/bin/python
# -*- coding: utf-8 -*-
from jira.exceptions import JIRAError


class CreateIssueError(JIRAError):
    pass


class JIRAUserNotFound(JIRAError):
    pass


class AssignError(JIRAError):
    pass
