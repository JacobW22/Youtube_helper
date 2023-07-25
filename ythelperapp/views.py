from django.shortcuts import render, redirect
from django.contrib import messages as msg
from django.contrib.auth import authenticate, login, logout

from .forms import CreateUserForm, LoginUserForm, UpdateUserForm, StartTaskForm
from .decorators import login_check, not_authenticated_only
from .models import user_data_storage, User
from .tasks import TransferPlaylist

import os
import re
import openai
import backoff
import pytube
import asyncio
import isodate
import spotipy


from pytube import YouTube
from datetime import datetime as dt
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil.parser import isoparse
from spotipy.oauth2 import SpotifyOAuth

# Hide it from Github
load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

# The required scopes for playlist creation
SCOPE = "playlist-modify-private playlist-modify-public"

youtube = build("youtube", "v3", developerKey=GOOGLE_API_KEY)

sites_context = {
    "main_page": "<i class='fa-solid fa-download'></i></i>&nbsp; Video Downloader",
    "comments": "<i class='fa-regular fa-comments'></i>&nbsp; YT Comments Filtering",
    "youtube_to_spotify": "<i class='fa-brands fa-spotify'></i>&nbsp; Youtube Playlist To Spotify",
    "ai_page": "<i class='fa-regular fa-image'></i>&nbsp; Ai Avatar Generator",
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

        Download_history = storage.download_history

        unique_videos = []
        unique_titles = set()

        for movie in Download_history:
            title = movie[0]

            if title not in unique_titles:
                unique_videos.append(movie)
                unique_titles.add(title)
                if len(unique_videos) == 10:
                    break

        for vid_info in unique_videos:
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
    context.update({"sites_context": sites_context})

    if request.method == "POST":
        link = request.POST.get("sended_link")
        try:
            link = link.split("&", 1)[0]
            yt = YouTube(link)

        except Exception:
            msg.info(request, "Invalid url")
            return redirect(main_page)

        # Store data in user history
        if "username" in login_context:
            username = login_context["username"]
            storage = user_data_storage.objects.get(
                user=User.objects.get(username=username)
            )

            if storage.save_history:
                time = dt.now()

                try:
                    info = [
                        yt.title,
                        link,
                        time.strftime("%d/%m/%Y %H:%M"),
                        yt.thumbnail_url,
                    ]
                    storage.download_history.append(info)
                    storage.save()

                except Exception:
                    msg.info(request, "Something went wrong, history not updated ")

        return redirect("download_page", parameter=link)

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

            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
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
                object_name=str(user) + " storage",
                user=User.objects.get(username=user),
                download_history=["registered"],
                prompts_history=["registered"],
                filtered_comments_history=["registered"],
                transferred_playlists_history=["registered"]
            )

            storage = user_data_storage.objects.get(
                user=User.objects.get(username=user)
            )

            storage.download_history.remove("registered")
            storage.prompts_history.remove("registered")
            storage.filtered_comments_history.remove("registered")
            storage.transferred_playlists_history.remove("registered")
            storage.save()

            msg.success(request, "Welcome on board " + "<b>" + user + "</b>")
            return redirect(login_page)

    context = {"form": form}

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "sign_up_page.html", context)


# Backoff for sending request again ( sometimes titles can't be found by pytube )
@login_check
@backoff.on_exception(
    backoff.expo, (pytube.exceptions.PytubeError, ValueError), max_time=0.3
)
def download_page(request, login_context, parameter):
    context = {}

    try:
        context = run_async(parameter)
    except Exception:
        msg.info(request, "Something went wrong, please try again")
        return redirect(main_page)

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "download_page.html", context)


