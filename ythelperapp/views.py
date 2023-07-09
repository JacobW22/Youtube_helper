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

sites_context = {
  "main_page": "<i class='fa-solid fa-download'></i></i>&nbsp; Video Downloader",
  "ai_page": "<i class='fa-regular fa-image'></i>&nbsp; Ai thumbnail generator",
  "comments": "<i class='fa-regular fa-comments'></i>&nbsp; YT comments filtering"
}

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

        for vid_info in Download_history:
            it_is_in_dict = False

            # First item in download history (always add)
            if Download_videos_informations == []:
                Download_videos_informations.append(
                    {
                        "title": vid_info[0],
                        "thumbnail": vid_info[3],
                        "publish_date": vid_info[2],
                        "link": vid_info[1],
                    }
                )
            else:  
                # If it's not the first item, check if already exists
                for dictionary in Download_videos_informations:
                    if vid_info[1] in dictionary.values():
                        it_is_in_dict = True

                
                if it_is_in_dict == False:
                    Download_videos_informations.append(
                        {
                            "title": vid_info[0],
                            "thumbnail": vid_info[3],
                            "publish_date": vid_info[2],
                            "link": vid_info[1],
                        }
                    )

        context.update({"number_of_links": range(0, len(Download_videos_informations))})
        context.update({"videos_informations": Download_videos_informations})

    context.update(login_context)
    context.update({'sites_context': sites_context})

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
            return redirect(login_page)

    context = {
        "form": form,
    }

    context.update(login_context)
    context.update({'sites_context': sites_context})

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
                object_name=str(user)+" storage", user=User.objects.get(username=user), download_history=["registered"], prompts_history=["registered"], filtered_comments_history=["registered"]
            )

            storage = user_data_storage.objects.get(
                user=User.objects.get(username=user)
            )

            storage.download_history.remove("registered")
            storage.prompts_history.remove("registered")
            storage.filtered_comments_history.remove("registered")
            storage.save()

            msg.success(request, user + " Welcome on board")
            return redirect(login_page)

    context = {"form": form}

    context.update(login_context)
    context.update({'sites_context': sites_context})

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

    # Store data in user history
    if "username" in login_context:
        username = login_context["username"]
        storage = user_data_storage.objects.get(
            user=User.objects.get(username=username)
        )

        time = dt.now()
        info = [title, parameter, time.strftime("%d/%m/%Y %H:%M"), thumbnail]
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
    context.update({'sites_context': sites_context})

    return render(request, "download_page.html", context)


@login_check
def download_video(request, login_context, parameter):
    yt = YouTube(parameter)

    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
    }

    context.update(login_context)
    context.update({'sites_context': sites_context})


    return render(request, "video_download.html", context)


@login_check
def download_audio(request, login_context, parameter):
    yt = YouTube(parameter)

    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
    }

    context.update(login_context)
    context.update({'sites_context': sites_context})


    return render(request, "audio_download.html", context)


@login_check
def ai_page(request, login_context, parameter="", parameter_title=""):

    if request.method == "POST":

        description = request.POST.get("description")


        try:
            response_data = openai.Image.create(
                prompt=description + " user profile img",
                n=1,
                size="1024x1024"
            )

            link = response_data["data"][0]["url"]

            fixed_link = quote(link, safe=':/?&=%')

        except openai.error.RateLimitError:
            msg.success("Ai model is currently overloaded, please wait a second")
            return redirect(ai_page)
    


        # Store data in user history
        if "username" in login_context:
            username = login_context["username"]
            storage = user_data_storage.objects.get(
                user=User.objects.get(username=username)
            )

            time = dt.now()
            info = [description, fixed_link.replace('%25', '%'), time.strftime("%d/%m/%Y %H:%M")]
            storage.prompts_history.append(info)
            storage.save()

        return redirect(ai_page, parameter = fixed_link, parameter_title = description)

    context = {}
    context.update(login_context)
    context.update({'sites_context': sites_context})


    if parameter != "":
        context.update({
            "image_link": parameter.replace('%25', '%'),
            "image_title" : parameter_title,
        })

    return render(request, "ai_site.html", context)



pageTokens = [None]
previous_request_previousPageID = [0]
previous_request_pageID = [0]
video_info = {}

