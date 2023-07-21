from .celery import app

from dotenv import load_dotenv, find_dotenv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import spotipy

load_dotenv(find_dotenv())

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


# .delay()
@app.task
def TransferPlaylist(sp_token, playlist_id, ignore_result = True):

### 1: Youtube - Get Song Titles ###
   
    youtube = build('youtube', 'v3', developerKey=GOOGLE_API_KEY)

    # Retrieve the first page of playlist items
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults= 50
    )

    response_for_title = youtube.playlists().list(
        part='snippet', 
        id=playlist_id,
        fields='items(snippet(title))'
    ).execute()

    if response_for_title['items'][0]['snippet']['title']:
        playlist_name = response_for_title['items'][0]['snippet']['title']
    else:
        playlist_name = response['items'][0]['snippet']['title']

        

    response = request.execute()

    # Initialize an empty list to store the video titles
    video_titles = []


    while response:
        # Extract video titles from the response
        for item in response['items']:
            video_titles.append(item['snippet']['title'])

        # Check if there are more pages to retrieve
        if 'nextPageToken' in response:
            next_page_token = response['nextPageToken']
            # Retrieve the next page of playlist items
            response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
        else:
            break


### 2: Spotify - Create New Playlist ###

    sp = spotipy.Spotify(auth=sp_token)
    
    # Get the user access token
    user_id = sp.me()['id']


    data = {
        'name': playlist_name,
        'public': True,
        'description': "Imported From Youtube"
    }

    response = sp.user_playlist_create(user=user_id, **data)

    playlist_id = response['id']

### 3: Spotify - Search Songs ###
    
    track_ids = []

    for title in video_titles:
        search_result = sp.search(q=title, type='track', limit=1)
        if search_result['tracks']['items']:
            track_ids.append(search_result['tracks']['items'][0]['id'])


### 4: Spotify - Add To Playlist ###

    # Split the list of track IDs into smaller batches of 100 tracks each for spotify rules
    batch_size = 100
    track_batches = [track_ids[i:i + batch_size] for i in range(0, len(track_ids), batch_size)]
    
    
    for track_batch in track_batches:
        sp.playlist_add_items(playlist_id, track_batch)




