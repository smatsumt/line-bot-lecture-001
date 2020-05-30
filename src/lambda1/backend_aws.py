#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

import boto3

logger = logging.getLogger(__name__)
s3 = boto3.resource("s3")

bucket_name = os.getenv("IMAGE_S3_BUCKET", "")
bucket = s3.Bucket(bucket_name)


def store_image_file(local_filepath: Path):
    """ 画像ファイルを S3 に保存する """
    filename = local_filepath.name
    bucket.upload_file(Key=filename, Filename=str(local_filepath))
