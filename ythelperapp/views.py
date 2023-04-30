from django.shortcuts import render, redirect
from pytube import YouTube
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from .decorators import login_check, not_authenticated
from .models import user_data_storage, User

import datetime
import random
from datetime import datetime as dt

# Create your views here.


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
        # Get random item from history
        # Eliminate repetitions

        Download_videos_informations = []

        Download_history = random.sample(
            storage.download_history, len(storage.download_history)
        )
        Download_history = Download_history[:10]  # Limit to 10 slides

        for item in Download_history:
            it_is_in_dict = 0

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
                for dictionary in Download_videos_informations:
                    if item[0] in dictionary.values():
                        it_is_in_dict += 1

                if it_is_in_dict == 0:
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
        return redirect("download/?link=" + link)

    return render(request, "main_page.html", context)


@not_authenticated
def login_page(request):
    form = CreateUserForm()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password1")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome " + username)
            return redirect(main_page)
        else:
            messages.info(request, "Username or Password is incorrect")

    context = {
        "form": form,
    }
    return render(request, "login_page.html", context)


def logoutUser(request):
    logout(request)
    return redirect(main_page)


@not_authenticated
def sign_up_page(request):
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

            messages.success(request, user + " Welcome on board")
            return redirect(login_page)

    context = {"form": form}
    return render(request, "sign_up_page.html", context)


@login_check
def download_page(request, login_context):
    link = request.GET.get("link")
    yt = YouTube(link)
    title = yt.title
    thumbnail = yt.thumbnail_url

    length = str(datetime.timedelta(seconds=yt.length))

    views = f"{yt.views:,}"  # Format numbers 100000 = 100,000 etc.

    name = request.GET.get("name")

    # Store link in user database
    if "username" in login_context:
        username = login_context["username"]
        storage = user_data_storage.objects.get(
            user=User.objects.get(username=username)
        )
        time = dt.now()
        info = [link, title, thumbnail, time.strftime("%d/%m/%Y %H:%M")]
        storage.download_history.append(info)
        storage.save()

    # For downloading sd quality video files
    if name == "sd_quality":
        sd_quality_stream = yt.streams.get_by_resolution("360p")

        if sd_quality_stream == None:
            sd_quality_stream = yt.streams.get_highest_resolution()

        sd_quality_stream.download(output_path="static/", filename="video.mp4")

        return redirect("video/?link=" + link)

    # For downloading highest quality video files
    if name == "hd_quality":
        hd_quality_stream = yt.streams.get_by_resolution("1080p")

        if hd_quality_stream == None:
            hd_quality_stream = yt.streams.get_highest_resolution()

        hd_quality_stream.download(output_path="static/", filename="video.mp4")

        return redirect("video/?link=" + link)

    # For downloading audio files
    if name == "mp3":
        mp3_stream = yt.streams.get_audio_only("mp4")

        mp3_stream.download(output_path="static/", filename="audio.mp3")

        return redirect("audio/?link=" + link)

    context = {
        "link": link,
        "title": title,
        "views": views,
        "thumbnail": thumbnail,
        "description": yt.description,
        "publish_date": yt.publish_date,
        "length": length,
    }

    context.update(login_context)

    return render(request, "download_page.html", context)


@login_check
def download_video(request, login_context):
    link = request.GET.get("link")
    yt = YouTube(link)

    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
    }

    context.update(login_context)

    return render(request, "video_download.html", context)


@login_check
def download_audio(request, login_context):
    link = request.GET.get("link")
    yt = YouTube(link)

    context = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
    }

    context.update(login_context)

    return render(request, "audio_download.html", context)
