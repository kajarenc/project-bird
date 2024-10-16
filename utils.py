# Taken from https://github.com/SunoApi/SunoApi/blob/main/utils.py

import json
import os
import time
import random
import re
import requests

import boto3
import streamlit as st

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
S3_WEB_SITE_URL = os.getenv("S3_WEB_SITE_URL")
S3_ACCESSKEY_ID = os.getenv("S3_ACCESSKEY_ID")
S3_SECRETKEY_ID = os.getenv("S3_SECRETKEY_ID")

COMMON_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    # "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Referer": "https://suno.com/",
    "Origin": "https://suno.com",
}

BASE_URL = "https://studio-api.suno.ai"

def fetch(url, headers=None, data=None, method="POST"):
    if headers is None:
        headers = {}
    headers.update(COMMON_HEADERS)
    if data is not None:
        data = json.dumps(data)

    try:
        resp = None
        requests.packages.urllib3.disable_warnings()
        if method == "GET":
            resp = requests.get(url=url, headers=headers, verify=False)
        else:
            resp = requests.post(url=url, headers=headers, data=data, verify=False)
        if resp.status_code != 200:
            print(resp.text)
        if S3_WEB_SITE_URL is None or S3_WEB_SITE_URL == "https://cdn1.suno.ai":
            result = resp.text
        elif S3_WEB_SITE_URL is not None and "s3.bitiful.net" in S3_WEB_SITE_URL:
            result = resp.text.replace('https://cdn1.suno.ai/', f'{S3_WEB_SITE_URL}/files/')
        else:
            result = resp.text.replace('https://cdn1.suno.ai/', 'https://res.sunoapi.net/files/')
        result = result.replace('.png', '.png?fmt=webp&txt=SunoAPI&txt-size=0.35&txt-pos=0.5,*0.96&txt-alpha=0.30')
        return json.loads(result)
        # return resp.json()
    except Exception as e:
        return {"detail":str(e)}

def get_page_feed(page, token):
    headers = {"Authorization": f"Bearer {token}"}
    # api_url = f"{BASE_URL}/api/feed/?ids={ids}"
    api_url = f"{BASE_URL}/api/feed/?page={page}"
    response = fetch(api_url, headers, method="GET")
    return response

def generate_music(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/v2/"
    response = fetch(api_url, headers, data)
    return response

def local_time():
    return  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def check_url_available(url, twice=False):
    if S3_WEB_SITE_URL is None or S3_WEB_SITE_URL == "https://cdn1.suno.ai":
        pass
    elif S3_WEB_SITE_URL is not None and "s3.bitiful.net" in S3_WEB_SITE_URL:
        url = url.replace(f'{S3_WEB_SITE_URL}/files/', 'https://cdn1.suno.ai/')
    else:
        url = url.replace(f'https://res.sunoapi.net/files/', 'https://cdn1.suno.ai/')
    i = 0
    while not twice and i < 10:
        # 每间隔一秒钟检查一次url文件大小
        file_size = get_file_size(url)
        if file_size >= 1024*1024:
            print(local_time() + f" ***check_url_available -> {url} 文件大小：{file_size} 大于1MB可访问到***\n")
            break
        i += 1
        print(local_time() + f" ***check_url_available -> {url} 文件大小：{file_size} 小于1MB继续检查***\n")
        time.sleep(2)
    time.sleep(3)

def get_file_size(url):
    try:
        requests.packages.urllib3.disable_warnings()
        resp = requests.head(url, verify=False)
        if resp.status_code == 200:
            file_size = resp.headers.get('Content-Length')
            if file_size:
                return int(file_size)
            # else:
            #     return 0
            print(local_time() + f" ***check_url_available -> {url} file_size -> {file_size} ***\n")
        else:
            print(local_time() + f" ***check_url_available -> {url} status_code -> {resp.status_code} ***\n")
            return 0
    except Exception as e:
        print(local_time() + f" ***check_url_available -> {url} exception -> {str(e)} ***\n")
        return 0


def suno_upload_audio(filename, bytes_data, token, my_bar):
    try:
        upload_url = f"{BASE_URL}/api/uploads/audio/"
        data = {"extension": "mp3"}
        resp = requests.post(upload_url, headers={"Authorization": f"Bearer {token}"}, data=json.dumps(data))
        result = resp.json()
        print(local_time() + f" ***suno_upload_audio -> {upload_url} upload request -> {result} ***\n")
        my_bar.progress(20)
        audio_id = result['id']
        upload_url = result['url']
        resp = requests.post(url=result['url'], data=result['fields'], files={"file": bytes_data}) 
        if resp.status_code == 204:
            print(local_time() + f" ***suno_upload_audio -> {upload_url} upload result -> {resp.status_code} ***\n")
            data = {
                "upload_type": "file_upload",
                "upload_filename": filename
            }
            upload_url = f"{BASE_URL}/api/uploads/audio/{audio_id}/upload-finish/"
            resp = requests.post(upload_url, headers={"Authorization": f"Bearer {token}"}, data=json.dumps(data))
            result = resp.json()
            print(local_time() + f" ***suno_upload_audio -> {upload_url} upload finish -> {result} ***\n")
            my_bar.progress(40)
            upload_url = f"{BASE_URL}/api/uploads/audio/{audio_id}/"
            while True:
                resp = requests.get(upload_url, headers={"Authorization": f"Bearer {token}"})
                result = resp.json()
                print(local_time() + f" ***suno_upload_audio -> {upload_url} upload status -> {result} ***\n")
                if 'detail' in result and result['detail'] == "Unauthorized":
                    pass
                elif 'status' in result and result['status'] == "complete":
                    break
                elif 'status' in result and result['status'] == "error":
                    return {"detail": result['error_message']}
                else:
                    time.sleep(5)
            my_bar.progress(60)
            upload_url = f"{BASE_URL}/api/uploads/audio/{audio_id}/initialize-clip/"
            resp = requests.post(upload_url, headers={"Authorization": f"Bearer {token}"})
            result = resp.json()
            print(local_time() + f" ***suno_upload_audio -> {upload_url} initializa-clip -> {result} ***\n")
            my_bar.progress(80)
            return result['clip_id']
        else:
            print(local_time() + f" ***suno_upload_audio -> {upload_url} upload status_code -> {str(resp.status_code)} ***\n")
            return {"detail": str(resp.status_code)}
    except Exception as e:
        print(local_time() + f" ***suno_upload_audio -> {upload_url} exception -> {str(e)} ***\n")
        return {"detail": 'Unauthorized'}
