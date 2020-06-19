#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, LocationMessage, StickerMessage,
    TextSendMessage, ImageSendMessage, StickerSendMessage,
    QuickReply, QuickReplyButton, CameraAction, CameraRollAction, LocationAction,
    FollowEvent, SourceUser,
)

import backend_aws
import control_session

backend = backend_aws  # ここを指定して、モジュールを差し替えることが可能

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET'))
tmp_dir = Path(os.getenv("TMPDIR", "/tmp"))

logger = logging.getLogger(__name__)


# *SendMessage 利用時に共通して使うクリックリプライボタン (カメラで更新等のクイックボタンを毎度、つける)
DEFAULT_QUICK_REPLY = QuickReply(items=[
    QuickReplyButton(action=CameraAction(label="カメラで更新")),
    QuickReplyButton(action=CameraRollAction(label="写真で更新")),
    QuickReplyButton(action=LocationAction(label="場所を設定")),
])
quick_reply_dict = {
    None: DEFAULT_QUICK_REPLY,
    "no_menu": None,
}

WELLCOME_MESSAGE = """
{nickname_call}はじめまして！😃
友だち追加ありがとうございます。firsttest001 です。

さっそくお店の登録から、始めていきましょう！
""".strip()
# このトークからの通知を受け取らない場合は、画面右上のメニューから通知をオフにしてください。


def callback(headers, body):
    # get X-Line-Signature header value
    signature = headers['X-Line-Signature']

    # get request body as text
    logger.info("Request body: " + body)

    # handle webhook body
    handler.handle(body, signature)

    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    """ FollowEvent handler """
    # あいさつメッセージの準備
    nickname_call = ""
    if isinstance(event.source, SourceUser):
        profile = line_bot_api.get_profile(event.source.user_id)
        nickname_call = f"{profile.display_name}さん、"
    welcome_messages = [TextSendMessage(text=WELLCOME_MESSAGE.format(nickname_call=nickname_call))]

    # セッション処理 - text_message のときと同じ
    session_info = backend.get_session(event.source.user_id)
    response = control_session.do(session_info, {})
    # あいさつメッセージを添えて、初期メッセージを出す
    line_bot_api.reply_message(
        event.reply_token,
        welcome_messages + list(map(_response_to_message, response))
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ TextMessage handler """
    # セッション処理
    session_info = backend.get_session(event.source.user_id)
    response = control_session.do(session_info, vars(event.message))

    line_bot_api.reply_message(
        event.reply_token,
        list(map(_response_to_message, response)))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """ ImageMessage handler """
    # 画像を保存
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = tmp_dir / f"{event.message.id}.jpg"
    with file_path.open("wb") as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # バックエンド処理
    image_url = backend.store_image_file(file_path)

    # セッション処理
    session_info = backend.get_session(event.source.user_id)
    response = control_session.do(session_info, {"image": image_url})

    # メッセージ送信
    line_bot_api.reply_message(
        event.reply_token,
        list(map(_response_to_message, response)))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    """ LocationMessage handler """
    # セッション処理
    session_info = backend.get_session(event.source.user_id)
    response = control_session.do(session_info, vars(event.message))

    line_bot_api.reply_message(
        event.reply_token,
        list(map(_response_to_message, response)))


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    """ StickerMessage handler - スタンプのハンドラ"""
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(package_id=event.message.package_id, sticker_id=event.message.sticker_id,
                           quick_reply=DEFAULT_QUICK_REPLY))


def _response_to_message(response: dict):
    """ control_session が返す response から Line の Message オブジェクトを生成 """
    if "text" in response:
        quick_reply = quick_reply_dict.get(response.get("quick_reply"))
        return TextSendMessage(text=response["text"], quick_reply=quick_reply)
    elif "image" in response:
        return ImageSendMessage(original_content_url=response["image"])
    else:
        raise ValueError("Invalid response.")
