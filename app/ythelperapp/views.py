# Django dependencies
from django.shortcuts import render, redirect
from django.contrib import messages as msg
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Api
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import download_history_Serializer, prompts_history_Serializer, filtered_comments_history_Serializer, transferred_playlists_history_Serializer

# App packages
from .forms import CreateUserForm, LoginUserForm, UpdateUserForm, StartTaskForm
from .decorators import login_check, login_required, not_authenticated_only, rate_limit, RedirectException
from .models import user_data_storage, download_history_item, prompts_history_item, filtered_comments_history_item, transferred_playlists_history_item, User, Ticket
from .tasks import TransferPlaylist, download_and_store_image
from settings.base import BASE_DIR

# Python dependencies
import os
import re
import openai
import asyncio
import isodate
import spotipy
import boto3
import random
import environ
import logging

from pytube import YouTube
from datetime import datetime as dt
from urllib.parse import quote
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil.parser import isoparse
from spotipy.oauth2 import SpotifyOAuth
from botocore.config import Config

# Logging
logger = logging.getLogger('youtube_helper')

# Retrieve environment variables 
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '..', '.env'))

OPENAI_API_KEY = env("OPENAI_API_KEY")
GOOGLE_API_KEY = env("GOOGLE_API_KEY")
CLIENT_ID = env("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = env("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = env("SPOTIFY_REDIRECT_URI")


# The required scope for Spotify playlist creation
SCOPE = "playlist-modify-private playlist-modify-public"


# Youtube Api object
youtube = build("youtube", "v3", developerKey=GOOGLE_API_KEY)


# Navbar menu info
sites_context = {
    "main_page": "<i class='fa-solid fa-download'></i></i>&nbsp; Video Downloader",
    "comments": "<i class='fa-regular fa-comments'></i>&nbsp; YT Comments Filtering",
    "youtube_to_spotify": "<i class='fa-brands fa-spotify'></i>&nbsp; Youtube Playlist To Spotify",
    "ai_page": "<i class='fa-regular fa-image'></i>&nbsp; Ai Avatar Generator",
}




"""


Api Views
   ↓

"""

class RetrieveDownloadHistory(viewsets.ModelViewSet):
    serializer_class = download_history_Serializer
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        logger.info(f"Download History Api request for user: {self.request.user.username}")
        return download_history_item.objects.filter(user=self.request.user) 
    

    
class RetrievePromptsHistory(viewsets.ModelViewSet):
    serializer_class = prompts_history_Serializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        logger.info(f"Prompts History Api request for user: {self.request.user.username}")
        return prompts_history_item.objects.filter(user=self.request.user)



class RetrieveFilteredCommentsHistory(viewsets.ModelViewSet):
    serializer_class = filtered_comments_history_Serializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        logger.info(f"Filtered Comments Api request for user: {self.request.user.username}")
        return filtered_comments_history_item.objects.filter(user=self.request.user)



class RetrieveTransferredPlaylistsHistory(viewsets.ModelViewSet):
    serializer_class = transferred_playlists_history_Serializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        logger.info(f"Transferred Playlists History Api request for user: {self.request.user.username}")
        return transferred_playlists_history_item.objects.filter(user=self.request.user)
    



"""


Function Views
      ↓
      
"""

@login_check
def main_page(request, login_context):
    context = {}

    # Use download history for slides on the main page
    if "username" in login_context:
        unique_videos = list(download_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).order_by('title').distinct('title'))
        random.shuffle(unique_videos)
        
        context.update({"number_of_links": range(0, len(unique_videos[:10]))})
        context.update({"unique_videos": unique_videos[:10]})


    if request.method == "POST":
        video_url = request.POST.get("sended_link")

        try:
            if "youtu.be" in video_url:
                video_url = video_url.split("youtu.be/", 1)[1]
                video_id = video_url.split("?", 1)[0]
                video_url = f'https://www.youtube.com/watch?v={video_id}'

            else:
                video_url = video_url.split("&", 1)[0]
            yt = YouTube(video_url)

        except Exception as e:
            logger.error(f"Video downloader view, Exception: {e}")
            msg.info(request, "Invalid url")
            return redirect(main_page)


        # Store data in user history
        if "username" in login_context:
            storage = user_data_storage.objects.get(
                user=User.objects.get(username=login_context["username"])
            )

            if storage.save_history:
                try:
                    download_history_item.objects.create(
                        user=User.objects.get(username=login_context["username"]), 
                        title=yt.title,
                        link=video_url,
                        thumbnail_url=yt.thumbnail_url
                    )
                    logger.info(f"Item has been added to database by {request.user.username}")


                except Exception as e:
                    logger.error(f"Exception while saving user history: {e}")
                    msg.info(request, "Error while saving history")

        return redirect("download_page", video_url=video_url)
    

    context.update(login_context)
    context.update({"sites_context": sites_context})
    return render(request, "main_page.html", context)


