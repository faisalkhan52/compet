import os
import re
import shutil
import yt_dlp


def is_valid_youtube_url(url: str) -> bool:
    """Check if a URL is a valid YouTube link."""
    patterns = [
        r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+",
        r"(https?://)?(www\.)?youtube\.com/shorts/[\w\-]+",
    ]
    return any(re.search(p, url) for p in patterns)


def _ffmpeg_available() -> bool:
    """Return True if ffmpeg is available on PATH."""
    return shutil.which("ffmpeg") is not None


def get_youtube_info(url: str) -> dict:
    """
    Fetch metadata for a YouTube video without downloading it.

    Returns:
        dict with keys: success, title, duration, uploader, thumbnail, error
    """
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "success": True,
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "thumbnail": info.get("thumbnail", ""),
                "error": None,
            }
    except Exception as e:
        return {
            "success": False,
            "title": None,
            "duration": 0,
            "uploader": None,
            "thumbnail": None,
            "error": str(e),
        }


def download_youtube_audio(url: str, output_dir: str = "downloads") -> dict:
    """
    Download the audio track of a YouTube video.

    Strategy:
    - If ffmpeg is available: download best audio and convert to MP3.
    - If ffmpeg is NOT available: download best native audio (m4a/webm/opus)
      without any post-processing. Whisper API accepts all these formats.

    Args:
        url: YouTube video URL
        output_dir: Directory to save the downloaded audio

    Returns:
        dict with keys: success, file_path, title, duration, error
    """
    try:
        if not is_valid_youtube_url(url):
            return {
                "success": False,
                "file_path": None,
                "title": None,
                "duration": 0,
                "error": "Invalid YouTube URL. Please enter a valid YouTube link.",
            }

        os.makedirs(output_dir, exist_ok=True)
        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        ffmpeg = _ffmpeg_available()

        if ffmpeg:
            # Full quality: download best audio + convert to MP3 via ffmpeg
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        else:
            # No ffmpeg: prefer m4a (natively supported by Whisper), fall back to any audio
            ydl_opts = {
                "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
                # No postprocessors — skip ffmpeg entirely
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "youtube_audio")
            duration = info.get("duration", 0)
            # yt-dlp tells us the actual extension used
            ext = info.get("ext", "m4a") if not ffmpeg else "mp3"

        # Resolve actual file path
        safe_title = yt_dlp.utils.sanitize_filename(title)
        file_path = os.path.join(output_dir, f"{safe_title}.{ext}")

        # Fallback: pick the most recently modified audio file in output_dir
        if not os.path.exists(file_path):
            audio_exts = (".mp3", ".m4a", ".webm", ".opus", ".ogg", ".wav")
            audio_files = sorted(
                [f for f in os.listdir(output_dir) if f.endswith(audio_exts)],
                key=lambda f: os.path.getmtime(os.path.join(output_dir, f)),
                reverse=True,
            )
            if audio_files:
                file_path = os.path.join(output_dir, audio_files[0])
            else:
                return {
                    "success": False,
                    "file_path": None,
                    "title": title,
                    "duration": duration,
                    "error": "Download appeared to succeed but audio file could not be located.",
                }

        return {
            "success": True,
            "file_path": file_path,
            "title": title,
            "duration": duration,
            "error": None,
        }

    except yt_dlp.utils.DownloadError as e:
        return {
            "success": False,
            "file_path": None,
            "title": None,
            "duration": 0,
            "error": f"Download failed: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "title": None,
            "duration": 0,
            "error": f"Unexpected error: {str(e)}",
        }
