#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from slackbot.models import Session
from slackbot.models.card import Card
from slackbot.models.channel import Channel
from slackbot.jira.methods import open_issue, assign_issue, add_watcher
from slackbot.slack.methods import (
    user_info,
    channel_info,
    group_info,
    for_humans_text,
    message_permalink
)
from slackbot.slack.slackcommand import (
    SlackCommand,
    CmdArgumentParser,
    PlannedException,
    handle_exceptions
)


class Register(SlackCommand):
    session = Session()
    help_text = "\n".join([
        "Comando responsável por registrar cards."
    ])

    def _help(self):
        self.send(text=self.help_text)

    def _handle_args(self, args):
        parser = CmdArgumentParser(
            description="Abre um card no JIRA e associa a uma thread do Slack",
            prog='open-card',
            add_help=False
        )
        parser.add_argument(
            "issue_type",
            type=str,
            metavar="ISSUE_TYPE",
            nargs="?",
            help="Tipo de issue para abertura do card"
        )
        parser.add_argument(
            "-p",
            "--priority",
            type=str,
            help="Prioridade do card."
        )
        parser.add_argument(
            "--help",
            required=False,
            action="store_true",
            help="Mostra esta mensagem."
        )
        self.usage = parser.format_usage()
        return parser.parse_args(args)

    @handle_exceptions
    def run(self):
        """
        Método de registro de cards
        """

        self.text = "Só testando mesmo."
        self.send()

        """
        # Verifica se eh uma mensagem normal, ou dentro da thread
        args = self._handle_args(self.arguments)

        if args.help:
            self._help()
            return

        # Captura de Dados
        ts = self.msg_ts
        issue_text = self.cmd_text
        requester = user_info(self.msg_from).get('user')
        operator = user_info(self.msg_from).get('user')
        channel_conf = Channel().find(channel=self.channel)

        # Validação de configuração
        if not channel_conf:
            self.text = "Canal não configurado!"
            self.send()
            raise PlannedException("canal não configurado")

        # Define com qual issue type o card será aberto
        if args.issue_type:
            if args.issue_type in channel_conf.issue_types:
                issue_type = channel_conf.dict_issuetypes.get(args.issue_type)
            else:
                self.text = " ".join([
                    "`ISSUE_TYPE` incorreto, esperado um dos valores: ",
                    "`{}`".format(channel_conf.issue_types)
                ])
                self.send()
                raise PlannedException("Tipo de card incorreto.")
        elif channel_conf.issuetype:
            issue_type = channel_conf.issuetype
        else:
            self.text = " ".join([
                "Não existe issue type configurado, favor informar",
                "```{}```".format(self.usage)
            ])
            self.send()
            raise PlannedException("Tipo de card não informado/configurado.")

        if args.priority:
            if args.priority in channel_conf.priorities:
                priority = channel_conf.dict_priorities.get(args.priority)
            else:
                self.text = " ".join([
                    "`PRIORITY` incorreto, Esperado um dos valores:",
                    "`{}`".format(channel_conf.priorities)
                ])
                self.send()
                raise PlannedException("Prioridade incorreta.")
        elif channel_conf.priority:
            priority = channel_conf.priority
        else:
            self.text = " ".join([
                "Não existe priority configurado, favor informar",
                "```{}```".format(self.usage)
            ])
            self.send()
            raise PlannedException("Prioridade não informada/configurada.")

        # Verifica se já foi aberto um card para esta thread
        card = self.session.query(Card).filter_by(slack_ts=ts).first()
        if card:
            self.logger.debug("Card existente.")
            self.text = "\n".join([
                "Já existe um card para esta thread:", 
                "Card `{}`.".format(card.jira_issue)
            ])
            self.send()
        else:
            self.logger.debug("Criando novo card.")
            self._open_card(
                ts=ts,
                text=for_humans_text(issue_text),
                requester=requester,
                operator=operator,
                project=channel_conf.project,
                issue_type=issue_type,
                priority=priority
            )
        """


    def _requester_from_echo(self):
        """ 
        Retorna usuário em caso de menção
        """

        re_atuser = re.compile(r'<@[A-Z0-9]*>')
        echo_line = self.mthread_text.split('\n')[0]
        self.logger.debug("\n\n{}".format(echo_line))
        mentioned_user = re_atuser.findall(echo_line)[0]
        self.logger.debug("\n\n{}".format(echo_line))
        return user_info(mentioned_user[2:-1]).get('user')

    def _open_card(self, ts, text, requester, operator, project, issue_type, priority):
        if self.channel.startswith('C'):
            ch_info = channel_info(self.channel)
            channel = ch_info.get('channel').get('name')
        elif self.channel.startswith('G'):
            gp_info = group_info(self.channel)
            channel = gp_info.get('group').get('name')
        elif self.channel.startswith('D'):
            us_info = user_info(self.msg_from)
            channel = us_info.get('user').get('name')

        req_name = requester.get('profile').get('real_name_normalized')
        req_mail = requester.get('profile').get('email')
        req_id = requester.get('id')
        oper_mail = operator.get('profile').get('email')
        permalink = message_permalink(channel=self.channel, ts=self.thread_ts)

        # Montagem de mensagem legível
        issue_fulltext = [
            "*Solicitante:* {}".format(req_name),
            "*E-mail:* {}".format(req_mail),
            "*Msg Origem:* {}".format(permalink),
            "*Solicitação:* \r{}".format(text)
        ]

        summary = "Solicitado via Slack: Channel #{}".format(channel)
        issue = open_issue(
            project=project,
            summary=summary,
            text="\r".join(issue_fulltext),
            issue_type=issue_type,
            priority=priority)

        # Adiciona o operador como responsavel
        try:
            assign_issue(issue_id=issue.key, user_email=oper_mail)
        except Exception as e:
            self.logger.error("Erro em adição de responsável: {}".format(e))

        # Adiciona o solicitante como watcher
        try:
            add_watcher(issue_id=issue.key, user_email=req_mail)
        except Exception as e:
            self.logger.error("Erro na adição de visualizador: {}".format(e))

        card = Card(
            slack_ts=ts,
            jira_issue=issue.key,
            status='opened',
            requester=req_id
        )
        self.session.add(card)
        self.session.commit()

        self.text = "Card `{}` criado.\n{}".format(issue.key, issue.permalink())
        self.send()
