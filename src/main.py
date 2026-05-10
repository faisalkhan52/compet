import os
from dotenv import load_dotenv
from openai import OpenAI
from transcriber import transcribe_audio
from summarizer import generate_podcast_analysis
from video_extractor import extract_audio_from_video

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found in .env")
    print("Please create a .env file with your OpenAI API key")
    exit(1)

client = OpenAI(api_key=api_key)

print("✅ Podcast Notes Agent initialized. API key loaded.")

def display_results(transcript_result, analysis_result):
    transcript = transcript_result["text"]
    print(f"✅ Transcription complete!")
    print(f"📊 Transcript length: {len(transcript)} characters")
    print(f"\n📖 Transcript preview (first 300 chars):\n{transcript[:300]}...\n")
    
    print(f"{'='*60}")
    print("📊 STEP 2: ANALYZING CONTENT")
    print('='*60)
    
    if not analysis_result["success"]:
        print(f"❌ Analysis error: {analysis_result['error']}")
        return
        
    print("✅ Analysis complete!\n")
    
    print(f"{'='*60}")
    print("📋 SUMMARY")
    print('='*60)
    print(analysis_result["summary"])
    
    print(f"\n{'='*60}")
    print("💡 KEY TAKEAWAYS")
    print('='*60)
    for i, takeaway in enumerate(analysis_result["takeaways"], 1):
        print(f"{i}. {takeaway}")
    
    print(f"\n{'='*60}")
    print("⭐ HIGHLIGHTS")
    print('='*60)
    for i, highlight in enumerate(analysis_result["highlights"], 1):
        print(f"{i}. {highlight}")
    
    print(f"\n{'='*60}")
    print("🏷️  TOPICS COVERED")
    print('='*60)
    for topic in analysis_result["topics"]:
        print(f"• {topic}")
    
    if analysis_result["guest_info"]:
        print(f"\n{'='*60}")
        print("👤 GUEST INFORMATION")
        print('='*60)
        print(analysis_result["guest_info"])
    
    print(f"\n{'='*60}")
    print("✨ NOTES GENERATED SUCCESSFULLY")
    print('='*60)


def process_podcast(audio_path: str):
    if not os.path.exists(audio_path):
        print(f"\n⚠️  Sample audio file not found: {audio_path}")
        return
        
    print(f"\n{'='*60}")
    print("📝 STEP 1: TRANSCRIBING PODCAST")
    print('='*60)
    
    transcript_result = transcribe_audio(audio_path, source_type="podcast")
    if not transcript_result["success"]:
        print(f"❌ Transcription error: {transcript_result['error']}")
        return
        
    analysis_result = generate_podcast_analysis(transcript_result["text"], content_type="podcast")
    display_results(transcript_result, analysis_result)


def process_video(video_path: str):
    if not os.path.exists(video_path):
        print(f"\n⚠️  Video file not found: {video_path}")
        return
        
    print(f"\n{'='*60}")
    print("📝 STEP 1: EXTRACTING AUDIO FROM VIDEO")
    print('='*60)
    
    extraction_result = extract_audio_from_video(video_path)
    if not extraction_result["success"]:
        print(f"❌ Extraction error: {extraction_result['error']}")
        return
        
    audio_path = extraction_result["file_path"]
    print(f"✅ Audio extracted to {audio_path}")
    
    print(f"\n{'='*60}")
    print("📝 STEP 2: TRANSCRIBING EXTRACTED AUDIO")
    print('='*60)
    
    transcript_result = transcribe_audio(audio_path, source_type="video")
    if not transcript_result["success"]:
        print(f"❌ Transcription error: {transcript_result['error']}")
        return
        
    analysis_result = generate_podcast_analysis(transcript_result["text"], content_type="video")
    display_results(transcript_result, analysis_result)

def process_youtube(url: str):
    print("YouTube processing not fully implemented yet.")

def main():
    # Example usage
    sample_audio = "uploads/sample_podcast.mp3"
    if os.path.exists(sample_audio):
        process_podcast(sample_audio)
    else:
        print(f"No sample podcast at {sample_audio} to process.")

if __name__ == "__main__":
    main()

# Dummy WSGI application to satisfy Vercel's serverless function requirement.
def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b"CLI entrypoint. This is a Streamlit application. Streamlit requires persistent WebSockets and cannot be hosted on Vercel's Serverless Functions. Please deploy this repository using Streamlit Community Cloud, Google Cloud Run, or Render."]

application = app
handler = app
