import time

import streamlit as st

from cookie import new_suno_auth, start_keep_alive, get_random_token, suno_sqlite
from utils import generate_music, suno_upload_audio, check_url_available


@st.cache_resource
def initialize():
    """
    IDENTITY = "razgriz.35@gmail.com"
    SESSION = "sess_2nUbUioIE8cci4IcaLtfXVxyfdI"
    COOKIE = "ajs_anonymous_id=b26c2460-7a5f-40f7-a582-d8d028e68d5e; _ga=GA1.1.561711694.1729030604; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yblViU21LanJuOXlYc1oxRTZiRVpGQW43RHYiLCJyb3RhdGluZ190b2tlbiI6ImRkd2RydTZkbWZudnJnenI3cGdyZjV2Y3dtaWt2YzQ4cmRiYnFqMmkifQ.I_oDWyYEBVeMwQElLmJXAhD5rsFXxrHC0EPxKY9NDvdtjCRxzxWrCZhExHz3PdY5KePVSlpY85Bd-neZth4GpvObhapVvVwbGTctwC0Ve3vOchB8JjoXDgpXXcChmir1gswN18D7xjTrGQRJ_hBnsjv_1HfzBqXAw_w6bYv8lt7UdkLAsGW_vzFdi8QK6act4qShMK3Cssaw7i4TQ9GOeUWE1UwsXc7tn6pah_5-YoEk7fm3lTBFegFLcLAsWsnNRiprwQcdb-RDgoVWcU2OOMZ4T3YI7uP8uIl-NdFgwg01YxOldpy1GRs9naSsK5tOlnbXlEz68exYm_WzN3a1eg; __client_uat=1729030618; __client_uat_U9tcbTPE=1729030618; _cfuvid=duxLkYcnDIzVKTqd40InlnT4uo9Q48vqk.kTVWVVD4I-1729061150123-0.0.1.1-604800000; __stripe_mid=e8a2f2ed-7b63-43b7-a774-998ffe916a17b750bb; __stripe_sid=0da0dc47-a48a-4bc6-9571-dfa801228af4a59a16; _ga_7B0KEDD7XP=GS1.1.1729061151.2.1.1729062026.0.0.0; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%22d4e5009a-0077-4560-9868-6b8086c182dd%22%2C%22%24device_id%22%3A%20%22192924143e0334-088282ad763fa1-16525637-1d73c0-192924143e0334%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22d4e5009a-0077-4560-9868-6b8086c182dd%22%7D; __cf_bm=AmvxajhANOB.9Ks2SW2Uwxpa.dm0jC9V1a0CpeNPjC0-1729062077-1.0.1.1-pcg1ko.Ok8rhJ7k8nneaXbvaqQML0U4YL23iC1sWx6qL.Y_w0YOK8j1ToIPGFsZK49fZitNbS7IDnx8eq.i23g"
    """

    IDENTITY = "kajarenc@gmail.com"
    SESSION = "sess_2nUeeIUXJ3oFyqDG6TVmoUUH1JH"
    COOKIE = "_ga=GA1.1.585205625.1729032160; ajs_anonymous_id=438875d6-73c5-495f-ba79-9c6b3620ddb7; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yblVlY0d5TGpudzNkZjRxWGoxbzlHNkhGcFUiLCJyb3RhdGluZ190b2tlbiI6Ijg2dDQwdzQ1NXU0Nmt2eWk3bnRmbDJiN3U2ZG83MWluOTgwM2k2ajMifQ.cXI-1vGA8RJkJwKGYdgyoD0D3nbS9fhgJaylnRunAxBevg2pgfs1XSlxsri6FvYPUz-NMz8dSstDgu5i77xztAVdp3D0QoC8vA1mb6NB-4dtR6T0CTUsX0xMWt8fBsIfYgihrN4zMf8sCbR7TRRjj9mt9bIUsbVOGTM-w1Cixnt0Y64CWot9M_CjqHmS-4qtmgGMWf4TmuRoB5RlmIMF6haRIiabNCXiUP0nKZAF10zFb3wZcWKDW6XtS7jsosOHX6suiMHkD3hkl7wgTi_G-MXVrNYzH_Rdf9cj01dLdSQLlHbciExtGcjBrAM7V81q5Z_XWu7vj-lbgyz58cybJw; __client_uat=1729032175; __client_uat_U9tcbTPE=1729032175; __stripe_mid=6c824372-68d9-4aec-909b-1d7dbb907910de1fd9; _cfuvid=NGkTvHpyWkbBjAErGoBGglfsVNhsC6cuvmAo4LvP0Dk-1729037517837-0.0.1.1-604800000; __cf_bm=gbV6zTAMrh6OoWzsjKuEtPlRj8ucEq7Xq.VMW5mq0rc-1729067137-1.0.1.1-kCxvVXoD6oFJ.la3fQkG6OLsE4_jzn8OOKQFNIk2.Kmblkayud53cYYFNe1oDPASN05PWrOgHgYVOXXPxoS.3w; _ga_7B0KEDD7XP=GS1.1.1729067137.2.0.1729067137.0.0.0; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%22ed21731f-e67d-447c-bcab-3f31fb679475%22%2C%22%24device_id%22%3A%20%22192925901f28e3-04dfa047351119-16525637-1d73c0-192925901f28e3%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22ed21731f-e67d-447c-bcab-3f31fb679475%22%7D"
    existing_id = suno_sqlite.query_one("select id,identity,[session],cookie from session where identity =?", (IDENTITY,))
    if existing_id:
        existing_id = suno_sqlite.operate_one("update session set session=?, cookie=?, token=? where identity =?", (SESSION, COOKIE, IDENTITY,""))
    else:
        existing_id = suno_sqlite.operate_one("insert into session (identity,session,cookie,token) values(?,?,?,?)", (IDENTITY, SESSION, COOKIE,""))

    if existing_id:
        new_suno_auth(IDENTITY, SESSION, COOKIE)
        start_keep_alive()


initialize()

if (audio := st.experimental_audio_input("Record some audio")):
    upload_progress = st.progress(0, text="Uploading recording")
    continue_clip_id = suno_upload_audio("my_audio.wav", audio.read(), get_random_token(), upload_progress)

    data = {
        "title": "My random title",  # TODO(vdonato): Title input
        "tags": ",",
        "prompt": "",
        "mv": "chirp-v3-5",
        "continue_at": None,
        "continue_clip_id": continue_clip_id,
        "generation_type":"TEXT",
        "task": "extend",
        "continued_aligned_prompt": None,
        "negative_tags": "",
        "infill_end_s": None,
        "infill_start_s": None
    }

    resp = generate_music(data, get_random_token())
    upload_progress.progress(90)

    song_url1 = f"https://cdn1.suno.ai/{resp['clips'][0]['id']}.mp3"
    song_url2 = f"https://cdn1.suno.ai/{resp['clips'][1]['id']}.mp3"

    check_url_available(song_url1)
    check_url_available(song_url2)

    upload_progress.progress(99)

    time.sleep(60)
    upload_progress.progress(100)
    upload_progress.empty()

    st.audio(song_url1)
    st.audio(song_url2)

