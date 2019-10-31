#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import logging
import argparse

from slackbot.utils import getenv
from slackbot.daemon import Daemon
from slackbot.slack.rtmslackbot import RTMSlackBot
from slackbot.slack.exception import RTMConnectionLost

# Importer dos comandos de processamento
from slackbot.commands.register import Register
from slackbot.commands.handlers import HandleCommand

# Logging
READ_DELAY = getenv('DEFAULT_READ_DELAY')
RETRY_DELAY = getenv('DEFAULT_RETRY_DELAY')
LOGLEVEL = getenv('DEFAULT_LOGLEVEL')

# Comandos aceitos
known_commands = {
    'register': Register
}

class BotDeamon(Daemon):
    """ 
    Class to daemonize bot
    """
    def __init__(
        self,
        pidfile,
        stdin='/dev/null',
        stdout='/dev/null',
        stderr='/dev/null',
        logger=None
    ):
        """
        Inicializador do Deamon
        """
        Daemon.__init__(
            self, pidfile,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            logger=logger
        )

    def _handle_commands(self, cmd):
        """
        Processamento dos comandos enviados
        """
        self.logger.debug("Command: {}".format(cmd.command))
        cmd.__class__ = known_commands.get(
            cmd.command.lower(),
            HandleCommand
        )
        threading.Thread(target=cmd.run).start()
        self.logger.debug("Thread initiated.")

    def run(self):
        """
        Execução dos processos do Bot
        """
        def connect():
            try:
                sb.connect(retry=10)
                self.logger.info("Connected!")
            except:
                self.logger.error("Waiting to retry more...")
                time.sleep(int(RETRY_DELAY))
                connect()

        sb = RTMSlackBot(channel=None)
        self.logger.info("Connecting to Slack RTM API...")
        connect()
        while True:
            try:
                commands = sb.read_commands()
                if commands:
                    self.logger.info(commands)
                for cmd in commands:
                    self._handle_commands(cmd)
                time.sleep(int(READ_DELAY))
            except RTMConnectionLost:
                self.logger.error("Connection with Slack lost.")
                self.logger.info("Re-connecting to Slack RTM API...")
                connect()
                self.logger.info("Reconnected!")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.logger.error("---\r\nException: {}\r\nType: {}\r\nFile: {}\r\nLine: {}\r\n".format(
                    e,
                    exc_type,
                    fname,
                    exc_tb.tb_lineno
                ))


def start_logging(level):
    """
    Logging
    """
    logging.addLevelName(5, 'DEEPDEBUG')
    try:
        lvl = getattr(logging, level)
    except AttributeError:
        if level == 'DEEPDEBUG':
            lvl = 5
        else:
            raise AttributeError("error with level")

    # logger = logging.getLogger(__name__)
    logger = logging.getLogger()
    logger.setLevel(lvl)

    file_handler = logging.FileHandler('logs/slackbot.log')
    file_handler.setLevel(lvl)
    f_formatter = logging.Formatter(
        '%(threadName)s: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(f_formatter)
    logger.addHandler(file_handler)

    ver_handler = logging.StreamHandler()
    ver_handler.setLevel(logging.INFO)
    logger.addHandler(ver_handler)
    return logger


def load_args(sysargs):
    """
    Parser dos argumentos do Bot
    """

    parser = argparse.ArgumentParser(
        prog='',
        description="Chatbot de interacao com Slack"
    )
    parser.add_argument(
        "option",
        type=str,
        choices=('start', 'stop', 'restart'),
        help="Option of slackbot service"
    )

    return parser.parse_args(sysargs)


def main(sysargs):
    args = load_args(sysargs)
    logger = start_logging(LOGLEVEL)
    logger.debug("Slackbot called with sysargs: {}".format(args))

    if LOGLEVEL in ('DEBUG', 'DEEPDEBUG'):
        outfile = '/tmp/slackbot.out'
    else:
        outfile = '/dev/null'

    slackbot = BotDeamon(
        pidfile='/tmp/slackbot.pid',
        stdout=outfile,
        stderr=outfile)
    logger.debug("class {} instantiated".format(slackbot.__class__))

    if args.option == 'start':
        if getenv('SLACKBOT_DAEMON') == 'true':
            logger.info("Starting slackbot as deamon...")
            slackbot.start()
        else:
            logger.info("Starting slackbot...")
            slackbot.run()
    elif args.option == 'stop':
        logger.info("Stoping slackbot...")
        slackbot.stop()
    elif args.option == 'restart':
        logger.info("Re-starting slackbot...")
        slackbot.restart()


if __name__ == '__main__':
    main(sys.argv[1:])
