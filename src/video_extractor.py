import os
from moviepy.editor import VideoFileClip

def extract_audio_from_video(video_path: str) -> dict:
    """
    Extracts the audio track from a video file and saves it as an MP3.
    
    Args:
        video_path: Path to the video file (e.g., mp4, webm, mkv)
        
    Returns:
        Dictionary with keys:
        - success (bool): Whether extraction was successful
        - file_path (str): Path to the extracted audio file
        - duration (float): Duration of the audio in seconds
        - error (str): Error message if failed
    """
    try:
        # Validate file exists
        if not os.path.exists(video_path):
            return {
                "success": False,
                "file_path": None,
                "duration": 0,
                "error": f"Video file not found: {video_path}"
            }
        
        # Ensure downloads directory exists
        os.makedirs("downloads", exist_ok=True)
        
        # Generate output path
        base_name = os.path.basename(video_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_path = os.path.join("downloads", f"{name_without_ext}.mp3")
        
        # Extract audio using moviepy
        video = VideoFileClip(video_path)
        
        if video.audio is None:
            video.close()
            return {
                "success": False,
                "file_path": None,
                "duration": 0,
                "error": "No audio track found in the video file."
            }
            
        audio = video.audio
        duration = audio.duration
        
        # Write to mp3 file
        audio.write_audiofile(output_path, logger=None) # logger=None to suppress moviepy prints
        
        # Close clips to free resources
        audio.close()
        video.close()
        
        return {
            "success": True,
            "file_path": output_path,
            "duration": duration,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "duration": 0,
            "error": f"Failed to extract audio from video: {str(e)}"
        }
