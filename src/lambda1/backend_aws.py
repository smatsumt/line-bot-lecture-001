#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
import uuid

import boto3

logger = logging.getLogger(__name__)
s3 = boto3.resource("s3")

bucket_name = os.getenv("IMAGE_S3_BUCKET", "")
bucket = s3.Bucket(bucket_name)

user_2_store_info = {}

user_2_session_dict = {}


def store_image_file(local_filepath: Path):
    """ 画像ファイルを S3 に保存する """
    filename = local_filepath.name
    bucket.upload_file(Key=filename, Filename=str(local_filepath))
    return f"https://{bucket_name}.s3-ap-northeast-1.amazonaws.com/{filename}"


# store info functions
def create_store(user_id: str):
    store_id = str(uuid.uuid4())
    store_info = {
        "id": store_id,
        "name": "",
        "images": [],
        "location": {},
    }
    user_2_store_info[user_id] = store_info


def update_store(user_id: str, store_info: dict):
    if user_id in user_2_store_info:
        user_2_store_info[user_id].update(store_info)
    else:
        user_2_store_info[user_id] = store_info


def query_store(user_id: str):
    return user_2_store_info.get(user_id)


def delete_store(user_id: str):
    del user_2_store_info[user_id]


def store_session(user_id: str, session_info: dict):
    user_2_session_dict[user_id] = session_info


def get_session(user_id: str):
    return user_2_session_dict.get(user_id, {"user_id": user_id})
