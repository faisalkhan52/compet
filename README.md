# 🎤 Podcast Notes Agent

A Python application that transcribes podcast audio files and generates AI-powered highlights, key takeaways, and summaries using OpenAI.

## Features

- 🎙️ Audio transcription (MP3, WAV, M4A, OGG, FLAC) using Whisper API
- ✨ AI-generated highlights and key takeaways
- 📋 Executive summary generation
- 🏷️ Topic extraction
- 👤 Guest information detection
- 💾 Export notes as TXT file
- 👨🏫 Teach mode for learning how prompts work

## Setup

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key: `OPENAI_API_KEY=sk-proj-...`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `streamlit run src/app.py`

## Usage

1. Upload a podcast audio file (MP3, WAV, M4A, OGG, FLAC)
2. Click "Transcribe Podcast" to convert audio to text
3. Click "Generate Highlights & Takeaways" to analyze
4. View summary, key takeaways, highlights, and topics
5. Export notes as TXT file or process another podcast

## API Requirements

- OpenAI API Key (from https://platform.openai.com/account/api-keys)
- Models used:
  - `whisper-1` for audio transcription
  - `gpt-4o` for analysis with JSON output

## Project Structure

- `src/main.py` - Entry point and main script
- `src/transcriber.py` - Audio to text transcription module
- `src/summarizer.py` - Podcast analysis and summarization module
- `src/app.py` - Streamlit web UI
- `uploads/` - Directory for uploaded audio files
- `output/` - Directory for exported notes