@login_check
@not_authenticated_only
def login_page(request, login_context):
    form = LoginUserForm()

    if request.method == "POST":
        form = LoginUserForm(request.POST)

        if form.is_valid():
            email = request.POST.get("email").lower()
            password = request.POST.get("password")

            # Custom authorization backend
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                logger.info(f"User {request.user.username} has logged in")
                msg.success(request, "Welcome " + "<b>" + request.user.username + "</b>")
                return redirect(main_page)

            else:
                msg.info(request, "Password is incorrect")
                return redirect(login_page)

    context = {"form": form}

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "login_page.html", context)


def logoutUser(request):
    logger.info(f"User {request.user.username} has logged out")
    logout(request)
    return redirect(main_page)


@login_check
@not_authenticated_only
def sign_up_page(request, login_context):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            form.save()
            logger.info(f"User {username} has been created")


            user_data_storage.objects.create(
                user=User.objects.get(username=username)
            )
            logger.info(f"User's {username} storage has been created")


            msg.success(request, "Welcome on board " + "<b>" + username + "</b>")
            return redirect(login_page)

    context = {"form": form}

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "sign_up_page.html", context)


@login_check
def download_page(request, login_context, video_url):
    context = {}

    try:    
        # Extract video metadata and download links
        context = run_async(video_url)

    except Exception as e:
        logger.error(f"Download_page view, Exception: {e}")
        msg.info(request, "Something went wrong, please try again")
        return redirect(main_page)

    context.update(login_context)
    context.update({"sites_context": sites_context})
    context.update({"video_duration": isodate.parse_duration(context.get("length"))})

    return render(request, "download_page.html", context)


