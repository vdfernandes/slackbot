#!/usr/bin/python
# -*- coding: utf-8 -*-
from slackbot.models import Session
from slackbot.models.card import Card
from slackbot.models.channel import Channel
from slackbot.jira.methods import transict_issue
from slackbot.slack.methods import user_info, for_humans_text
from slackbot.slack.slackcommand import (
    SlackCommand,
    CmdArgumentParser,
    PlannedException,
    handle_exceptions
)


class Close(SlackCommand):
    session = Session()
    help_text = "\n".join([
        "-- Pendente implementação --"
    ])

    def _help(self):
        self.send(text=self.help_text)

    def _handle_args(self, args):
        parser = CmdArgumentParser(
            description="Fecha o card JIRA e associado a thread corrente.",
            prog='comment',
            add_help=False
        )
        parser.add_argument(
            "status",
            type=str,
            metavar="STATUS",
            nargs="?",
            default="success",
            choices=('success', 'failed', 'aborted'),
            help="Tipo de issue para abertura do card"
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
        Executa o processo de fechamento de card no JIRA
        """
        args = self._handle_args(self.arguments)
        if args.help:
            self._help()
            return

        user = user_info(self.msg_from).get('user')
        ch = Channel().find(channel=self.channel)
        if not ch:
            self.text = "Canal não configurado!"
            self.send()
            raise PlannedException("Canal não configurado.")

        # Verifica se já foi aberto um card para esta thread
        card = self.session.query(Card).filter_by(slack_ts=self.thread_ts).first()
        if card:
            self.logger.debug("Closing card.")
            self._close(
                user=user,
                issue_id=card.jira_issue,
                transiction=ch.id_tr_close,
                comment=for_humans_text(self.cmd_text),
                status=args.status
            )
            self.text = "Card `{}` finalizado!".format(card.jira_issue)
            self.send()
        else:
            self.logger.debug("No card to close.")
            self.text = "Não existe card associado a esta thread."
            self.send()

    def _close(self, user, issue_id, transiction, comment, status):
        """
        Transição de card para finalizado.
        """
        user_name = user.get('profile').get('real_name_normalized')
        user_mail = user.get('profile').get('email')

        comment_fulltext = [
            "*Fechado com status {}*".format(status),
            "*From:* {}".format(user_name),
            "*E-mail:* {}".format(user_mail),
            "*Comentário de fechamento:* \r{}".format(comment)
        ]

        transict_issue(
            issue_id=issue_id,
            transition=transiction,
            comment="\r".join(comment_fulltext)
        )
