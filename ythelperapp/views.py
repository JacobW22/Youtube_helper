from django.shortcuts import render, redirect
from pytube import YouTube
import datetime

# Create your views here.


def main_page(request):

    if request.method == 'POST':
        link = request.POST.get('sended_link')
        return redirect('download/?link=' + link)

    return render(request, 'main_page.html')



def download_page(request):

    link = request.GET.get('link')
    yt = YouTube(link)

    length = str(datetime.timedelta(seconds=yt.length))
    
    views = f'{yt.views:,}' # For 100000 = 100,000 etc.

    name = request.GET.get('name')


    # For sd quality video files
    if name == "sd_quality":

        sd_quality_stream = yt.streams.get_by_resolution("360p")

        if sd_quality_stream == None:
            sd_quality_stream = yt.streams.get_highest_resolution()

        sd_quality_stream.download(output_path="static/",filename="video.mp4")

        return redirect('video/?link=' + link)


    # For downloading highest quality video files
    if name == "hd_quality":

        hd_quality_stream = yt.streams.get_by_resolution("1080p")

        if hd_quality_stream == None:
            hd_quality_stream = yt.streams.get_highest_resolution()

        hd_quality_stream.download(output_path="static/",filename="video.mp4") 

        return redirect('video/?link=' + link)


    # For downloading audio files
    if name == "mp3":

        mp3_stream = yt.streams.get_audio_only("mp4")

        mp3_stream.download(output_path="static/",filename="audio.mp3")

        return redirect('audio/?link=' + link)


    context = {
    'link' : link,
    'title' : yt.title,
    'views' : views,
    'thumbnail' : yt.thumbnail_url,
    'description' : yt.description,
    'publish_date' : yt.publish_date,
    'length' : length,
    }

    return render(request, 'download_page.html', context)



def download_video(request):
    link = request.GET.get('link')
    yt = YouTube(link)

    context = {
    'title' : yt.title,
    'thumbnail' : yt.thumbnail_url,
    }

    return render(request, 'video_download.html', context)
    


def download_audio(request):
    link = request.GET.get('link')
    yt = YouTube(link)

    context = {
    'title' : yt.title,
    'thumbnail' : yt.thumbnail_url,
    }

    return render(request, 'audio_download.html', context)