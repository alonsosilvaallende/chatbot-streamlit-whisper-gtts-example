import streamlit as st
import base64
from tempfile import NamedTemporaryFile
from audiorecorder import audiorecorder
from whispercpp import Whisper
from gtts import gTTS
import whisper


to_language_code_dict = whisper.tokenizer.TO_LANGUAGE_CODE
to_language_code_dict["automatic"] = "auto"
language_list = list(to_language_code_dict.keys())
language_list = sorted(language_list)
language_list = [language.capitalize() for language in language_list if language != "automatic"]
language_list = ["Automatic"] + language_list
#language_list = "Automatic"
# Download whisper.cpp
@st.cache_resource  # 👈 Add the caching decorator
def load_model(precision):
    if precision == "whisper-tiny":
        model = Whisper('tiny')
    elif precision == "whisper-base":
        model = Whisper('base')
    else:
        model = Whisper('small')
    return model


def inference(audio, lang):
    # Save audio to a file:
    with NamedTemporaryFile(suffix=".mp3") as temp:
        with open(f"{temp.name}", "wb") as f:
            f.write(audio.export().read())
        result = w.transcribe(f"{temp.name}", lang=lang)
        text = w.extract_text(result)
    return text[0]

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

# Streamlit
with st.sidebar:
    audio = audiorecorder("Click to send voice message", "Recording... Click when you're done", key="recorder")
    st.title("Echo Bot with Whisper")
    language = st.selectbox('Language', language_list, index=23)
    lang = to_language_code_dict[language.lower()]
    precision = st.selectbox("Precision", ["whisper-tiny", "whisper-base", "whisper-small"])
    w = load_model(precision)
    voice = st.toggle('Voice')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if (prompt := st.chat_input("Your message")) or len(audio):
    # If it's coming from the audio recorder transcribe the message with whisper.cpp
    if len(audio)>0:
        prompt = inference(audio, lang)

    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"{prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
        if voice:
            if lang == 'es':
                tts = gTTS(response, lang='es', tld="cl")
            else:
                tts = gTTS(response, lang=lang)
            #tts = gTTS(response, lang='it')
            with NamedTemporaryFile(suffix=".mp3") as temp:
                tempname = temp.name
                tts.save(tempname)
                autoplay_audio(tempname)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