@login_check
def ai_page(request, login_context, parameter="", parameter_title=""):
    if request.method == "POST":
        description = request.POST.get("description")

        try:
            response_data = openai.Image.create(
                prompt=description
                + ", digital art, icon, avatar image, illustration style, epic, user profile image, ultra quality, 1:1",
                n=1,
                size="1024x1024",
            )

            link = response_data["data"][0]["url"]

            fixed_link = quote(link, safe=":/?&=%")

        except openai.error.RateLimitError:
            msg.success("Ai model is currently overloaded, please wait a second")
            return redirect(ai_page)

        # Store data in user history
        if "username" in login_context:
            username = login_context["username"]
            storage = user_data_storage.objects.get(
                user=User.objects.get(username=username)
            )

            if storage.save_history:
                time = dt.now()
                info = [
                    description,
                    fixed_link.replace("%25", "%"),
                    time.strftime("%d/%m/%Y %H:%M"),
                ]
                storage.prompts_history.append(info)
                storage.save()

        return redirect(ai_page, parameter=fixed_link, parameter_title=description)

    context = {}
    context.update(login_context)
    context.update({"sites_context": sites_context})

    if parameter != "":
        context.update(
            {
                "image_link": parameter.replace("%25", "%"),
                "image_title": parameter_title,
            }
        )

    return render(request, "ai_site.html", context)


pageTokens = [None]
previous_request_previousPageID = [0]
previous_request_pageID = [0]
video_metadata_temp = {}


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

                except Exception:
                    pageTokens.clear()
                    pageTokens.append(None)
                    msg.info(request, "Something went wrong, please try again")
                    return redirect(comments)

            case _:
                try:
                    video_url = request.POST.get("video_url")
                    video_id = video_url.split("=", 1)[1]

                    order = "relevance"
                    maxResults = 25
                    pageID = 1
                    previousPageID = 1
                    searchInput = ""

                    if video_metadata_temp:
                        video_metadata_temp.clear()

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

                except Exception:
                    pageTokens.clear()
                    pageTokens.append(None)
                    msg.info(request, "Url is incorrect")
                    return redirect(comments)

    # On first load
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
            url = url.split("list=", 1)[1]
            playlist_id = url.split("&", 1)[0]

            # Store data in user history
            if "username" in login_context:
                username = login_context["username"]
                storage = user_data_storage.objects.get(
                    user=User.objects.get(username=username)
                )

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
                    time = dt.now()
                    info = [
                        title,
                        request.POST.get("url"),
                        time.strftime("%d/%m/%Y %H:%M"),
                    ]
                    storage.transferred_playlists_history.append(info)
                    storage.save()


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
    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "manage_account_General.html", context)


@login_check
def manage_account_Overview(request, login_context):
    username = login_context["username"]

    storage = user_data_storage.objects.get(user=User.objects.get(username=username))

    for video in storage.download_history[-6:]:
        del video[3]

    context = {
        "vid_downloads_quantity": len(storage.download_history),
        "prompts_quantity": len(storage.prompts_history),
        "filtered_comments_quantity": len(storage.filtered_comments_history),
        "transferred_playlists_quantity": len(storage.transferred_playlists_history),
        
        "download_history": storage.download_history[-6:],
        "prompts_history": storage.prompts_history[-6:],
        "filtered_comments_history": storage.filtered_comments_history[-6:],
        "transferred_playlists_history": storage.transferred_playlists_history[-6:],
    }

    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "manage_account_Overview.html", context)


@login_check
def manage_account_Private(request, login_context):
    context = {}
    context.update(login_context)
    context.update({"sites_context": sites_context})

    return render(request, "manage_account_Private.html", context)