@login_required
@login_check
def ai_page(request, login_context, image_url="", image_description=""):
    if request.method == "POST":
        description = request.POST.get("description")

        try:
            safe_link = get_openai_response(request, login_context, description)
        except RedirectException as e:
            return redirect(e.url)
        
        return redirect(ai_page, image_url=safe_link, image_description=description)

    context = {}
    context.update(login_context)
    context.update({"sites_context": sites_context})


    if image_url != "":
        context.update(
            {
                "image_link": image_url.replace("%25", "%"),
                "image_title": image_description,
            }
        )
    else:
        # If no image provided check user's remaining Tickets   
        if login_context['logged']:
            try:
                remaining_tickets = Ticket.objects.get(user=User.objects.get(username=login_context['username'])).remaining_tickets
            except ObjectDoesNotExist:
                remaining_tickets = 3

            context.update({"tickets": remaining_tickets})

        users_avatars = get_avatars()  
        context.update({"users_avatars": users_avatars})
        

    return render(request, "ai_site.html", context)


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
                    
                    # Clear page Tokens on first page
                    if int(pageID) == 1 and int(previousPageID) == 1:
                        if len(request.session['pageTokens']) > 1:
                            request.session['pageTokens'].clear()
                            request.session['pageTokens'].append(None)

                    context = show_comments(
                        request,
                        order,
                        maxResults,
                        pageID,
                        previousPageID,
                        video_id,
                        searchInput,
                        login_context,
                        isFirstTime=False,
                    )
                    return render(request, "comments.html", context)

                except Exception as e:
                    request.session['pageTokens'].clear()
                    logger.error(f"Comments view, Exception: {e}")
                    msg.info(request, "Something went wrong, please try again")
                    return redirect(comments)

            case _:
                # If the url has been passed on
                try:
                    video_url = request.POST.get("video_url")

                    try:
                        if "youtu.be" in video_url:
                            video_url = video_url.split("youtu.be/", 1)[1]
                            video_id = video_url.split("?", 1)[0]
                        else:
                            video_url = video_url.split("&", 1)[0]
                            video_id = video_url.split("=", 1)[1]

                    except Exception as e:
                        logger.error(f"Comments view, Exception: {e}")
                        msg.info(request, "Invalid url")
                        return redirect(comments)
                    

                    order = "relevance"
                    maxResults = 25
                    pageID = 1
                    previousPageID = 1
                    searchInput = ""

                    request.session['pageTokens'] = [None]
                    request.session['previous_request_pageID'] = None
                    request.session['previous_request_previousPageID'] = None
                    request.session['video_metadata_temp'] = {}

                    context = show_comments(
                        request,
                        order,
                        maxResults,
                        pageID,
                        previousPageID,
                        video_id,
                        searchInput,
                        login_context,
                        isFirstTime=True,
                    )
                    return render(request, "comments.html", context)

                except Exception as e:
                    logger.error(f"Comments view, Exception: {e}")
                    msg.info(request, "Video cannot be found")
                    return redirect(comments)

    context = {}
    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "comments.html", context)


@login_check
def youtube_to_spotify(request, login_context):
    context = {}
    form = StartTaskForm()

    if "code" not in request.GET:
        context.update({"not_auth": True})

    if request.method == "POST":

        # Create Spotify authorization object
        sp_oauth = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
        )

        # If the user is not authenticated, redirect them to Spotify's login page
        if "code" not in request.GET:
            auth_url = sp_oauth.get_authorize_url()
            return redirect(auth_url)

        form = StartTaskForm(request.POST)

        if form.is_valid():
            url = request.POST.get("url")

            # Block Youtube Mix playlists
            if "list=RD" not in url: 
                url = url.split("list=", 1)[1]
                playlist_id = url.split("&", 1)[0]

                # Store data in user history 
                if "username" in login_context:
                    storage = user_data_storage.objects.get(
                        user=User.objects.get(username=login_context["username"])
                    )

                    # Retrieve playlist title
                    response_for_title = (
                        youtube.playlists()
                        .list(part="snippet", id=playlist_id, fields="items(snippet(title))")
                        .execute()
                    )
                    
                    if response_for_title["items"][0]["snippet"]["title"]:
                        title = response_for_title["items"][0]["snippet"]["title"]
                    else:
                        title = "Couldn't find"

                    if storage.save_history:
                        download_history_item.objects.create(
                            user=User.objects.get(username=login_context["username"]), 
                            title=title,
                            link=request.POST.get("url"),
                        )
                        logger.info(f"Item has been added to database by {request.user.username}")



                # If the user has granted permission and returned with the authorization code
                code = request.GET.get("code")
                token_info = sp_oauth.get_access_token(code)

                sp = spotipy.Spotify(auth=token_info["access_token"])
                user_id = sp.me()["id"]
                user_account_url = f"https://open.spotify.com/user/{user_id}"

                # Pass the access token to a Celery task for further processing
                TransferPlaylist.delay(
                    sp_token=token_info["access_token"], playlist_id=playlist_id
                )

                return redirect(youtube_to_spotify_done, account_url=user_account_url)

            else:
                msg.info(request, "Youtube Mix is not accepted")
                return redirect(youtube_to_spotify) 
            
    context.update({"form": form})
    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "youtube_to_spotify.html", context)


