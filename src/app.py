import streamlit as st
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from transcriber import transcribe_audio
from summarizer import generate_podcast_analysis
from video_extractor import extract_audio_from_video
from youtube_extractor import download_youtube_audio, get_youtube_info, is_valid_youtube_url

load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Podcast Notes Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and header
st.title("🎤 Podcast Notes Agent")
st.caption("📻 Upload a podcast or video, get instant highlights and key takeaways powered by AI")

# Teach mode toggle
col1, col2 = st.columns([0.9, 0.1])
with col2:
    show_teach_mode = st.checkbox("👨‍🏫", help="Show system prompts and API requests")

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("videos", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

# Initialize session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "uploaded_video_name" not in st.session_state:
    st.session_state.uploaded_video_name = ""
if "last_system_prompt" not in st.session_state:
    st.session_state.last_system_prompt = ""
if "last_raw_json" not in st.session_state:
    st.session_state.last_raw_json = ""
if "transcription_request" not in st.session_state:
    st.session_state.transcription_request = {}
if "content_source" not in st.session_state:
    st.session_state.content_source = "🎙️ Podcast File"
if "youtube_url" not in st.session_state:
    st.session_state.youtube_url = ""
if "youtube_info" not in st.session_state:
    st.session_state.youtube_info = None

# Sidebar: File upload
with st.sidebar:
    st.header("📥 Content Source")
    
    st.session_state.content_source = st.radio(
        "Select source type:",
        ["🎙️ Podcast File", "🎬 Video File", "🎥 YouTube Link"]
    )
    
    if st.session_state.content_source == "🎙️ Podcast File":
        st.markdown("Supported formats: MP3, WAV, M4A, OGG, FLAC")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["mp3", "wav", "m4a", "ogg", "flac"],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            file_path = f"uploads/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_video_name = ""  # Clear video
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.markdown(f"*File size:* {uploaded_file.size / 1024 / 1024:.2f} MB")
            
    elif st.session_state.content_source == "🎬 Video File":
        st.markdown("Supported formats: MP4, WebM, MKV")
        
        uploaded_video = st.file_uploader(
            "Choose a video file",
            type=["mp4", "webm", "mkv"],
            label_visibility="collapsed"
        )
        
        if uploaded_video is not None:
            file_path = f"videos/{uploaded_video.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_video.getbuffer())
            st.session_state.uploaded_video_name = uploaded_video.name
            st.session_state.uploaded_file_name = ""  # Clear audio
            st.success(f"✅ Uploaded: {uploaded_video.name}")
            st.markdown(f"*File size:* {uploaded_video.size / 1024 / 1024:.2f} MB")
            
    elif st.session_state.content_source == "🎥 YouTube Link":
        st.markdown("Paste a YouTube video URL:")
        youtube_url_input = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            value=st.session_state.youtube_url,
        )

        if youtube_url_input and youtube_url_input != st.session_state.youtube_url:
            st.session_state.youtube_url = youtube_url_input
            st.session_state.youtube_info = None  # reset preview on new URL

        if st.session_state.youtube_url:
            if not is_valid_youtube_url(st.session_state.youtube_url):
                st.error("❌ Invalid YouTube URL")
            else:
                if st.button("🔍 Fetch Video Info", use_container_width=True):
                    with st.spinner("Fetching video details..."):
                        st.session_state.youtube_info = get_youtube_info(st.session_state.youtube_url)

                if st.session_state.youtube_info:
                    info = st.session_state.youtube_info
                    if info["success"]:
                        st.success(f"🎬 **{info['title']}**")
                        mins = int(info['duration'] // 60)
                        secs = int(info['duration'] % 60)
                        st.caption(f"👤 {info['uploader']}  •  ⏱️ {mins}:{secs:02d}")
                    else:
                        st.error(f"❌ {info['error']}")

    st.markdown("---")
    st.markdown("*How it works:*")
    st.markdown("""
    1. Upload content or provide a link
    2. Click "Transcribe" (or Extract & Transcribe)
    3. Click "Analyze" to get AI insights
    4. Export your notes
    """)

# Main content area
st.markdown("---")

# Show current file status
content_type = "podcast"
if st.session_state.content_source == "🎙️ Podcast File" and st.session_state.uploaded_file_name:
    st.info(f"📁 *Current file:* {st.session_state.uploaded_file_name} [PODCAST]")
    content_type = "podcast"
elif st.session_state.content_source == "🎬 Video File" and st.session_state.uploaded_video_name:
    st.info(f"📁 *Current video:* {st.session_state.uploaded_video_name} [VIDEO]")
    content_type = "video"
elif st.session_state.content_source == "🎥 YouTube Link" and st.session_state.youtube_url:
    yt_title = st.session_state.youtube_info["title"] if st.session_state.youtube_info and st.session_state.youtube_info["success"] else st.session_state.youtube_url
    st.info(f"🎥 *Current source:* {yt_title} [YOUTUBE]")
    content_type = "youtube"
else:
    st.warning("👉 *Start by selecting a content source in the sidebar*")

# Tab 1: Transcription
tab1, tab2, tab3 = st.tabs(["📝 Transcription", "✨ Analysis", "📚 Resources"])

with tab1:
    st.subheader("Step 1: Transcribe Content")
    st.markdown("Convert your content to text using OpenAI's Whisper API")
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        if st.session_state.content_source == "🎙️ Podcast File":
            if st.button("🎙️ Transcribe Podcast", type="primary", use_container_width=True):
                if not st.session_state.uploaded_file_name:
                    st.error("❌ Please upload a podcast file first")
                else:
                    file_path = f"uploads/{st.session_state.uploaded_file_name}"
                    
                    with st.spinner("🔄 Transcribing audio using Whisper API..."):
                        result = transcribe_audio(file_path, source_type="podcast")
                        st.session_state.transcription_request = {
                            "model": "whisper-1",
                            "file": st.session_state.uploaded_file_name,
                            "language": "en"
                        }
                    
                    if result["success"]:
                        st.session_state.transcript = result["text"]
                        st.success("✅ Transcription complete!")
                    else:
                        st.error(f"❌ Transcription failed: {result['error']}")
                        
        elif st.session_state.content_source == "🎬 Video File":
            if st.button("🎬 Extract Audio & Transcribe", type="primary", use_container_width=True):
                if not st.session_state.uploaded_video_name:
                    st.error("❌ Please upload a video file first")
                else:
                    video_path = f"videos/{st.session_state.uploaded_video_name}"
                    
                    with st.spinner("📥 Extracting audio from video..."):
                        extraction_result = extract_audio_from_video(video_path)
                    
                    if not extraction_result["success"]:
                        st.error(f"❌ Extraction failed: {extraction_result['error']}")
                    else:
                        audio_path = extraction_result["file_path"]
                        st.success(f"✅ Audio extracted successfully")
                        
                        with st.spinner("🔄 Transcribing audio using Whisper API..."):
                            result = transcribe_audio(audio_path, source_type="video")
                            st.session_state.transcription_request = {
                                "model": "whisper-1",
                                "file": os.path.basename(audio_path),
                                "language": "en"
                            }
                        
                        if result["success"]:
                            st.session_state.transcript = result["text"]
                            st.success("✅ Transcription complete!")
                        else:
                            st.error(f"❌ Transcription failed: {result['error']}")

        elif st.session_state.content_source == "🎥 YouTube Link":
            if st.button("🎥 Download & Transcribe YouTube", type="primary", use_container_width=True):
                if not st.session_state.youtube_url or not is_valid_youtube_url(st.session_state.youtube_url):
                    st.error("❌ Please enter a valid YouTube URL in the sidebar first")
                else:
                    with st.spinner("⬇️ Downloading audio from YouTube..."):
                        yt_result = download_youtube_audio(st.session_state.youtube_url)

                    if not yt_result["success"]:
                        st.error(f"❌ Download failed: {yt_result['error']}")
                    else:
                        audio_path = yt_result["file_path"]
                        st.success(f"✅ Audio downloaded: **{yt_result['title']}**")

                        with st.spinner("🔄 Transcribing audio using Whisper API..."):
                            result = transcribe_audio(audio_path, source_type="youtube")
                            st.session_state.transcription_request = {
                                "model": "whisper-1",
                                "file": os.path.basename(audio_path),
                                "language": "en",
                                "source": yt_result["title"],
                            }

                        if result["success"]:
                            st.session_state.transcript = result["text"]
                            st.success("✅ Transcription complete!")
                        else:
                            st.error(f"❌ Transcription failed: {result['error']}")

    # Show transcript if available
    if st.session_state.transcript:
        st.markdown("---")
        st.subheader("📖 Full Transcript")
        
        with st.expander("View full transcript", expanded=True):
            st.text_area(
                "Transcript:",
                value=st.session_state.transcript,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
        
        # Transcript stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", len(st.session_state.transcript.split()))
        with col2:
            st.metric("Character Count", len(st.session_state.transcript))
        with col3:
            est_minutes = len(st.session_state.transcript.split()) / 150
            st.metric("Est. Duration", f"{int(est_minutes)} min")

with tab2:
    st.subheader("Step 2: Analyze Content")
    st.markdown("Generate highlights, key takeaways, and summary using GPT-4o")
    
    if st.session_state.transcript:
        if st.button("✨ Generate Highlights & Takeaways", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Analyzing {content_type} with GPT-4o..."):
                analysis = generate_podcast_analysis(st.session_state.transcript, content_type=content_type)
                st.session_state.analysis_result = analysis
                st.session_state.last_system_prompt = analysis.get("system_prompt", "")
                st.session_state.last_raw_json = analysis.get("raw_response", "")
        
        # Show analysis results
        if st.session_state.analysis_result and st.session_state.analysis_result["success"]:
            result = st.session_state.analysis_result
            
            st.success("✅ Analysis complete!")
            st.markdown("---")
            
            # Summary
            st.subheader("📋 Executive Summary")
            st.info(result["summary"])
            
            # Key Takeaways and Highlights in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💡 Key Takeaways")
                for i, takeaway in enumerate(result["takeaways"], 1):
                    st.markdown(f"**{i}.** {takeaway}")
            
            with col2:
                st.subheader("⭐ Highlights")
                for i, highlight in enumerate(result["highlights"], 1):
                    st.markdown(f"**{i}.** {highlight}")
            
            # Topics
            st.markdown("---")
            st.subheader("🏷️ Topics Covered")
            topic_cols = st.columns(min(max(len(result["topics"]), 1), 3))
            for i, topic in enumerate(result["topics"]):
                with topic_cols[i % len(topic_cols)]:
                    st.metric("", topic)
            
            # Guest info
            if result["guest_info"]:
                st.markdown("---")
                st.subheader("👤 Guest Information")
                st.write(result["guest_info"])
            
            # Export and reset buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Export Notes", use_container_width=True):
                    # Create export text
                    export_text = f"""NOTES EXPORT
{'='*50}

SUMMARY
{'-'*50}
{result['summary']}

KEY TAKEAWAYS
{'-'*50}
{chr(10).join([f"{i}. {t}" for i, t in enumerate(result['takeaways'], 1)])}

HIGHLIGHTS
{'-'*50}
{chr(10).join([f"{i}. {h}" for i, h in enumerate(result['highlights'], 1)])}

TOPICS COVERED
{'-'*50}
{chr(10).join([f"• {t}" for t in result['topics']])}

GUEST INFORMATION
{'-'*50}
{result['guest_info'] if result['guest_info'] else 'Not mentioned'}

FULL TRANSCRIPT
{'-'*50}
{st.session_state.transcript}

Generated by Podcast Notes Agent
"""
                    st.download_button(
                        label="📥 Download TXT",
                        data=export_text,
                        file_name=f"{content_type}_notes.txt",
                        mime="text/plain"
                    )
            
            with col2:
                if st.button("📊 Export JSON", use_container_width=True):
                    export_json = {
                        "summary": result["summary"],
                        "takeaways": result["takeaways"],
                        "highlights": result["highlights"],
                        "topics": result["topics"],
                        "guest_info": result["guest_info"],
                        "transcript": st.session_state.transcript
                    }
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(export_json, indent=2),
                        file_name=f"{content_type}_notes.json",
                        mime="application/json"
                    )
            
            with col3:
                if st.button("🔄 New Content", use_container_width=True):
                    st.session_state.transcript = ""
                    st.session_state.analysis_result = None
                    st.session_state.uploaded_file_name = ""
                    st.session_state.uploaded_video_name = ""
                    st.rerun()
        
        elif st.session_state.analysis_result and not st.session_state.analysis_result["success"]:
            st.error(f"❌ Analysis failed: {st.session_state.analysis_result['error']}")
    
    else:
        st.info("👉 Transcribe your content first to see analysis")

with tab3:
    st.subheader("📚 How to Use")
    st.markdown("""
    ### Content Modes
    - **🎙️ Podcast Mode**: Upload audio files directly.
    - **🎬 Video Mode**: Upload video files to automatically extract their audio and process.
    - **🎥 YouTube Mode**: (Coming Soon) Process videos directly from YouTube URLs.
    
    ### Features
    - 🎙️ **Transcription**: Converts audio/video to text using OpenAI Whisper
    - ✨ **Analysis**: Extracts key insights using GPT-4o
    - 📋 **Summary**: 2-3 paragraph executive summary
    - 💡 **Takeaways**: 3-5 actionable key learnings
    - ⭐ **Highlights**: 3-5 memorable quotes or moments
    - 🏷️ **Topics**: Main themes covered
    - 👤 **Guest Info**: Information about speakers
    - 💾 **Export**: Download as TXT or JSON
    
    ### Supported Formats
    - **Audio**: MP3, WAV, M4A, OGG, FLAC
    - **Video**: MP4, WebM, MKV
    
    ### API Keys Used
    - **Whisper API** (for transcription)
    - **GPT-4o** (for analysis with JSON output)
    """)

# TEACH MODE
if show_teach_mode:
    st.markdown("---")
    st.markdown("## 👨‍🏫 Teach Mode: How It Works")
    
    if st.session_state.last_system_prompt:
        with st.expander("🔧 System Prompt for Analysis", expanded=False):
            st.markdown("*This prompt tells GPT-4o how to analyze content:*")
            st.code(st.session_state.last_system_prompt, language="text")
        
        with st.expander("📤 Raw API Response (JSON)", expanded=False):
            st.markdown("*Raw JSON response from GPT-4o before parsing:*")
            st.code(st.session_state.last_raw_json, language="json")
    
    if st.session_state.transcription_request:
        with st.expander("🎙️ Transcription API Request", expanded=False):
            st.markdown("*Parameters sent to Whisper API:*")
            st.code(json.dumps(st.session_state.transcription_request, indent=2), language="json")

# Dummy WSGI application to satisfy Vercel's serverless function requirement.
# Streamlit requires WebSockets and persistent processes, which Vercel Serverless Functions
# do not support. This WSGI app will return a helpful error message if accessed via Vercel.
def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b"This is a Streamlit application. Streamlit requires persistent WebSockets and cannot be hosted on Vercel's Serverless Functions. Please deploy this repository using Streamlit Community Cloud, Google Cloud Run, or Render."]

application = app
handler = app

