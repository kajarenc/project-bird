import streamlit as st


x = st.experimental_audio_input("SAY SOMETHING!!!")

if x:
    st.audio(x)
