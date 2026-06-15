import os
import time
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from youtube_client import get_authenticated_service, get_recent_videos, update_video_metadata
from ai_generator import generate_metadata
from email_notifier import send_email_notification
from whatsapp_notifier import send_whatsapp_message
from comment_manager import get_unreplied_comments, generate_reply, post_reply

# Load environment variables
load_dotenv()

CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# File to keep track of processed videos so we don't process them again
PROCESSED_VIDEOS_FILE = "processed_videos.txt"

def load_processed_videos():
    if not os.path.exists(PROCESSED_VIDEOS_FILE):
        return set()
    with open(PROCESSED_VIDEOS_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_processed_video(video_id):
    with open(PROCESSED_VIDEOS_FILE, "a") as f:
        f.write(f"{video_id}\n")

def main():
    print("Starting YouTube Metadata Automation Bot...")
    if not CHANNEL_ID or CHANNEL_ID == "YOUR_CHANNEL_ID_HERE":
        print("Error: Please set YOUTUBE_CHANNEL_ID in your .env file.")
        return
        
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "YOUR_GEMINI_API_KEY_HERE":
        print("Error: Please set GEMINI_API_KEY in your .env file.")
        return

    # Authenticate with YouTube
    try:
        youtube = get_authenticated_service()
        print("Successfully authenticated with YouTube.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    print(f"Monitoring channel: {CHANNEL_ID} every {POLL_INTERVAL} seconds...")
    print(f"DRY_RUN mode is: {'ON (no changes will be made to YouTube)' if DRY_RUN else 'OFF (videos will be updated)'}")

    while True:
        try:
            # 1. Fetch recent videos
            recent_videos = get_recent_videos(youtube, CHANNEL_ID, max_results=5)
            processed_videos = load_processed_videos()
            
            for video in recent_videos:
                video_id = video['video_id']
                
                # Check if we have already processed this video based on the tag
                if video_id in processed_videos or '#OptimisedbyBOSS' in video.get('tags', []):
                    print(f"Skipping {video_id} - already processed (found in processed list or has #OptimisedbyBOSS tag).")
                    continue
                    
                print(f"\nFound new video! ID: {video_id} | Title: {video['title']}")
                
                # 2. Generate new metadata using AI
                print("Generating optimized metadata with AI...")
                new_metadata = generate_metadata(video['title'], video['description'])
                
                if not new_metadata:
                    print("Failed to generate metadata, skipping this video.")
                    continue
                    
                print("--- AI Generated Content ---")
                print(f"Title: {new_metadata.get('title')}")
                print(f"Tags: {', '.join(new_metadata.get('tags', []))}")
                print("----------------------------")
                
                # 3. Update the video on YouTube
                if not DRY_RUN:
                    print(f"Updating video {video_id} on YouTube...")
                    success = update_video_metadata(
                        youtube, 
                        video_id, 
                        new_metadata.get('title'), 
                        new_metadata.get('description'), 
                        new_metadata.get('tags')
                    )
                    
                    if success:
                        save_processed_video(video_id)
                        
                        shorts_text = "\n".join(new_metadata.get('shorts_ideas', []))
                        body = f"The YouTube Description Bot has successfully optimized and updated the video: '{new_metadata.get('title')}'.\n\nVideo ID: {video_id}\nLink: https://www.youtube.com/watch?v={video_id}\n\nShorts Ideas:\n{shorts_text}"
                        send_email_notification(f"TAGS ADDED: {new_metadata.get('title')}", body)
                        send_whatsapp_message(f"✅ Video Optimized: {new_metadata.get('title')}\n\nShorts Ideas:\n{shorts_text}")
                else:
                    print(f"DRY RUN: Skipping YouTube update for {video_id}. Marking as processed.")
                    # Even in dry run, we mark it as processed to avoid infinite loops during testing
                    save_processed_video(video_id)
            # 4. Check for comments on recent videos
            print("Checking for unreplied comments...")
            for video in recent_videos:
                video_id = video['video_id']
                unreplied_comments = get_unreplied_comments(youtube, video_id)
                for comment in unreplied_comments:
                    print(f"Generating reply for comment by {comment['author']}...")
                    reply_text = generate_reply(comment['text'], video['title'])
                    if reply_text and not DRY_RUN:
                        if post_reply(youtube, comment['id'], reply_text):
                            body = f"Replied to {comment['author']} on video '{video['title']}'.\n\nComment: {comment['text']}\nReply: {reply_text}"
                            send_email_notification(f"Replied on Comment: {video['title']}", body)
                            send_whatsapp_message(f"💬 Replied to {comment['author']} on {video['title']}")
                    elif reply_text and DRY_RUN:
                        print(f"DRY RUN: Would have replied to {comment['author']}: {reply_text}")

            if os.getenv("GITHUB_ACTIONS"):
                print("Running in GitHub Actions mode, completing single run and exiting.")
                break
                
            print(f"Sleeping for {POLL_INTERVAL} seconds...")
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"An error occurred during polling: {e}")
            if os.getenv("GITHUB_ACTIONS"):
                raise e
            print("Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()
