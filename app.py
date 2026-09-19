import streamlit as st
import subprocess
import os
import tempfile
from pathlib import Path

st.set_page_config(page_title="Music Source Separator", layout="centered")
st.title("🎵 Music Source Separator")
st.write("Upload an MP3 or WAV file, then click Process to split it into vocals, drums, bass, and other instruments.")

uploaded_file = st.file_uploader("Drag and drop your audio file here", type=["mp3", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Process"):
        with st.spinner("Separating sources... this can take a few minutes, especially on CPU."):
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, uploaded_file.name)
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            output_dir = os.path.join(temp_dir, "separated")

            result = subprocess.run(
                ["demucs", "-o", output_dir, input_path],
                capture_output=True,
                text=True,
            )

        if result.returncode != 0:
            st.error("Something went wrong while processing:")
            st.code(result.stderr)
        else:
            base_name = Path(uploaded_file.name).stem
            model_dirs = [
                d for d in os.listdir(output_dir)
                if os.path.isdir(os.path.join(output_dir, d))
            ]

            if model_dirs:
                track_dir = os.path.join(output_dir, model_dirs[0], base_name)
                st.success("Done! Here are your separated tracks:")

                stem_icons = {
                    "vocals": "🎤",
                    "drums": "🥁",
                    "bass": "🎸",
                    "piano": "🎹",
                    "other": "🎻",
                }

                for stem_file in sorted(os.listdir(track_dir)):
                    stem_name = Path(stem_file).stem
                    icon = stem_icons.get(stem_name.lower(), "🎵")
                    st.subheader(f"{icon} {stem_name.capitalize()}")
                    st.audio(os.path.join(track_dir, stem_file))
            else:
                st.error("Couldn't find the separated output. Check the terminal for details.")