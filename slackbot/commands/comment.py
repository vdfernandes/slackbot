#!/usr/bin/python
# -*- coding: utf-8 -*-
from slackbot.models import Session
from slackbot.models.card import Card
from slackbot.jira.methods import comment_issue
from slackbot.slack.methods import user_info, for_humans_text, get_message
from slackbot.slack.slackcommand import (
    SlackCommand,
    CmdArgumentParser,
    handle_exceptions
)


class Comment(SlackCommand):
    session = Session()
    help_text = "\n".join([
        "-- Pendente implementação --"
    ])

    def _help(self):
        self.send(text=self.help_text)

    def _handle_args(self, args):
        parser = CmdArgumentParser(
            description="Adiciona um comentário ao card atual",
            prog='comment',
            add_help=False
        )
        parser.add_argument(
            "--help",
            required=False,
            action="store_true",
            help="Mostra esta mensagem."
        )
        parser.add_argument(
            "point",
            type=str,
            nargs="?",
            choices=(':point_up:'),
            help="De onde capturar o texto do comentário."
        )
        self.usage = parser.format_usage()
        return parser.parse_args(args)

    @handle_exceptions
    def run(self):
        """
        Execução de comentário para card no JIRA.
        """
        args = self._handle_args(self.arguments)
        if args.help:
            self._help()
            return

        # verifica se já foi aberto um card para esta thread
        card = self.session.query(Card).filter_by(slack_ts=self.thread_ts).first()
        if card:
            self.logger.debug("Adding comment to a card.")
            if args.point:
                try:
                    pointed_msg = self._get_pointed_up_message()
                    pointed_user = pointed_msg.get('user')
                    user = user_info(pointed_user).get('user')
                    comment = pointed_msg.get('text')
                except:
                    self.logger.error("Comment: error to ger previous message")
                    user = user_info(self.msg_from).get('user')
                    comment = self.cmd_text
            else:
                user = user_info(self.msg_from).get('user')
                comment = self.cmd_text

            self._comment(
                user=user,
                issue_id=card.jira_issue,
                comment=for_humans_text(comment)
            )
        else:
            self.logger.debug("No card to comment.")
            self.text = "Não existe card aberto para comentar."
            self.send()

    def _comment(self, user, issue_id, comment):
        """
        Adição de comentário em card
        """
        user_name = user.get('profile').get('real_name_normalized')
        user_mail = user.get('profile').get('email')

        comment_fulltext = [
            "*From:* {}".format(user_name),
            "*E-mail:* {}".format(user_mail),
            "*Comentário:* \r{}".format(comment)
        ]

        comment_issue(
            issue_id=issue_id,
            comment="\r".join(comment_fulltext))

        self.text = "`comentario adicionado`"
        self.send()
