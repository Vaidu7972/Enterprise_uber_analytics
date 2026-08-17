import io
import os
import tempfile
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from agentic_ai.ui.styles.icons import get_icon_svg


def transcribe_audio_buffer(audio_file_buffer, lang: str = "en-IN") -> tuple[str, str]:
    """Transcribe recorded audio file buffer using SpeechRecognition with robust error handling and guaranteed temp file cleanup."""
    if not audio_file_buffer:
        return "", "Audio buffer is empty."

    tmp_path = None
    try:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file_buffer.read())
            tmp_path = tmp.name

        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language=lang)
        if not text or not text.strip():
            return "", "Audio was recorded, but no speech was detected."
        return text.strip(), ""
    except sr.UnknownValueError:
        return "", "We couldn't understand the recording. Please try speaking clearly."
    except sr.RequestError:
        return "", "Speech transcription service is temporarily unavailable."
    except Exception:
        return "", "Audio captured, but speech could not be processed. Please try again."
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def create_spoken_summary(text_content: str) -> str:
    """Create a concise spoken summary of the answer text for Text-to-Speech playback."""
    if not text_content:
        return ""

    clean = (
        text_content.replace("#", "")
        .replace("*", "")
        .replace("`", "")
        .replace("•", "")
        .replace("- ", "")
        .replace("\n\n", " ")
        .replace("\n", " ")
        .strip()
    )

    sentences = [s.strip() for s in clean.split(".") if s.strip()]
    if len(sentences) >= 2:
        summary = f"{sentences[0]}. {sentences[1]}."
    elif len(sentences) == 1:
        summary = f"{sentences[0]}."
    else:
        summary = clean

    if len(summary) > 280:
        summary = summary[:277] + "..."

    return summary


def generate_audio_reply(text_content: str) -> bytes:
    """Generate audio MP3 speech bytes for the spoken summary reply using gTTS."""
    if not text_content:
        return b""

    try:
        summary_text = create_spoken_summary(text_content)
        if not summary_text:
            return b""

        fp = io.BytesIO()
        tts = gTTS(text=summary_text, lang="en", slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return b""


def render_voice_panel(is_active: bool = False) -> str | None:
    """Render compact Voice Assistant panel only when activated by the 🎤 trigger button. Occupies ZERO vertical space when inactive."""
    if not is_active:
        return None

    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    bg_color = "#151D2F" if is_dark else "#FFFFFF"
    border_color = "rgba(59,130,246,0.3)" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    lang_code = st.session_state.get("voice_lang", "en-IN")

    st.markdown(f"""
        <div class="ai-voice-panel" style="background:{bg_color}; border:1px solid {border_color}; border-radius:12px; padding:12px 16px; margin-bottom:12px; box-shadow:0 4px 16px rgba(0,0,0,0.08);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="display:flex; align-items:center; gap:8px; font-weight:800; color:{text_color}; font-size:0.92rem;">
                    {get_icon_svg('Mic', '#3B82F6', 18)} Voice Query Recording
                </div>
                <div style="font-size:0.72rem; color:#3B82F6; background:rgba(59,130,246,0.12); padding:2px 8px; border-radius:6px; font-weight:700;">
                    {lang_code}
                </div>
            </div>
            <p style="margin:0 0 8px 0; font-size:0.78rem; color:{sub_color};">Speak into your microphone. Review and edit transcription before dispatching to UberOps AI.</p>
        </div>
    """, unsafe_allow_html=True)

    recorded_audio = st.audio_input("🎤 Record microphone query", key="compact_voice_audio_input_popover")

    if recorded_audio:
        transcribed_text, err_msg = transcribe_audio_buffer(recorded_audio, lang=lang_code)

        if err_msg:
            st.warning(f"⚠️ {err_msg}")
        elif transcribed_text:
            st.markdown("""
                <div style="margin-top:6px; margin-bottom:4px; font-size:0.8rem; font-weight:700; color:#10B981; display:flex; align-items:center; gap:6px;">
                    ✓ Voice Captured — Review & Edit Transcription
                </div>
            """, unsafe_allow_html=True)

            edited_text = st.text_area(
                "Transcription",
                value=transcribed_text,
                key="voice_transcription_edit_area",
                height=70,
                help="You can modify the transcribed text before submitting to UberOps AI."
            )

            btn_col1, btn_col2 = st.columns([1, 1])

            with btn_col1:
                if st.button("🚀 Send to UberOps AI", key="btn_send_voice_query", type="primary", use_container_width=True):
                    st.session_state.show_voice_panel = False
                    return edited_text.strip()

            with btn_col2:
                if st.button("🔄 Re-record", key="btn_rerecord_voice", use_container_width=True):
                    st.rerun()

    return None


def render_voice_interface() -> str | None:
    """Legacy wrapper for voice panel rendering."""
    return render_voice_panel(is_active=st.session_state.get("show_voice_panel", False))