@login_check
def youtube_to_spotify_done(request, login_context, account_url):
    context = {}
    context.update({"sp_account_url": account_url})
    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "youtube_to_spotify_done.html", context)


@login_check
def manage_account_General(request, login_context):
    storage = user_data_storage.objects.get(
        user=User.objects.get(username=login_context["username"])
    )

    form = UpdateUserForm(
        initial={
            "username": request.user.username,
            "email": request.user.email,
            "save_history": storage.save_history,
        }
    )

    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            msg.success(request, "Account has been updated")
            return redirect(manage_account_General)

    context = {"form": form}
    context.update({"user": User.objects.get(username=login_context["username"])})
    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "manage_account_General.html", context)


@login_check
def manage_account_Overview(request, login_context):

    context = {
        "vid_downloads_quantity": download_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).count(),
        "prompts_quantity": prompts_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).count(),
        "filtered_comments_quantity": filtered_comments_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).count(),
        "transferred_playlists_quantity": transferred_playlists_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).count(),
        
        "download_history": download_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).order_by('-saved_on')[:6],
        "prompts_history": prompts_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).order_by('-saved_on')[:6],
        "filtered_comments_history": filtered_comments_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).order_by('-saved_on')[:6],
        "transferred_playlists_history": transferred_playlists_history_item.objects.filter(user=User.objects.get(username=login_context["username"])).order_by('-saved_on')[:6],
    }

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "manage_account_Overview.html", context)


@login_check
def manage_account_Private(request, login_context):
    context = {}

    try: 
        context.update({"api_token": f'Token {Token.objects.get(user=User.objects.get(username=login_context["username"]))}'})
    except Exception:
        pass

    if request.method == "POST":
        try:
            Token.objects.create(user=User.objects.get(username=login_context["username"]))
            return redirect(manage_account_Private)
        except Exception:
            pass
    

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "manage_account_Private.html", context)




"""


Non-view Functions
        ↓
      
"""

def run_async(url):
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    context = loop.run_until_complete(gather_functions(url))

    return context


async def gather_functions(url):
    Shared_result = await asyncio.gather(get_streams_data(url), get_video_metadata(url))

    context = {}
    context.update(Shared_result[0])
    context.update(Shared_result[1])

    return context


async def get_streams_data(url):
    streams_data = {}
    streams_data_no_audio = {}
    seen_resolution = set()

    # Create a PyTube YouTube object
    yt = await asyncio.get_event_loop().run_in_executor(None, lambda: YouTube(url))

    # Get all available streams for the video
    resolutions = [
        "144p",
        "240p",
        "360p",
        "480p",
        "720p",
        "1080p",
        "1440p",
        "2160p",
        "4320p",
    ]

    filtered_streams = await asyncio.get_event_loop().run_in_executor(
        None, lambda: yt.streams.filter(resolution=resolutions, only_video=False)
    )

    # Sort streams by resolution in descending order
    filtered_streams = sorted(
        filtered_streams, key=lambda stream: int(stream.resolution[:-1]), reverse=True
    )

    audio = await asyncio.get_event_loop().run_in_executor(
        None, lambda: yt.streams.get_audio_only()
    )

    # Extract download links from the streams
    for stream in filtered_streams:
        file_extension = stream.mime_type.split("/")[-1]

        if stream.resolution not in seen_resolution:
            seen_resolution.add(stream.resolution)

            match stream.is_progressive:
                case True:
                    streams_data[stream.url] = [
                        stream.resolution,
                        file_extension.upper(),
                    ]
                case False:
                    streams_data_no_audio[stream.url] = [
                        stream.resolution,
                        file_extension.upper(),
                    ]

    streams_data = {
        "streams_data": streams_data,
        "streams_data_no_audio": streams_data_no_audio,
        "audio_download_url": audio.url,
    }

    return streams_data


