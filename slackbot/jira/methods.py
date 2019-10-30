#!/usr/bin/python
# -*- coding: utf-8 -*-
from slackbot.jira import client
from slackbot.jira.exception import (
    CreateIssueError,
    JIRAError,
    JIRAUserNotFound,
    AssignError
)


def open_issue(project, summary, text, issue_type, priority=None):
    """
    Abre um card no JIRA
    """
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
    """
    Busca um card no JIRA
    """
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
    """
    Comenta um card no JIRA
    """
    issue = get_issue(issue_id, fields='status')
    client.add_comment(issue=issue, body=comment)


def transict_issue(issue_id, transition, comment):
    """
    Transiciona um card no JIRA
    """
    issue = get_issue(issue_id, fields='status')
    client.transition_issue(
        issue=issue, transition=transition, comment=comment)


def get_transictions(issue_id):
    """
    Busca uma lista de transições disponíveis para um card no JIRA
    """
    issue = get_issue(issue_id, fields='status')
    return client.transitions(issue)


def assign_issue(issue_id, user_email):
    """
    Atribui um responsável a um card no JIRA
    """
    try:
        issue = get_issue(issue_id, fields='status')
        user = get_user(user_email)
        client.assign_issue(issue=issue, assignee=user.name)
    except IndexError:
        raise JIRAUserNotFound("Usuario nao localizado no JIRA")
    except Exception as e:
        raise AssignError("Erro ao realizar assign a issue: {}".format(e))


def add_watcher(issue_id, user_email):
    """
    Atribui um visualizador a um card no JIRA
    """
    try:
        issue = get_issue(issue_id, fields='status')
        user = get_user(user_email)
        client.add_watcher(issue, user.name)
    except IndexError:
        raise JIRAUserNotFound("Usuario nao localizado no JIRA")
    except Exception as e:
        raise AssignError("Error on add watcher: {}".format(e))


def get_user(user_email):
    """
    Busca os dados de um usuário no JIRA
    """
    return client.search_users(user=user_email, maxResults=1)[0]