async def get_video_comments(video_id, order, maxResults, previousPageID, pageID, searchInput, quotaUser):

    try:
        # Retrieve the comments for the specified video
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='html',
            order=order,
            maxResults=maxResults,
            pageToken = pageTokens[-1],
            quotaUser = quotaUser
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
                    pageToken = pageTokens[-1],
                    quotaUser = quotaUser
                )

        response = await asyncio.to_thread(request.execute)

        if 'nextPageToken' not in response:
            processed_comments.append('last_page')

        if searchInput != "":

            if 'items' in response:
                filtered_comments = [comment for comment in response['items'] if re.search(re.escape(searchInput), comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"], re.IGNORECASE)]

                for comment in filtered_comments:
                    snippet = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    highlighted_comment = re.sub(f'({re.escape(searchInput)})', r'<mark>\1</mark>', snippet, flags=re.IGNORECASE)
                    comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"] = highlighted_comment
                
                for comment in filtered_comments:
                    # Extract the comment snippet
                    snippet = comment['snippet']['topLevelComment']['snippet']


                    author = snippet['authorDisplayName']
                    channel_url = snippet['authorChannelUrl']
                    text = snippet['textDisplay']
                    likes = f"{snippet['likeCount']:,}"
                    profile_image_url = snippet['authorProfileImageUrl']
                    publish_date = isoparse(snippet['publishedAt']).strftime('%Y-%m-%d %H:%M:%S')

                    # Add the processed comment to the list
                    processed_comments.append({
                        'author': author,
                        'channel_url' : channel_url,
                        'text': text,
                        'likes': likes,
                        'profile_image_url': profile_image_url,
                        'publish_date': publish_date
                    })
        else:
            if 'items' in response:
                for comment in response['items']:
                    # Extract the comment snippet
                    snippet = comment['snippet']['topLevelComment']['snippet']
                    author = snippet['authorDisplayName']
                    channel_url = snippet['authorChannelUrl']
                    text = snippet['textDisplay']
                    likes = f"{snippet['likeCount']:,}"
                    profile_image_url = snippet['authorProfileImageUrl']
                    publish_date = isoparse(snippet['publishedAt']).strftime('%Y-%m-%d %H:%M:%S')

                    # Add the processed comment to the list
                    processed_comments.append({
                        'author': author,
                        'channel_url' : channel_url,
                        'text': text,
                        'likes': likes,
                        'profile_image_url': profile_image_url,
                        'publish_date': publish_date
                    })


        if order == 'time':
            date_format = "%Y-%m-%d %H:%M:%S"
            date1 = dt.strptime(processed_comments[0].get('publish_date'), date_format)
            date2 = dt.strptime(processed_comments[1].get('publish_date'), date_format)

            if date1 < date2:
                    processed_comments[0]['pinned'] = True

        return processed_comments

    except HttpError as e:
        error_message = f'An HTTP error {e.resp.status} occurred: {e.content}'
        raise HttpError(e.resp, error_message)



async def get_video_comments_view_async(video_id, order, maxResults, previousPageID, pageID, searchInput, quotaUser, isFirstTime):

    if not video_id:
        return {'error': 'No video_id parameter provided'}, 400

    try:
        match isFirstTime:
            case True:
                
                comments_and_VidInfo = await asyncio.gather(get_video_comments(video_id, order, maxResults, previousPageID, pageID, searchInput, quotaUser), get_video_informations(video_id))

                comments_and_VidInfo = {
                    'comments': comments_and_VidInfo[0],
                    'video_info': comments_and_VidInfo[1],
                }

                return comments_and_VidInfo
            
            case False:
                
                comments = await get_video_comments(video_id, order, maxResults, previousPageID, pageID, searchInput, quotaUser)
                
                comments_and_VidInfo = {
                    'comments': comments,
                    'video_info': video_info
                }

                return  comments_and_VidInfo


    except HttpError as e:
        error_message = f'An HTTP error {e.resp.status} occurred: {e.content}'
        return {'error': error_message}, 500
    


async def get_video_informations(video_id):
    video_url = "https://www.youtube.com/watch?v=" + video_id
    yt = YouTube(video_url)

    try:
        title = yt.title
        thumbnail = yt.thumbnail_url
        views = f"{yt.views:,}"  # Format numbers 100000 = 100,000 etc.
        length = str(datetime.timedelta(seconds=yt.length))
        publish_date = yt.publish_date
    except:
        title = "Could not find or video was deleted by Youtube"
        thumbnail = "couldn't find"
        views = "couldn't find"
        length = "couldn't find"

        publish_date = "couldn't find"

    video_informations = {
        "title": title,
        "thumbnail": thumbnail,
        "views": views,
        "publish_date": publish_date,
        "length": length
    }

    video_info.update(video_informations)

    return video_informations


def store_comments_data(video_id, username):
    video_url = "https://www.youtube.com/watch?v=" + video_id
    yt = YouTube(video_url)

    # Store data in user history
    storage = user_data_storage.objects.get(
        user=User.objects.get(username=username)
    )

    time = dt.now()

    try:
        info = [yt.title, video_url, time.strftime("%d/%m/%Y %H:%M")]
    except Exception:
        info = ["could't find", video_url, time.strftime("%d/%m/%Y %H:%M")]
    
    storage.filtered_comments_history.append(info)
    storage.save()

    return 


def show_comments(order, maxResults, pageID, previousPageID, video_id, searchInput, login_context, isFirstTime):
    context = {}

    if video_id != None:
        
        context = {
            'order': order,
            'maxResults': maxResults,
            'pageID': int(pageID),
            'video_id' : video_id,
            'searchInput': searchInput
        }


        # Reset previous saved pageTokens
        if previousPageID == '1' and pageID == '1':
            pageTokens.clear()
            pageTokens.append(None)

        if login_context.get("logged") == True: 
            quotaUser = login_context.get("username")
        else: 
            quotaUser = None


        # E.g. previousPage = 1 and Page = 2, so if refreshed next api request won't be sent

        match str(previous_request_pageID[-1]) == str(pageID):
            case True:
                stopRequest = True
            case False:
                previous_request_pageID.pop(0)
                previous_request_pageID.append(pageID)

                stopRequest = False



        match str(previous_request_previousPageID[-1]) == str(previousPageID):
            case True:
                stopRequest2 = True
            case False:
                previous_request_previousPageID.pop(0)
                previous_request_previousPageID.append(previousPageID)

                stopRequest2 = False


        if stopRequest == True and stopRequest2 == True:
            previousPageID = pageID

        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comments_and_VidInfo = loop.run_until_complete(get_video_comments_view_async(video_id, order, maxResults, previousPageID, pageID, searchInput, quotaUser, isFirstTime))
        

        context.update(comments_and_VidInfo)
        context.update({'count' : len(comments_and_VidInfo['comments'])})
        context.update(login_context)
        context.update({'sites_context': sites_context})

        if 'last_page' in comments_and_VidInfo['comments']:
            context.update({'last_page': True})
            comments_and_VidInfo['comments'].remove('last_page')

        return context

    else:

        context.update(login_context)
        context.update({'sites_context': sites_context})

        return context
            

@login_check
def comments(request, login_context):
    if request.method == "POST":
        match request.POST.get("video_url"):
        
            case None:

                try:
                    order = request.POST.get("order")
                    maxResults = request.POST.get("maxResults")
                    previousPageID = request.POST.get("previousPageID")
                    pageID = request.POST.get("pageID")
                    video_id = request.POST.get("video_id")
                    searchInput = request.POST.get("searchInput")


                    context = show_comments(order, maxResults, pageID, previousPageID, video_id, searchInput, login_context, isFirstTime = False)
                    return render(request, "comments.html", context)
                
                except Exception as err:
                    print(err)
                    pageTokens.clear()
                    pageTokens.append(None)
                    msg.info(request, "Something went wrong, please try again")
                    return redirect(comments)
    
            case _:

                try:
                    video_url = request.POST.get("video_url")   
                    video_id = video_url.split("=", 1)[1]

                    
                    order = 'relevance'
                    maxResults = 25
                    pageID = 1
                    previousPageID = 1
                    searchInput = ""

                    if video_info:
                        video_info.clear()

                    # Store in history
                    store_comments_data(video_id, login_context["username"])

                    context = show_comments(order, maxResults, pageID, previousPageID, video_id, searchInput, login_context, isFirstTime = True)
                    return render(request, "comments.html", context)
                
                except Exception as err:
                    print(err)
                    pageTokens.clear()
                    pageTokens.append(None)
                    msg.info(request, "Url is incorrect")
                    return redirect(comments)
                
    # On first load
    context = {}
    context.update(login_context)
    context.update({'sites_context': sites_context})

    return render(request, "comments.html", context)


@login_check
def manage_account_General(request, login_context):

    context = {}
    context.update(login_context)
    context.update({'sites_context': sites_context})

    return render(request, "manage_account_General.html", context)



@login_check
def manage_account_Overview(request, login_context):
    username = login_context["username"]

    storage = user_data_storage.objects.get(
            user=User.objects.get(username=username)
        )
    
    for video in storage.download_history[-6:]:
        del video[3]




    context = {
        'vid_downloads_quantity' : len(storage.download_history),
        'prompts_quantity': len(storage.prompts_history),
        'filtered_comments_quantity': len(storage.filtered_comments_history),

        'download_history': storage.download_history[-6:],
        'prompts_history': storage.prompts_history[-6:],
        'filtered_comments_history': storage.filtered_comments_history[-6:]
    }

    context.update(login_context)
    context.update({'sites_context': sites_context})

    return render(request, "manage_account_Overview.html", context)



@login_check
def manage_account_Private(request, login_context):

    context = {}
    context.update(login_context)
    context.update({'sites_context': sites_context})

    return render(request, "manage_account_Private.html", context)

