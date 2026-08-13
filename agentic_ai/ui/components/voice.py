import streamlit as st
import streamlit.components.v1 as components
from agentic_ai.ui.styles.icons import get_icon_svg


def render_voice_input_component():
    """Render browser-native Web Speech API microphone speech recognition bridge."""
    speech_html = f"""
    <div style="background:#151D2F; border:1px solid rgba(148,163,184,0.15); border-radius:12px; padding:12px 16px; font-family:sans-serif; color:#F8FAFC; display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <button id="mic-btn" style="background:#3B82F6; color:white; border:none; padding:8px 14px; border-radius:8px; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:8px;">
                {get_icon_svg('Mic', '#FFFFFF', 16)} Click to Speak Query
            </button>
            <span id="mic-status" style="font-size:0.85rem; color:#94A3B8;">Ready to listen...</span>
        </div>
        <div id="mic-result" style="font-size:0.9rem; font-weight:600; color:#60A5FA;"></div>
    </div>

    <script>
        const btn = document.getElementById('mic-btn');
        const status = document.getElementById('mic-status');
        const result = document.getElementById('mic-result');

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            btn.onclick = () => {{
                try {{
                    recognition.start();
                    status.innerText = 'Listening... Speak clearly into your microphone.';
                    btn.style.background = '#EF4444';
                }} catch (e) {{
                    status.innerText = 'Microphone active or busy.';
                }}
            }};

            recognition.onresult = (event) => {{
                const transcript = event.results[0][0].transcript;
                result.innerText = 'Captured: "' + transcript + '"';
                status.innerText = 'Voice input captured! Click Send below.';
                btn.style.background = '#3B82F6';
            }};

            recognition.onerror = (event) => {{
                status.innerText = 'Speech recognition error: ' + event.error;
                btn.style.background = '#3B82F6';
            }};

            recognition.onend = () => {{
                if (btn.style.background === 'rgb(239, 68, 68)') {{
                    btn.style.background = '#3B82F6';
                    status.innerText = 'Speech ended. Review captured query.';
                }}
            }};
        }} else {{
            status.innerText = 'Voice input is not available in this browser. Please type query.';
            btn.disabled = true;
            btn.style.opacity = '0.5';
        }}
    </script>
    """
    components.html(speech_html, height=75)


def render_tts_audio_player(text_content: str, key_suffix: str = ""):
    """Render browser-native Web SpeechSynthesis text-to-speech reader."""
    # Clean text to exclude code blocks or markdown tables
    clean_text = text_content.replace("#", "").replace("*", "").replace("`", "").replace("•", "")
    clean_text_js = clean_text.replace("'", "\\'").replace("\n", " ")

    tts_html = f"""
    <div style="display:inline-flex; align-items:center; gap:8px; margin-top:8px;">
        <button id="tts-play-{key_suffix}" style="background:rgba(59,130,246,0.14); color:#60A5FA; border:1px solid rgba(96,165,250,0.3); padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:6px;">
            {get_icon_svg('Volume2', '#60A5FA', 14)} Read Aloud
        </button>
        <button id="tts-stop-{key_suffix}" style="background:rgba(239,68,68,0.14); color:#FCA5A5; border:1px solid rgba(252,165,165,0.3); padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:6px;">
            {get_icon_svg('VolumeX', '#FCA5A5', 14)} Stop
        </button>
        <span id="tts-status-{key_suffix}" style="font-size:0.75rem; color:#94A3B8;"></span>
    </div>

    <script>
        const playBtn = document.getElementById('tts-play-{key_suffix}');
        const stopBtn = document.getElementById('tts-stop-{key_suffix}');
        const status = document.getElementById('tts-status-{key_suffix}');

        if ('speechSynthesis' in window) {{
            playBtn.onclick = () => {{
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance('{clean_text_js[:400]}');
                msg.rate = 1.0;
                msg.pitch = 1.0;
                msg.onstart = () => {{ status.innerText = 'Reading...'; }};
                msg.onend = () => {{ status.innerText = ''; }};
                window.speechSynthesis.speak(msg);
            }};

            stopBtn.onclick = () => {{
                window.speechSynthesis.cancel();
                status.innerText = '';
            }};
        }} else {{
            playBtn.disabled = true;
            stopBtn.disabled = true;
            status.innerText = 'Text-to-speech not supported.';
        }}
    </script>
    """
    components.html(tts_html, height=45)
