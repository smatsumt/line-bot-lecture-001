#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import backend_aws

backend = backend_aws  # must be inject from outside


def do(session_info: dict, request: dict):
    """

    :param session_info:
    :param request:
    :return: response(dict)
    """
    if "store_id" in session_info:
        # お店が登録済みの場合
        return do_update_store(session_info, request)
    else:
        # お店が未登録の場合
        return do_register_store(session_info, request)


def do_register_store(session_info: dict, request: dict):
    """

    :param session_info:
    :param request:
    :return: response(dict)
    """
    user_id = session_info["user_id"]
    # 初手の仮実装
    store_info = {
        "id": "testid000001",
        "name": "shop_test001",
        "images": [],
        "location": {},
    }
    backend.update_store(user_id, store_info)
    session_info["store_id"] = "testid000001"
    backend.store_session(user_id, session_info)
    return {"text": "お店を登録しました"}


def do_update_store(session_info: dict, request: dict):
    """

    :param session_info:
    :param request:
    :return: response(dict)
    """
    user_id = session_info["user_id"]
    if "image" in request:
        # 画像がきたとき
        store_info = backend.query_store(user_id)
        images = store_info.get("images", [])
        images.append(request["image"])
        store_info["images"] = images
        backend.update_store(user_id, store_info)
        return {"text": "お店の写真を更新しました"}

    elif "address" in request:
        # 場所情報がきたとき
        store_info = backend.query_store(user_id)
        store_info["location"] = {
            "address": request["address"],
            "latitude": request["latitude"],
            "longitude": request["longitude"],
        }
        backend.update_store(user_id, store_info)
        return {"text": f"お店の場所を {request['address']} に設定しました"}

    else:
        # デバッグ用 - お店情報の json を出す
        store_info = backend.query_store(user_id)
        message = json.dumps(store_info)
        return {"text": message}
