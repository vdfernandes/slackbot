#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging


def load_yaml(filename):
    """
    Retorna dict com conteúdo do arquivo YAML
    """
    import yaml

    logger = logging.getLogger(__name__)
    cur_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(cur_path, filename)

    logger.debug("loading file {}".format(file_path))
    with open(file_path, 'r') as yaml_file:
        try:
            yaml_dict = yaml.load(yaml_file)
            return yaml_dict
        except yaml.YAMLError as e:
            logger.error("Error to load file {0}: {1}".format(file_path, e))
            raise

def getenv(name, default=''):
    """
    Retorna as variáveis de ambiente com base no nome
    """
    try:
        return os.environ[name]
    except Exception as e:
        return default

