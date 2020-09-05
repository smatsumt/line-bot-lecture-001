"""
オウム返し Line Bot
"""

import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


def lambda_handler(event, context):
    headers = event["headers"]  # or event["multiValueHeaders"]
    body = event["body"]

    # get X-Line-Signature header value
    signature = headers['X-Line-Signature']

    # handle webhook body
    handler.handle(body, signature)

    return {"statusCode": 200, "body": "OK"}


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ TextMessage handler """
    input_text = event.message.text

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=input_text))
