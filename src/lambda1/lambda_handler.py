#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""

import os
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET'))


def lambda_handler(event, context):
    headers = event["headers"]  # or event["multiValueHeaders"]
    body = event["body"]

    result = callback(headers, body)
    return {"statusCode": 200, "body": json.dumps(result)}


def callback(headers, body):
    # get X-Line-Signature header value
    signature = headers['X-Line-Signature']

    # get request body as text
    print("Request body: " + body)

    # handle webhook body
    handler.handle(body, signature)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ TextMessage handler """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
