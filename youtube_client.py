import os
import pickle
# pyrefly: ignore [missing-import]
from google_auth_oauthlib.flow import InstalledAppFlow
# pyrefly: ignore [missing-import]
from google.auth.transport.requests import Request
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated_service():
    """Authenticates the user and returns a YouTube service object."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secret.json'):
                raise FileNotFoundError(
                    "client_secret.json is missing! \n"
                    "Please go to Google Cloud Console (console.cloud.google.com), \n"
                    "create a project, enable 'YouTube Data API v3', create an OAuth 2.0 Client ID (Desktop app), \n"
                    "download the JSON, and save it as 'client_secret.json' in this folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            # This opens a browser window for you to login and grant access to the app
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)

def get_recent_videos(youtube, channel_id, max_results=5):
    """Fetches the most recent videos uploaded to the specified channel."""
    # First, get the 'uploads' playlist ID for the channel
    channel_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    if not channel_response.get('items'):
        print(f"No channel found with ID: {channel_id}")
        return []
        
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Retrieve recent videos from the uploads playlist
    playlistitems_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=max_results
    ).execute()
    
    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlistitems_response.get('items', [])]
    
    if not video_ids:
        return []
        
    videos_response = youtube.videos().list(
        part='snippet',
        id=','.join(video_ids)
    ).execute()
    
    videos = []
    for item in videos_response.get('items', []):
        videos.append({
            'video_id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'published_at': item['snippet']['publishedAt'],
            'tags': item['snippet'].get('tags', [])
        })
        
    return videos

def update_video_metadata(youtube, video_id, new_title, new_description, new_tags):
    """Updates the video title, description, and tags."""
    # First, fetch the current video snippet to ensure we preserve categoryId etc.
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    
    if not video_response.get('items'):
        print(f"Video {video_id} not found.")
        return False
        
    snippet = video_response['items'][0]['snippet']
    
    # Update fields
    if new_title:
        snippet['title'] = new_title
    if new_description:
        snippet['description'] = new_description
    if new_tags:
        snippet['tags'] = new_tags
    
    # Push update
    update_response = youtube.videos().update(
        part='snippet',
        body={
            'id': video_id,
            'snippet': snippet
        }
    ).execute()
    
    print(f"Successfully updated video: {video_id}")
    return True