# Non-views functions


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
        # Call the API to retrieve the video details
        request = youtube2.videos().list(
            part="snippet,statistics,contentDetails", id=video_id
        )

        response = await asyncio.to_thread(request.execute)

        # Extract the snippet and statistics from the response
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

        length = isodate.parse_duration(content_details["duration"])

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
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
    video_id, order, maxResults, previousPageID, pageID, searchInput, quotaUser
):
    try:
        # Retrieve the comments for the specified video
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="html",
            order=order,
            maxResults=maxResults,
            pageToken=pageTokens[-1],
            quotaUser=quotaUser,
        )

        # Process the comments
        processed_comments = []

        match (int(pageID) - int(previousPageID)):
            case 1:
                response = await asyncio.to_thread(request.execute)

                if "nextPageToken" in response:
                    pageTokens.append(response["nextPageToken"])
                    request = youtube.commentThreads().list_next(request, response)

            case 0:
                pass

            case -1:
                pageTokens.pop()
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="html",
                    order=order,
                    maxResults=maxResults,
                    pageToken=pageTokens[-1],
                    quotaUser=quotaUser,
                )

        response = await asyncio.to_thread(request.execute)

        if "nextPageToken" not in response:
            processed_comments.append("last_page")

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
                    snippet = comment["snippet"]["topLevelComment"]["snippet"][
                        "textDisplay"
                    ]
                    highlighted_comment = re.sub(
                        f"({re.escape(searchInput)})",
                        r"<mark>\1</mark>",
                        snippet,
                        flags=re.IGNORECASE,
                    )
                    comment["snippet"]["topLevelComment"]["snippet"][
                        "textDisplay"
                    ] = highlighted_comment

                for comment in filtered_comments:
                    # Extract the comment snippet
                    snippet = comment["snippet"]["topLevelComment"]["snippet"]

                    author = snippet["authorDisplayName"]
                    channel_url = snippet["authorChannelUrl"]
                    text = snippet["textDisplay"]
                    likes = f"{snippet['likeCount']:,}"
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
                            "profile_image_url": profile_image_url,
                            "publish_date": publish_date,
                        }
                    )
        else:
            if "items" in response:
                for comment in response["items"]:
                    # Extract the comment snippet
                    snippet = comment["snippet"]["topLevelComment"]["snippet"]
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

        if order == "time":
            date_format = "%Y-%m-%d %H:%M:%S"
            date1 = dt.strptime(processed_comments[0].get("publish_date"), date_format)
            date2 = dt.strptime(processed_comments[1].get("publish_date"), date_format)

            if date1 < date2:
                processed_comments[0]["pinned"] = True

        return processed_comments

    except HttpError as e:
        error_message = f"An HTTP error {e.resp.status} occurred: {e.content}"
        raise HttpError(e.resp, error_message)


async def get_video_comments_view_async(
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
        return {"error": "No video_id parameter provided"}, 400

    try:
        match isFirstTime:
            case True:
                video_url = "https://www.youtube.com/watch?v=" + video_id

                comments_and_VidInfo = await asyncio.gather(
                    get_video_comments(
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

                video_metadata_temp.update(comments_and_VidInfo[1])

                comments_and_VidInfo = {
                    "comments": comments_and_VidInfo[0],
                    "video_metadata": comments_and_VidInfo[1],
                }

                return comments_and_VidInfo

            case False:
                comments = await get_video_comments(
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
                    "video_metadata": video_metadata_temp,
                }

                return comments_and_VidInfo

    except HttpError as e:
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

    if video_id is not None:
        context = {
            "order": order,
            "maxResults": maxResults,
            "pageID": int(pageID),
            "video_id": video_id,
            "searchInput": searchInput,
        }

        # Reset previous saved pageTokens
        if previousPageID == "1" and pageID == "1":
            pageTokens.clear()
            pageTokens.append(None)

        if login_context.get("logged"):
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

        if stopRequest and stopRequest2:
            previousPageID = pageID

        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comments_and_VidInfo = loop.run_until_complete(
            get_video_comments_view_async(
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
                time = dt.now()

                try:
                    info = [
                        comments_and_VidInfo["video_metadata"]["title"],
                        "https://www.youtube.com/watch?v=" + video_id,
                        time.strftime("%d/%m/%Y %H:%M"),
                    ]
                    storage.filtered_comments_history.append(info)
                    storage.save()
                except Exception:
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