async def get_video_metadata(url):
    # Another youtube object, first object in use by get_video_comments
    youtube2 = build("youtube", "v3", developerKey=GOOGLE_API_KEY)

    video_id = url.split("=", 1)[1]

    try:
        # Call youtube Api to retrieve video details
        yt_request = youtube2.videos().list(
            part="snippet,statistics,contentDetails", id=video_id
        )

        response = await asyncio.to_thread(yt_request.execute)

        video = response["items"][0]
        snippet = video["snippet"]
        statistics = video["statistics"]
        content_details = video["contentDetails"]

        title = snippet["title"]
        description = snippet["description"]
        publish_date = dt.strptime(
            snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%B %d, %Y")

        views = "{:,}".format(int(statistics["viewCount"])).replace(",", " ")
        likes = "{:,}".format(int(statistics["likeCount"])).replace(",", " ")
        comment_count = "{:,}".format(int(statistics["commentCount"])).replace(",", " ")

        length = content_details["duration"]


    except HttpError as e:
        logger.error(f"Video metadata, Http Exception: {e}")
        title = "Could not find or video was deleted by YouTube"
        length = "couldn't find"
        views = "couldn't find"
        publish_date = "couldn't find"
        description = "couldn't find"
        likes = "couldn't find"
        comment_count = "couldn't find"

    video_metadata = {
        "link": url,
        "title": title,
        "views": views,
        "likes": likes,
        "comment_count": comment_count,
        "video_id": video_id,
        "description": description,
        "publish_date": publish_date,
        "length": length,
    }

    return video_metadata


async def get_video_comments(
    request,
    video_id, 
    order, 
    maxResults, 
    previousPageID, 
    pageID, 
    searchInput, 
    quotaUser
):
    try:
        # Check if the page is previous, the same or next
        match (int(pageID) - int(previousPageID)):
            case 1:
                # Retrieve the comments for the specified video
                yt_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="html",
                    order=order,
                    maxResults=maxResults,
                    pageToken=request.session['pageTokens'][-1],
                    quotaUser=quotaUser,
                )
                        
            case 0:
                if len(request.session['pageTokens']) > 1 and int(pageID) != int(previousPageID):
                    request.session['pageTokens'].pop()
                    request.session.modified = True

                # Retrieve the comments for the specified video
                yt_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="html",
                    order=order,
                    maxResults=maxResults,
                    pageToken=request.session['pageTokens'][-1],
                    quotaUser=quotaUser,
                )

            case -1:
                if len(request.session['pageTokens']) > 2:	
                    request.session['pageTokens'] = request.session['pageTokens'][:-2]
                    request.session.modified = True
                else:
                    request.session['pageTokens'].pop()
                    request.session.modified = True

                # Retrieve the comments for the specified video
                yt_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="html",
                    order=order,
                    maxResults=maxResults,
                    pageToken=request.session['pageTokens'][-1],
                    quotaUser=quotaUser,
                )

        response = await asyncio.to_thread(yt_request.execute)
        
        if "nextPageToken" in response:
            request.session['pageTokens'].append(response["nextPageToken"])
            request.session.modified = True


        # Process the comments
        processed_comments = []

        # Check if the page is the last one
        if "nextPageToken" not in response:
            processed_comments.append("last_page")

        # Process the user's search phrase
        if searchInput != "":
            if "items" in response:
                filtered_comments = [
                    comment
                    for comment in response["items"]
                    if re.search(
                        re.escape(searchInput),
                        comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        re.IGNORECASE,
                    )
                ]

                for comment in filtered_comments:
                    # Html mark around phrase
                    highlighted_comment = re.sub(
                        r"(?![^<>]*>)(" + re.escape(searchInput) + r")",
                        r"<mark>\1</mark>",
                        comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        flags=re.IGNORECASE,
                    )

                    comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"] = highlighted_comment

                for comment in filtered_comments:
                    snippet = comment["snippet"]["topLevelComment"]["snippet"]

                    # Retrieve comment data
                    author = snippet["authorDisplayName"]
                    channel_url = snippet["authorChannelUrl"]
                    text = snippet["textDisplay"]
                    likes = f"{snippet['likeCount']:,}"
                    replies = f"{comment['snippet']['totalReplyCount']:,}"
                    profile_image_url = snippet["authorProfileImageUrl"]
                    publish_date = isoparse(snippet["publishedAt"]).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Add the processed comment to the list
                    processed_comments.append(
                        {
                            "author": author,
                            "channel_url": channel_url,
                            "text": text,
                            "likes": likes,
                            "replies": replies,
                            "profile_image_url": profile_image_url,
                            "publish_date": publish_date,
                        }
                    )
        else:
            if "items" in response:
                for comment in response["items"]:
                    snippet = comment["snippet"]["topLevelComment"]["snippet"]

                    # Retrieve comment data
                    author = snippet["authorDisplayName"]
                    channel_url = snippet["authorChannelUrl"]
                    text = snippet["textDisplay"]
                    likes = f"{snippet['likeCount']:,}"
                    replies = f"{comment['snippet']['totalReplyCount']:,}"
                    profile_image_url = snippet["authorProfileImageUrl"]
                    publish_date = isoparse(snippet["publishedAt"]).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Add the processed comment to the list
                    processed_comments.append(
                        {
                            "author": author,
                            "channel_url": channel_url,
                            "text": text,
                            "likes": likes,
                            "replies": replies,
                            "profile_image_url": profile_image_url,
                            "publish_date": publish_date,
                        }
                    )

        # Check if comment is pinned by the author
        if order == "time" and processed_comments:
            try:
                date_format = "%Y-%m-%d %H:%M:%S"
                date1 = dt.strptime(processed_comments[0].get("publish_date"), date_format)
                date2 = dt.strptime(processed_comments[1].get("publish_date"), date_format)

                if date1 < date2:
                    processed_comments[0]["pinned"] = True
            except Exception:
                pass

        return processed_comments

    except HttpError as e:
        logger.error(f"Comments view, Http exception: {e}")
        error_message = f"An HTTP error {e.resp.status} occurred: {e.content}"
        raise HttpError(e.resp, error_message)


