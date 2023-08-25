from .celery import app

from dotenv import load_dotenv, find_dotenv
from googleapiclient.discovery import build
from django.conf import settings

import os
import spotipy
import requests
import boto3
import uuid

load_dotenv(find_dotenv())

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


@app.task
def download_and_store_image(url):
    try:
        s3 = boto3.client(
            's3',    
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME


        img = requests.get(url).content
        file_name = str(uuid.uuid4()) + '.png'
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    

        with open(file_path, 'wb') as handler:
            handler.write(img)

        s3.upload_file(file_path, bucket_name, f'media/{file_name}', ExtraArgs={'ACL': 'public-read'})
        os.remove(file_path)

    except Exception as e:
        print("Error: ", e)
    

@app.task(bind=True)
def TransferPlaylist(self, sp_token, playlist_id, ignore_result=True):
    try:
        # __ 1: Youtube - Get Song Titles

        youtube = build("youtube", "v3", developerKey=GOOGLE_API_KEY)

        # Retrieve the first page of playlist items
        request = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50
        )

        response_for_title = (
            youtube.playlists()
            .list(part="snippet,contentDetails", id=playlist_id)
            .execute()
        )

        response = request.execute()

        try: # Get title from playlist
            playlist_name = response_for_title["items"][0]["snippet"]["title"]

        except Exception: # Get title from first video
            playlist_name = response["items"][0]["snippet"]["title"]

        # Initialize an empty list to store the video titles
        video_titles = []


        while response:
            # Extract video titles from the response
            for item in response["items"]:
                if item["snippet"]["title"] != "Private video" and item["snippet"]["title"] != "Deleted video":
                    video_titles.append(item["snippet"]["title"])


            # Check if there are more pages to retrieve
            if "nextPageToken" in response:
                next_page_token = response["nextPageToken"]
                # Retrieve the next page of playlist items
                response = (
                    youtube.playlistItems()
                    .list(
                        part="snippet",
                        playlistId=playlist_id,
                        maxResults=50,
                        pageToken=next_page_token,
                    )
                    .execute()
                )
            else:
                break

        # __ 2: Spotify - Create New Playlist

        sp = spotipy.Spotify(auth=sp_token)

        # Get the user access token
        user_id = sp.me()["id"]

        data = {
            "name": playlist_name,
            "public": True,
            "description": "Imported From Youtube",
        }

        response = sp.user_playlist_create(user=user_id, **data)

        playlist_id = response["id"]

        # __ 3: Spotify - Search Songs

        track_ids = []
        for title in video_titles:
            search_result = sp.search(q=title, type="track", limit=1)
            if search_result["tracks"]["items"]:
                track_ids.append(search_result["tracks"]["items"][0]["id"])

        # __ 4: Spotify - Add To Playlist

        # Split the list of track IDs into smaller batches of 100 tracks each for spotify rules
        batch_size = 100
        track_batches = [
            track_ids[i : i + batch_size] for i in range(0, len(track_ids), batch_size)
        ]
        for track_batch in track_batches:
            sp.playlist_add_items(playlist_id, track_batch)

    except Exception as e:
        print("Task failed", e)
