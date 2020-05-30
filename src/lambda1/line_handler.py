#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, LocationMessage, TextSendMessage,
)

import backend_aws

backend = backend_aws  # ここを指定して、モジュールを差し替えることが可能

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET'))
tmp_dir = Path(os.getenv("TMPDIR", "/tmp"))

logger = logging.getLogger(__name__)


def callback(headers, body):
    # get X-Line-Signature header value
    signature = headers['X-Line-Signature']

    # get request body as text
    logger.info("Request body: " + body)

    # handle webhook body
    handler.handle(body, signature)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """ TextMessage handler """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    """ ImageMessage handler """
    # 画像を保存
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = tmp_dir / f"{event.message.id}.jpg"
    with file_path.open("wb") as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # バックエンド処理
    backend.store_image_file(file_path)

    # メッセージ送信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.id))


@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    """ LocationMessage handler """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.address))
