import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_podcast_analysis(transcript: str, content_type: str = "podcast") -> dict:
    """
    Analyze podcast transcript and generate highlights, takeaways, summary.
    
    Uses GPT-4o with structured JSON output to extract:
    - Highlights: Key quotes or important moments
    - Takeaways: Main learnings from the podcast
    - Summary: 2-3 paragraph executive summary
    - Topics: Main topics covered
    - Guest Info: Information about guests (if mentioned)
    
    Args:
        transcript: Full podcast transcript text
    
    Returns:
        Dictionary with keys:
        - success (bool): Whether analysis was successful
        - highlights (list): List of key quotes/moments
        - takeaways (list): List of key learnings
        - summary (str): Executive summary
        - topics (list): Main topics covered
        - guest_info (str): Guest information
        - raw_response (str): Raw JSON from API (for teach mode)
        - system_prompt (str): System prompt used (for teach mode)
        - content_type (str): The type of content analyzed
        - error (str): Error message if failed
    
    Example:
        result = generate_podcast_analysis(transcript)
        if result["success"]:
            print(result["summary"])
            for takeaway in result["takeaways"]:
                print(f"- {takeaway}")
    """
    
    content_label = "video content" if content_type == "video" else "podcast"
    # System prompt for GPT-4o
    system_prompt = f"""You are a professional content analysis expert. Your task is to analyze {content_label} transcripts and extract key insights.

Given a {content_label} transcript, you MUST respond ONLY with a valid JSON object containing exactly these keys:
- highlights: Array of 3-5 key quotes or important moments from the {content_label}
- takeaways: Array of 3-5 main learnings or insights (1-2 sentences each)
- summary: 2-3 paragraph executive summary of the entire {content_label}
- topics: Array of 3-5 main topics or themes covered
- guest_info: Brief description of guests and their roles (empty string if not mentioned)

Rules:
1. Return ONLY the JSON object, no markdown, no backticks, no extra text
2. Each highlight should be a memorable quote or key moment
3. Each takeaway should be actionable and clear
4. Summary should be professional and comprehensive
5. Topics should be descriptive and specific
6. Keep guest_info empty string if no guests are mentioned"""

    user_message = f"Analyze this {content_label} transcript and extract insights:\n\n{transcript}"
    
    try:
        # Call GPT-4o with JSON response format
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract and parse JSON response
        raw_json = response.choices[0].message.content
        analysis = json.loads(raw_json)
        
        return {
            "success": True,
            "highlights": analysis.get("highlights", []),
            "takeaways": analysis.get("takeaways", []),
            "summary": analysis.get("summary", ""),
            "topics": analysis.get("topics", []),
            "guest_info": analysis.get("guest_info", ""),
            "raw_response": raw_json,
            "system_prompt": system_prompt,
            "content_type": content_type,
            "error": None
        }
    
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse JSON response: {str(e)}",
            "highlights": [],
            "takeaways": [],
            "summary": "",
            "topics": [],
            "guest_info": "",
            "raw_response": "",
            "system_prompt": system_prompt,
            "content_type": content_type
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "highlights": [],
            "takeaways": [],
            "summary": "",
            "topics": [],
            "guest_info": "",
            "raw_response": "",
            "system_prompt": system_prompt,
            "content_type": content_type
        }


if __name__ == "__main__":
    # Test summarizer with sample transcript
    sample_transcript = """
    Host: Welcome to the AI podcast. Today we're talking about machine learning.
    Guest: Thanks for having me. Machine learning has revolutionized how we process data.
    Host: Can you explain transformers?
    Guest: Transformers use attention mechanisms to process sequences in parallel, which is much faster than RNNs.
    This has led to breakthroughs in NLP and computer vision.
    Host: What's the most important takeaway?
    Guest: Understanding prompt engineering is crucial for LLMs. The way you phrase your question directly impacts the quality of responses.
    """
    
    print("Testing summarizer...")
    result = generate_podcast_analysis(sample_transcript)
    
    if result["success"]:
        print("✅ Analysis successful!\n")
        print("SUMMARY:")
        print(result["summary"])
        print("\nTAKEAWAYS:")
        for takeaway in result["takeaways"]:
            print(f"- {takeaway}")
    else:
        print(f"❌ ERROR: {result['error']}")
