# Yupil Search
A simple Discord bot for searching YouTube VOD transcripts.

## Steps
1. Acquire a JSON of all-video metadata from a specified YouTube channel using the [google-api-python-client](https://github.com/googleapis/google-api-python-client) with a [YouTube Data API v3](https://developers.google.com/youtube/registering_an_application) API key: **scripts/video_metadata.py**
2. Fetch VOD transcripts using the metadata JSON from step 1 and [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api): **scripts/fetch_transcripts.py**
3. Create a local SQLite database compiling the individual VOD transcript JSON data from step 2: **scripts/make_db.py**
4. Run bot for Discord integration and fuzzy search of VOD transcripts: **YupilSearch.py**
