from django.shortcuts import render, redirect
from django.contrib import messages as msg
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlencode
from django.dispatch import Signal, receiver
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

from .forms import CreateUserForm
from .decorators import login_check, not_authenticated_only
from .models import user_data_storage, User


import datetime
import random
import os
import re
import openai
import backoff
import pytube
import requests
import asyncio
import json
import time


from pytube import YouTube
from pytube.cli import on_progress
from datetime import datetime as dt
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote, unquote
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil.parser import isoparse

# Hide it from Github
load_dotenv(find_dotenv())

openai.api_key = os.environ.get("OPENAI_API_KEY")
google_api_key = os.environ.get("GOOGLE_API_KEY")

youtube = build('youtube', 'v3', developerKey=google_api_key)


@login_check
def main_page(request, login_context):
    context = {}

    # User download history
    if "username" in login_context:
        username = login_context["username"]
        storage = user_data_storage.objects.get(
            user=User.objects.get(username=username)
        )

        # Use download history for slides on the main page
        # Get random items from history
        # Eliminate repetitions

        Download_videos_informations = []

        Download_history = random.sample(
            storage.download_history, len(storage.download_history)
        )

        # Limit to 10 slides / random 10 elements from history
        Download_history = Download_history[:10]  

        for item in Download_history:
            it_is_in_dict = False

            # First item in download history (always add)
            if Download_videos_informations == []:
                Download_videos_informations.append(
                    {
                        "title": item[1],
                        "thumbnail": item[2],
                        "publish_date": item[3],
                        "link": item[0],
                    }
                )
            else:  
                # If it's not the first item, check if already exists
                for dictionary in Download_videos_informations:
                    if item[0] in dictionary.values():
                        it_is_in_dict = True

                
                if it_is_in_dict == False:
                    Download_videos_informations.append(
                        {
                            "title": item[1],
                            "thumbnail": item[2],
                            "publish_date": item[3],
                            "link": item[0],
                        }
                    )

        context.update({"number_of_links": range(0, len(Download_videos_informations))})
        context.update({"videos_informations": Download_videos_informations})

    context.update(login_context)

    if request.method == "POST":
        link = request.POST.get("sended_link")
        return redirect("download_page", parameter=link)

    return render(request, "main_page.html", context)


@login_check
@not_authenticated_only
def login_page(request, login_context):
    form = CreateUserForm()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password1")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            msg.success(request, "Welcome " + username)
            return redirect(main_page)
        else:
            msg.info(request, "Username or Password is incorrect")

    context = {
        "form": form,
    }

    context.update(login_context)

    return render(request, "login_page.html", context)


def logoutUser(request):
    logout(request)
    return redirect(main_page)


@login_check
@not_authenticated_only
def sign_up_page(request, login_context):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")

            # Create data storage for user in the database / avoid not-null by passing 'registered' string

            user_data_storage.objects.create(
                user=User.objects.get(username=user), download_history=["registered"]
            )
            storage = user_data_storage.objects.get(
                user=User.objects.get(username=user)
            )
            storage.download_history.remove("registered")
            storage.save()

            msg.success(request, user + " Welcome on board")
            return redirect(login_page)

    context = {"form": form}

    context.update(login_context)

    return render(request, "sign_up_page.html", context)


# Backoff for sending request again ( sometimes titles can't be found by pytube )
@login_check
@backoff.on_exception(
    backoff.expo, (pytube.exceptions.PytubeError, ValueError), max_time=0.3
)
def download_page(request, login_context, parameter):
    yt = YouTube(parameter, on_progress_callback=on_progress)

    try:
        title = yt.title
        thumbnail = yt.thumbnail_url
        length = str(datetime.timedelta(seconds=yt.length))
        views = f"{yt.views:,}"  # Format numbers 100000 = 100,000 etc.
        publish_date = yt.publish_date
        description = yt.description
    except:
        title = "Could not find or video was deleted by Youtube"
        thumbnail = "couldn't find"
        length = "couldn't find"
        views = "couldn't find"
        publish_date = "couldn't find"
        description = "couldn't find"

    name = parameter.split("-")

    # Store link in user database
    if "username" in login_context:
        username = login_context["username"]
        storage = user_data_storage.objects.get(
            user=User.objects.get(username=username)
        )

        time = dt.now()
        info = [parameter, title, thumbnail, time.strftime("%d/%m/%Y %H:%M")]
        storage.download_history.append(info)
        storage.save()

    # For downloading sd quality video files
    if "sd_quality" in name:
        sd_quality_stream = yt.streams.get_by_resolution("360p")

        if sd_quality_stream == None:
            sd_quality_stream = yt.streams.get_highest_resolution()

        sd_quality_stream.download(output_path="static/", filename="video.mp4")

        return redirect(download_video, parameter=name[0])

    # For downloading highest quality video files
    if "hd_quality" in name:
        hd_quality_stream = yt.streams.get_by_resolution("1080p")

        if hd_quality_stream == None:
            hd_quality_stream = yt.streams.get_highest_resolution()

        hd_quality_stream.download(output_path="static/", filename="video.mp4")

        return redirect(download_video, parameter=name[0])

    # For downloading audio files
    if "mp3" in name:
        mp3_stream = yt.streams.get_audio_only("mp4")

        mp3_stream.download(output_path="static/", filename="audio.mp3")

        return redirect(download_audio, parameter=name[0])

    context = {
        "link": parameter,
        "title": title,
        "views": views,
        "thumbnail": thumbnail,
        "description": description,
        "publish_date": publish_date,
        "length": length,
    }

    context.update(login_context)
    return render(request, "download_page.html", context)


