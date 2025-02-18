# Fetches all transcripts from a video metadata JSON created by video_metadata.py.
import os
import random
import time
import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

VOD_JSON = 'YUY_VOD_metadata.json'

formatter = JSONFormatter()

def retrieve_transcript(filename, youtube_id):
    transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
    json_format = formatter.format_transcript(transcript, indent=2)

    with open(filename, 'w', encoding='utf-8') as json_file:
        json_file.write(json_format)

with open(VOD_JSON, 'r') as file:
    vods = json.load(file)

for i in range(len(vods)):
    delay = random.randint(30, 60) # Delay can be shorter and may not be necessary at all - just being extra careful
    youtube_id = vods[i]['videoId']
    filename = f"../transcripts/VOD_{youtube_id}.json"
    if os.path.isfile(filename) is False:
        time.sleep(delay) # +/-
        try:
            retrieve_transcript(filename=filename, youtube_id=youtube_id)
        except:
            print(f"Transcript not found for {youtube_id}. Skipping.")
    else:
        print(f"{youtube_id} transcript already exists. Skipping.")
