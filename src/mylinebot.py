"""
オウム返し Line Bot
"""

import os

import boto3
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage,
)

handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))

rekognition = boto3.client("rekognition")


def lambda_handler(event, context):
    headers = event["headers"]
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


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """ TextMessage handler """
    # 画像を取得
    message_content = line_bot_api.get_message_content(event.message.id)
    sent_image_bytes = message_content.content

    # Rekognition 呼び出し
    result = rekognition.detect_faces(Image={"Bytes": sent_image_bytes}, Attributes=["ALL"])

    # 結果を出す
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(result)))
