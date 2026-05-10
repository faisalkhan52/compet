import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file_path: str, source_type: str = "podcast") -> dict:
    """
    Transcribe audio file to text using OpenAI Whisper API.
    
    Args:
        audio_file_path: Path to audio file (mp3, wav, m4a, ogg, flac, etc.)
        source_type: The source of the content ("podcast", "youtube", "video")
    
    Returns:
        Dictionary with keys:
        - success (bool): Whether transcription was successful
        - text (str): Transcribed text
        - duration (int): Duration in seconds (if available)
        - language (str): Detected language code
        - source_type (str): The source type passed in
        - error (str): Error message if failed
    
    Example:
        result = transcribe_audio("uploads/podcast.mp3")
        if result["success"]:
            print(result["text"])
        else:
            print(f"Error: {result['error']}")
    """
    try:
        # Validate file exists
        if not os.path.exists(audio_file_path):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_file_path}",
                "text": "",
                "duration": 0,
                "language": "",
                "source_type": source_type
            }
        
        # Get file size
        file_size = os.path.getsize(audio_file_path)
        max_size = int(os.getenv("MAX_FILE_SIZE", "25000000"))
        
        if file_size > max_size:
            return {
                "success": False,
                "error": f"File size {file_size} exceeds maximum {max_size} bytes",
                "text": "",
                "duration": 0,
                "language": "",
                "source_type": source_type
            }
        
        # Open and transcribe audio file
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        
        return {
            "success": True,
            "text": transcript.text,
            "duration": None,
            "language": "en",
            "source_type": source_type,
            "error": None
        }
    
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "text": "",
            "duration": 0,
            "language": "",
            "source_type": source_type
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Transcription failed: {str(e)}",
            "text": "",
            "duration": 0,
            "language": "",
            "source_type": source_type
        }


if __name__ == "__main__":
    # Test transcriber with sample audio file
    sample_audio = "uploads/sample_podcast.mp3"
    print(f"Testing transcriber with: {sample_audio}")
    result = transcribe_audio(sample_audio)
    
    if result["success"]:
        print("✅ Transcription successful!")
        print(f"Text preview: {result['text'][:200]}...")
    else:
        print(f"❌ ERROR: {result['error']}")