async def get_video_comments_view_async(
    request,
    video_id,
    order,
    maxResults,
    previousPageID,
    pageID,
    searchInput,
    quotaUser,
    isFirstTime,
):
    if not video_id:
        msg.info(request, "Cannot retrieve video id")
        return redirect('comments')

    try:
        # Check whether to run new request for video metadata 
        match isFirstTime:
            case True:
                video_url = "https://www.youtube.com/watch?v=" + video_id

                comments_and_VidInfo = await asyncio.gather(
                    get_video_comments(
                        request,
                        video_id,
                        order,
                        maxResults,
                        previousPageID,
                        pageID,
                        searchInput,
                        quotaUser,
                    ),
                    get_video_metadata(video_url),
                )

                request.session['video_metadata_temp'].update(comments_and_VidInfo[1])

                comments_and_VidInfo = {
                    "comments": comments_and_VidInfo[0],
                    "video_metadata": comments_and_VidInfo[1],
                    "video_duration": isodate.parse_duration(comments_and_VidInfo[1].get("length"))
                }

                return comments_and_VidInfo

            case False:
                comments = await get_video_comments(
                    request,
                    video_id,
                    order,
                    maxResults,
                    previousPageID,
                    pageID,
                    searchInput,
                    quotaUser,
                )

                comments_and_VidInfo = {
                    "comments": comments,
                    "video_metadata": request.session['video_metadata_temp'],
                    "video_duration": isodate.parse_duration(request.session['video_metadata_temp'].get("length")),
                }

                return comments_and_VidInfo

    except HttpError as e:
        logger.error(f"Comments_view, Http Exception: {e}")
        error_message = f"An HTTP error {e.resp.status} occurred: {e.content}"
        return {"error": error_message}, 500


