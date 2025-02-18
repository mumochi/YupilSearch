# Uses the Google YouTube Data API to retrieve metadata for videos published on a specified channel.
import json
from googleapiclient.discovery import build

API_KEY = '' # Google YouTube Data API v3 key
CHANNEL_ID = '' # YouTube channel ID (Share channel -> Copy channel ID)
VOD_JSON = '../YUY_VOD_metadata.json'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_videos(channel_id):
        videos = []
        next_page_token = None

        while True:
            request = youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=next_page_token,
                    type="video"
                    )
            response = request.execute()

            for item in response['items']:
                videos.append({
                    'videoId': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt']
                    })

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

        return videos

all_videos = get_channel_videos(CHANNEL_ID)

with open(VOD_JSON, 'w', encoding='utf-8') as f:
    json.dump(all_videos, f, ensure_ascii=False, indent=2)
