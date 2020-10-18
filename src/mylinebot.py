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
    # ユーザから送られてきた画像を一時ファイルとして保存
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = "/tmp/sent_image.jpg"
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # Rekognition で感情分析する
    with open(file_path, 'rb') as fd:
        sent_image_binary = fd.read()
        response = rekognition.detect_faces(Image={"Bytes": sent_image_binary}, Attributes=["ALL"])

    # メッセージを決める
    if all_happy(response):
        message = "みんな、いい笑顔ですね!!"
    elif all_angry(response):
        message = "みんな怒ってますねー"
    elif no_face(response):
        message = "そこに誰もいませんよ"
    else:
        message = "ぼちぼちですね"

    # 返答を送信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))

    # file_path の画像を削除
    os.remove(file_path)


def all_happy(response):
    """
    全員が happy なら True を返す
    :param response:
    :return:
    """
    for detail in response["FaceDetails"]:
        if most_emotion(detail["Emotions"]) != "HAPPY":
            return False
    return True


def all_angry(response):
    """
    全員が怒っていたら True を返す
    :param response:
    :return:
    """
    for detail in response["FaceDetails"]:
        if most_emotion(detail["Emotions"]) != "ANGRY":
            return False
    return True


def no_face(response):
    """
    顔がなければ True
    :param response:
    :return:
    """
    return len(response["FaceDetails"]) < 1


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