@login_check
def download_video(request, login_context, parameter):
    yt = YouTube(parameter)

    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
    }

    context.update(login_context)

    return render(request, "video_download.html", context)


@login_check
def download_audio(request, login_context, parameter):
    yt = YouTube(parameter)

    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
    }

    context.update(login_context)

    return render(request, "audio_download.html", context)


@login_check
def ai_page(request, login_context, parameter="", parameter_title=""):

    if request.method == "POST":

        description = request.POST.get("description")

    
        try:
            response_data = openai.Image.create(
                prompt=description,
                n=1,
                size="1024x1024"
            )

            link = response_data["data"][0]["url"]

            fixed_link = quote(link, safe=':/?&=%')

        except openai.error.RateLimitError:
            msg.success("Ai model is currently overloaded, please wait a second")
            return redirect(ai_page)


        print(link)
    

        return redirect(ai_page, parameter = fixed_link, parameter_title = description)

    context = {}
    context.update(login_context)

    if parameter != "":
        context.update({
            "image_link": parameter.replace('%25', '%'),
            "image_title" : parameter_title,
        })

    return render(request, "ai_site.html", context)

pageTokens = [None]

async def get_video_comments(video_id, order, maxResults, previousPageID, pageID):

    try:
        # Retrieve the comments for the specified video
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='html',
            order=order,
            maxResults=maxResults,
            pageToken = pageTokens[-1]
        )
        

        # Process the comments
        processed_comments = []

        match (int(pageID) - int(previousPageID)):

            case 1:
                response = await asyncio.to_thread(request.execute)

                if 'nextPageToken' in response:
                    pageTokens.append(response['nextPageToken'])
                    request = youtube.commentThreads().list_next(request, response)

            case 0: 
                pass

            case -1:
                pageTokens.pop()
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='html',
                    order=order,
                    maxResults=maxResults,
                    pageToken = pageTokens[-1]
                )

        response = await asyncio.to_thread(request.execute)

        if 'nextPageToken' not in response:
            processed_comments.append('last_page')


        if 'items' in response:
            for comment in response['items']:
                # Extract the comment snippet
                snippet = comment['snippet']['topLevelComment']['snippet']
                author = snippet['authorDisplayName']
                text = snippet['textDisplay']
                likes = snippet['likeCount']
                profile_image_url = snippet['authorProfileImageUrl']
                publish_date = isoparse(snippet['publishedAt']).strftime('%Y-%m-%d %H:%M:%S')


                # Add the processed comment to the list
                processed_comments.append({
                    'author': author,
                    'text': text,
                    'likes': likes,
                    'profile_image_url': profile_image_url,
                    'publish_date': publish_date
                })

            
        return processed_comments

    except HttpError as e:
        error_message = f'An HTTP error {e.resp.status} occurred: {e.content}'
        raise HttpError(e.resp, error_message)



async def get_video_comments_view_async(video_id, order, maxResults, previousPageID, pageID):

    if not video_id:
        return JsonResponse({'error': 'No video_id parameter provided'}, status=400)

    try:
        comments = await get_video_comments(video_id, order, maxResults, previousPageID, pageID)
        return {'comments': comments}

    except HttpError as e:
        error_message = f'An HTTP error {e.resp.status} occurred: {e.content}'
        return JsonResponse({'error': error_message}, status=500)


@login_check
def comments(request, login_context):
    context = {}

    if request.GET.get("order") != None:
        video_id = "uod9IJ4-47s"    
        order = request.GET.get("order")
        maxResults = request.GET.get("maxResults")
        previousPageID = request.GET.get("previousPageID")
        pageID = request.GET.get("pageID")

        context = {
            'order': order,
            'maxResults': maxResults,
            'pageID': int(pageID)
        }

        if previousPageID == '1' and pageID == '1':
            pageTokens.clear()
            pageTokens.append(None)

        
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comments = loop.run_until_complete(get_video_comments_view_async(video_id, order, maxResults, previousPageID, pageID))


        context.update(comments)
        context.update({'count' : len(comments['comments'])})
        context.update(login_context)


        if 'last_page' in comments['comments']:
            context.update({'last_page': True})
            comments['comments'].remove('last_page')

        return render(request, "comments.html", context)
    
    else:

        context.update(login_context)

        return render(request, "comments.html", context)
