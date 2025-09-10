import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import base64
from io import BytesIO

# Initialize recognizer
recognizer = sr.Recognizer()

def text_to_speech(text: str, autoplay: bool = True, show_player: bool = False):
    """Convert text to speech with optional player visibility"""
    if not text:
        return None
    
    tts = gTTS(text=text, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    
    # Only create player if show_player is True
    if show_player:
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        audio_tag = f"""
        <audio autoplay={str(autoplay).lower()} controls>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_tag, unsafe_allow_html=True)
    else:
        # Play audio without showing controls
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        audio_tag = f"""
        <audio autoplay={str(autoplay).lower()} style="display:none">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_tag, unsafe_allow_html=True)

def continuous_listen():
    """Continuous listening using Streamlit's session state"""
    if 'listening' not in st.session_state:
        st.session_state.listening = False
        st.session_state.accumulated_text = ""
    
    if st.button("🎤 Start Continuous Listening"):
        st.session_state.listening = True
    
    if st.button("⏹ Stop Listening"):
        st.session_state.listening = False
        return st.session_state.accumulated_text
    
    if st.session_state.listening:
        with st.spinner("Listening... Speak now (say 'stop' to end)"):
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = recognizer.listen(source, timeout=3)
                    text = recognizer.recognize_google(audio)
                    if "stop" in text.lower():
                        st.session_state.listening = False
                    else:
                        st.session_state.accumulated_text += " " + text
                        st.rerun()  # Refresh to show intermediate results
                except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                    pass
    
    return st.session_state.accumulated_text if not st.session_state.listening else ""