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

    # メッセージを決める
    if all_happy(result):
        message = "みんな、いい笑顔ですね!!"
    elif all_angry(result):
        message = "みんな怒ってますねー"
    elif no_face(result):
        message = "そこに誰もいませんよ"
    else:
        message = "ぼちぼちですね"

    # 結果を出す
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))


def all_happy(result):
    """
    全員が happy なら True を返す
    :param result:
    :return:
    """
    for detail in result["FaceDetails"]:
        if most_emotion(detail["Emotions"]) != "HAPPY":
            return False
    return True


def all_angry(result):
    """
    全員が怒っていたら True を返す
    :param result:
    :return:
    """
    for detail in result["FaceDetails"]:
        if most_emotion(detail["Emotions"]) != "ANGRY":
            return False
    return True


def no_face(result):
    """
    顔がなければ True
    :param result:
    :return:
    """
    return len(result["FaceDetails"]) < 1


def most_emotion(emotions):
    """
    もっとも確信度が高い感情を返す
    :param emotions:
    :return:
    """
    max_conf = 0
    result = ""
    for e in emotions:
        if max_conf < e["Confidence"]:
            max_conf = e["Confidence"]
            result = e["Type"]
    return result
