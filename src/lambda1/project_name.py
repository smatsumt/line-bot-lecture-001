#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""

import json
import logging
import os


def lambda_handler(event, context):
    _lambda_logging_init()
    # prm1 = event["pathParameters"]["prm1"]
    # prm2 = event["queryStringParameters"]["prm2"]
    # body = event["body"]

    return {"statusCode": 200, "body": json.dumps(event)}


def _lambda_logging_init():
    """
    logging の初期化。LOGGING_LEVEL, LOGGING_LEVELS 環境変数を見て、ログレベルを設定する。
      LOGGING_LEVELS - "module1=DEBUG,module2=INFO" という形の文字列を想定。自分のモジュールのみ DEBUG にするときなどに利用
    """
    logging.getLogger().setLevel(os.getenv('LOGGING_LEVEL', 'INFO'))  # lambda の場合はロガー設定済みのためこちらが必要
    if os.getenv('LOGGING_LEVELS'):
        for mod_lvl in os.getenv('LOGGING_LEVELS').split(','):
            mod, lvl = mod_lvl.split('=')
            logging.getLogger(mod.strip()).setLevel(lvl.strip())
