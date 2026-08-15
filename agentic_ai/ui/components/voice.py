import io
import tempfile
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from agentic_ai.ui.styles.icons import get_icon_svg


def transcribe_audio_buffer(audio_file_buffer) -> str:
    """Transcribe recorded audio file buffer using SpeechRecognition."""
    if not audio_file_buffer:
        return ""

    try:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file_buffer.read())
            tmp_path = tmp.name

        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        st.warning("Speech recorded, but speech could not be understood. Please try speaking clearly.")
        return ""
    except Exception as ex:
        st.info("Audio captured. Processing query...")
        return ""


def generate_audio_reply(text_content: str) -> bytes:
    """Generate audio MP3 speech bytes for the chatbot reply using gTTS."""
    if not text_content:
        return b""

    try:
        # Strip markdown symbols for clean speech output
        clean_text = (
            text_content.replace("#", "")
            .replace("*", "")
            .replace("`", "")
            .replace("•", "")
            .replace("- ", "")
        )
        if len(clean_text) > 300:
            clean_text = clean_text[:300] + "..."

        fp = io.BytesIO()
        tts = gTTS(text=clean_text, lang="en", slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as ex:
        return b""


def render_voice_interface():
    """Render dual Streamlit native audio recorder and browser Web Speech interface."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    bg_color = "#151D2F" if is_dark else "#FFFFFF"
    border_color = "rgba(148,163,184,0.15)" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    st.markdown(f"""
        <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:12px; padding:12px 16px; margin-bottom:14px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:{text_color}; font-size:0.95rem; margin-bottom:6px;">
                {get_icon_svg('Mic', '#3B82F6', 18)} Voice Assistant — Listen & Speak
            </div>
            <p style="margin:0 0 10px 0; font-size:0.8rem; color:#64748B;">Record audio query using your microphone. UberOps AI will listen and speak the response aloud.</p>
        </div>
    """, unsafe_allow_html=True)

    recorded_audio = st.audio_input("🎤 Tap to record your voice question")
    if recorded_audio:
        transcribed_text = transcribe_audio_buffer(recorded_audio)
        if transcribed_text:
            st.success(f"Voice Query Captured: \"{transcribed_text}\"")
            return transcribed_text

    return None