def show_comments(
    request,
    order,
    maxResults,
    pageID,
    previousPageID,
    video_id,
    searchInput,
    login_context,
    isFirstTime,
):
    context = {}

    if video_id:
        context = {
            "order": order,
            "maxResults": maxResults,
            "pageID": int(pageID),
            "video_id": video_id,
            "searchInput": searchInput,
        }

        if login_context["logged"]:
            quotaUser = login_context["username"]
        else:
            quotaUser = None

 

        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comments_and_VidInfo = loop.run_until_complete(
            get_video_comments_view_async(
                request,
                video_id,
                order,
                maxResults,
                previousPageID,
                pageID,
                searchInput,
                quotaUser,
                isFirstTime,
            )
        )

        if quotaUser and isFirstTime:
            # Store data in user history
            storage = user_data_storage.objects.get(
                user=User.objects.get(username=quotaUser)
            )

            if storage.save_history:
                try:
                    filtered_comments_history_item.objects.create(
                        user=User.objects.get(username=login_context["username"]), 
                        title=comments_and_VidInfo["video_metadata"]["title"],
                        link="https://www.youtube.com/watch?v=" + video_id,
                    )
                    logger.info(f"Item has been added to database by {request.user.username}")


                except Exception as e:
                    logger.error(f"Comments view, Exception while saving history: {e}")
                    msg.info(request, "Error occurred, history not updated")

        context.update(comments_and_VidInfo)
        context.update({"count": len(comments_and_VidInfo["comments"])})
        context.update(login_context)
        context.update({"sites_context": sites_context})

        if "last_page" in comments_and_VidInfo["comments"]:
            context.update({"last_page": True})
            comments_and_VidInfo["comments"].remove("last_page")

        return context

    else:
        context.update(login_context)
        context.update({"sites_context": sites_context})

        return context


def get_avatars():
    try:
        s3 = boto3.client(
            's3', 
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4')
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='media/', Delimiter='/')

        if 'Contents' in response:
            objects = response['Contents']
            image_objects = [obj for obj in objects if obj['Key'].endswith('.png')]
            image_objects.sort(key=lambda obj: obj['LastModified'], reverse=True)
            
            if len(image_objects) <= 8:
                random_image_objects = image_objects
            else:
                random_image_objects = random.sample(image_objects, 8)
            
            random_image_urls = []
            for img_obj in random_image_objects:
                url = s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': bucket_name, 'Key': img_obj['Key']},
                    ExpiresIn=3600,
                )
                random_image_urls.append(url)
            
            return random_image_urls
        else:
            return None
        
    except Exception as e:
        logger.error(f"Ai_page view, get_avatars func Exception: {e}")
        return None


@rate_limit
def get_openai_response(request, login_context, description):
    try:
        response_data = openai.Image.create(
            prompt=description
            + " in visual key of Jojo Bizzare Adventure, epic, anime style, japanese anime, nice background, hyper realistic, handsome, 1:1",
            n=1,
            size="1024x1024",
        )

        link = response_data["data"][0]["url"]

        fixed_link = quote(link, safe=":/?&=%")

        # Store data in user history
        try:
            if "username" in login_context:
                storage = user_data_storage.objects.get(
                    user=User.objects.get(username=login_context["username"])
                )

                if storage.save_history:
                    prompts_history_item.objects.create(
                        user=User.objects.get(username=login_context["username"]), 
                        title=description,
                        link=fixed_link.replace("%25", "%"),
                    )
                    logger.info(f"Item has been added to database by {request.user.username}")

        except Exception as e:
            logger.error(f"Ai page, Exception while saving history: {e}")
            msg.info(request, "Error while saving history")

        try:
            download_and_store_image.delay(fixed_link)
        except Exception as e:
            logger.info(f"Ai_page, Exception while sending task: {e}")
            pass
        
        return fixed_link

    except openai.error.RateLimitError:
        logger.info("OpenAi RateLimitError")
        msg.info("Ai model is currently overloaded, please wait a second")
        return redirect(ai_page)
    