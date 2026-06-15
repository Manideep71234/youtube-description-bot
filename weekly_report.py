import os
from youtube_client import get_authenticated_service
import google.generativeai as genai
from email_notifier import send_email_notification
from whatsapp_notifier import send_whatsapp_message
from telegram_notifier import send_telegram_message
from dotenv import load_dotenv

load_dotenv()

def get_channel_stats(youtube, channel_id):
    # Get channel total views, subs, videos
    response = youtube.channels().list(
        part="statistics",
        id=channel_id
    ).execute()
    if response.get("items"):
        return response["items"][0]["statistics"]
    return {}

def get_top_videos(youtube, channel_id):
    # Find the uploads playlist
    response = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    uploads_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Get recent videos
    playlist_response = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_id,
        maxResults=50
    ).execute()

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_response.get("items", [])]
    
    if not video_ids:
        return []

    # Get stats for those videos
    videos_response = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    ).execute()

    videos = []
    for item in videos_response.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        })
        
    # Sort by views descending
    videos.sort(key=lambda x: x["views"], reverse=True)
    return videos[:10]  # Top 10

def generate_report(stats, top_videos):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    videos_data = "\n".join([f"- {v['title']} (Views: {v['views']}, Likes: {v['likes']})" for v in top_videos])
    
    prompt = f"""
    You are an expert YouTube Channel Analyst. Analyze the performance of this channel.
    
    Channel Lifetime Stats:
    - Total Views: {stats.get('viewCount')}
    - Total Subscribers: {stats.get('subscriberCount')}
    - Total Videos: {stats.get('videoCount')}
    
    Top Recent Videos (by views):
    {videos_data}
    
    Write a weekly performance report email. Include:
    1. A brief summary of channel growth.
    2. An analysis of the most seen topics based on the top videos.
    3. An analysis of the language(s) mostly seen.
    4. Recommendations for next week's content based on what's working.
    
    Keep it professional, encouraging, and easy to read.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating report: {e}")
        return "Error generating the AI report."

def main():
    print("Generating Weekly Report...")
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    youtube = get_authenticated_service()
    
    stats = get_channel_stats(youtube, channel_id)
    top_videos = get_top_videos(youtube, channel_id)
    
    report_text = generate_report(stats, top_videos)
    
    print("Sending notifications...")
    send_email_notification("📈 Your Weekly YouTube Performance Report", report_text)
    
    # Send a short WhatsApp and Telegram summary
    wa_summary = f"📈 Weekly YouTube Report is ready!\n\nTop Video: {top_videos[0]['title']} ({top_videos[0]['views']} views).\n\nCheck your email for the full analysis of topics and languages!"
    send_whatsapp_message(wa_summary)
    send_telegram_message(f"📈 <b>Weekly YouTube Report is ready!</b>\n\nTop Video: {top_videos[0]['title']} ({top_videos[0]['views']} views).\n\n<i>Check your email for the full analysis of topics and languages!</i>")
    
    print("Done!")

if __name__ == "__main__":
    main()
