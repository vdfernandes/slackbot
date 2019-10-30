#!/usr/bin/python
# -*- coding: utf-8 -*-

from slackbot.models import Session
from slackbot.models.channel import Channel, ChannelPriority, ChannelIssueType

from slackbot.slack.slackcommand import (
    SlackCommand,
    CmdArgumentParser,
    handle_exceptions
)


class ConfigChannel(SlackCommand):
    session = Session()
    help_text = ""
    usage = ""

    def _handle_args(self, args):
        parser = CmdArgumentParser(
            description="Configura canal do Slack",
            prog='config-channel',
            add_help=False
        )
        parser.add_argument(
            "--project",
            type=str,
            metavar="JIRA_PROJECT",
            help="Projeto default para o canal"
        )
        parser.add_argument(
            "--issue-type",
            type=str,
            metavar="ISSUE_TYPE",
            help="Tipo de issue default do canal"
        )
        parser.add_argument(
            "--close-id",
            type=str,
            metavar="CLOSE_ID",
            help="ID da transição para fechar a issue"
        )
        parser.add_argument(
            "--reopen-id",
            type=str,
            metavar="REOPEN_ID",
            help="ID da transição para reabrir uma issue"
        )
        parser.add_argument(
            "--priority",
            type=str,
            metavar="JIRA_PRIORITY",
            help="Prioridade default para o canal ao abrir issues"
        )
        parser.add_argument(
            "--priorities",
            type=str,
            metavar="PRIORITIES",
            nargs='*',
            help="Lista de prioridades aceitas pelo canal. Formato SLACK_PRI:JIRA_PRI"
        )
        parser.add_argument(
            "--map-issuetypes", 
            type=str,
            metavar="MAP_ISSUETYPES",
            nargs='*',
            help="Lista 'de:para' de issue_types. Formato SLACK_ISSYETYPE:JIRA_ISSUETYPE"
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="Lista as configurações atuais"
        )
        parser.add_argument(
            "--help",
            required=False,
            action="store_true",
            help="Mostra esta mensagem."
        )
        self.help_text = parser.format_help()
        self.usage = parser.format_usage()
        return parser.parse_args(args)

    @handle_exceptions
    def run(self):
        """
        Execução de configuração inicial do canal
        """
        self.args = self._handle_args(self.arguments)

        if self.args.help:
            self._help()
            return

        if self.args.list:
            self._list()
            return

        if self.args.project or self.args.issue_type or self.args.priority or \
           self.args.close_id or self.args.reopen_id:
            self._config_channel()

        if self.args.priorities:
            self._config_priorities()

        if self.args.map_issuetypes:
            self._config_issuetypes()

    def _help(self):
        self.send(text=self.help_text)

    def _list(self):
        ch = Channel().find(channel=self.channel)
        full_text = [
            "```",
            "Channel ID: {}".format(ch.channel),
            "Project: {}".format(ch.project),
            "Default Issue Type: {}".format(ch.issuetype),
            "Default Priority: {}".format(ch.priority),
            "Close ID: {}".format(ch.id_tr_close)
        ]

        full_text.append("\nIssue Types (slack_issuetype : jira_issuetype)")
        full_text.append("----------------------------------------------")
        for sit, jit in ch.dict_issuetypes.items():
            full_text.append("    {} : {}".format(sit, jit))

        full_text.append("\nPriorities (slack_priority : jira_priority)")
        full_text.append("-------------------------------------------")
        for sp, jp in ch.dict_priorities.items():
            full_text.append("    {} : {}".format(sp, jp))

        full_text.append("```")
        self.text = "\n".join(full_text)
        self.send()

    def _config_channel(self):
        ch = Channel().find(channel=self.channel)
        if ch:
            self.text = "`Canal reconfigurado com sucesso.`"
            ch.project = self.args.project if self.args.project else ch.project
            ch.issuetype = self.args.issue_type if self.args.issue_type else ch.issuetype
            ch.priority = self.args.priority if self.args.priority else ch.priority
            ch.id_tr_close = self.args.close_id if self.args.close_id else ch.id_tr_close
            ch.id_tr_reopen = self.args.reopen_id if self.args.reopen_id else ch.id_tr_reopen
        else:
            self.text = "`Canal configurado com sucesso.`"
            ch = Channel(
                channel=self.channel,
                project=self.args.project,
                issuetype=self.args.issue_type,
                priority=self.args.priority,
                id_tr_close=self.args.close_id,
                id_tr_reopen=self.args.reopen_id
            )

        self.session.add(ch)
        self.session.commit()
        self.send()

    def _config_priorities(self):
        ch_priorities = ChannelPriority().find(channel=self.channel)

        if ch_priorities:
            self.text = "`Prioridades reconfiguradas com sucesso.`"
            ch_priorities.delete()
            self.session.commit()
        else:
            self.text = "`Prioridades configuradas com sucesso.`"

        for item in self.args.priorities:
            s_pri, j_pri = item.split(':')

            ch_pri = ChannelPriority(
                channel=self.channel,
                slack_priority=s_pri,
                jira_priority=j_pri
            )
            self.session.add(ch_pri)

        self.session.commit()
        self.send()

    def _config_issuetypes(self):
        ch_issuetypes = ChannelIssueType().find(channel=self.channel)

        if ch_issuetypes:
            self.text = "`Issue Types reconfigurados com sucesso.`"
            ch_issuetypes.delete()
            self.session.commit()
        else:
            self.text = "`Issue Types configurados com sucesso.`"

        for item in self.args.map_issuetypes:
            s_itype, j_itype = item.split(':')

            ch_itype = ChannelIssueType(
                channel=self.channel,
                slack_issuetype=s_itype,
                jira_issuetype=j_itype
            )
            self.session.add(ch_itype)

        self.session.commit()
        self.send()
