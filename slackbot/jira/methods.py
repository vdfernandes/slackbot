#!/usr/bin/python
# -*- coding: utf-8 -*-
from ..jira import client
from ..jira.exception import (
    CreateIssueError,
    JIRAError,
    JIRAUserNotFound,
    AssignError
)


def open_issue(project, summary, text, issue_type, priority=None):
    try:
        issue_dict = dict(
            project=project,
            summary=summary,
            description=text,
            issuetype=issue_type
        )
        if priority:
            issue_dict['priority'] = {'name': priority}

        issue = client.create_issue(fields=issue_dict)
        return issue
    except JIRAError as e:
        raise CreateIssueError("JIRAError ao criar Issue {}".format(e))
    except Exception as e:
        raise CreateIssueError("Erro inesperado ao criar Issue {}".format(e))


def get_issue(id_issue, fields=None):
    if not fields:
        fields = 'creator', \
                 'description', \
                 'issuetype', \
                 'priority', \
                 'project', \
                 'reporter', \
                 'resolution', \
                 'resolutiondate', \
                 'status', \
                 'summary', \
                 'watches'

    return client.issue(id_issue, fields)


def comment_issue(issue_id, comment):
    issue = get_issue(issue_id, fields='status')
    client.add_comment(issue=issue, body=comment)


def transict_issue(issue_id, transition, comment):
    issue = get_issue(issue_id, fields='status')
    client.transition_issue(
        issue=issue, transition=transition, comment=comment)


def get_transictions(issue_id):
    issue = get_issue(issue_id, fields='status')
    return client.transitions(issue)


def assign_issue(issue_id, user_email):
    try:
        issue = get_issue(issue_id, fields='status')
        user = get_user(user_email)
        client.assign_issue(issue=issue, assignee=user.name)
    except IndexError:
        raise JIRAUserNotFound("Usuario nao localizado no JIRA")
    except Exception as e:
        raise AssignError("Erro ao realizar assign a issue: {}".format(e))


def add_watcher(issue_id, user_email):
    try:
        issue = get_issue(issue_id, fields='status')
        user = get_user(user_email)
        client.add_watcher(issue, user.name)
    except IndexError:
        raise JIRAUserNotFound("Usuario nao localizado no JIRA")
    except Exception as e:
        raise AssignError("Error on add watcher: {}".format(e))


def get_user(user_email):
    """ Get the first occurrence of a user with especified email """
    return client.search_users(user=user_email, maxResults=1)[0]
