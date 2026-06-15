import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from youtube_client import get_authenticated_service

def get_unreplied_comments(youtube, video_id, max_results=20):
    try:
        response = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        ).execute()
        
        unreplied = []
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comment_id = item["id"]
            text = snippet["textDisplay"]
            author = snippet["authorDisplayName"]
            
            # Check if the bot has already replied
            replies = item.get("replies", {}).get("comments", [])
            bot_replied = any(reply["snippet"]["authorChannelId"]["value"] == os.getenv("YOUTUBE_CHANNEL_ID") for reply in replies)
            
            if not bot_replied:
                unreplied.append({
                    "id": comment_id,
                    "text": text,
                    "author": author
                })
        return unreplied
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def generate_reply(comment_text, video_title):
    prompt = f"""
    You are managing the YouTube channel for a video titled '{video_title}'.
    A viewer just left this comment: "{comment_text}"
    
    Analyze the tone of the comment. If it's a question/query, adopt a highly helpful and informative persona.
    If it's praise, be appreciative and warm. If it's funny, reply with a witty/funny tone.
    Always be professional but conversational.
    
    Write a short, engaging reply to this comment. Do NOT use emojis that might render poorly, stick to simple text.
    Return ONLY the text of the reply.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating comment reply: {e}")
        return None

def post_reply(youtube, comment_id, reply_text):
    try:
        youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": reply_text
                }
            }
        ).execute()
        return True
    except Exception as e:
        print(f"Error posting reply: {e}")
        return False
