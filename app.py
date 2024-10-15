import streamlit as st
from utils import upload_to_s3
from copy import deepcopy

if "processed_files" not in st.session_state:
    st.session_state.processed_files = dict()


uploaded_audio_file = st.experimental_audio_input("SAY SOMETHING!!!")


if uploaded_audio_file is not None:
    if uploaded_audio_file.file_id not in st.session_state.processed_files:
        st.session_state.processed_files = dict()
        st.session_state.processed_files[uploaded_audio_file.file_id] = {
            "file": uploaded_audio_file,
            "status": "pending",
            "public_url": None,
        }
        public_url = upload_to_s3(deepcopy(uploaded_audio_file))
        st.session_state.processed_files[uploaded_audio_file.file_id][
            "public_url"
        ] = public_url
        st.session_state.processed_files[uploaded_audio_file.file_id][
            "status"
        ] = "uploaded_to_s3"


st.write(st.session_state)
