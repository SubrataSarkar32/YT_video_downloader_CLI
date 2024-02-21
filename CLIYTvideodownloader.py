# CLI YT video downloader
import os
from moviepy.editor import *
from slugify import slugify
from pytube import YouTube
from pytube import*
import moviepy
from bs4 import BeautifulSoup 
import moviepy.editor as mymovie
import requests


def download_yt_video(yt_link, download_path, res="1080p"):
    yt = YouTube(yt_link)
    filenamee = slugify(YouTube(yt_link).title)
    video = yt.streams.filter(adaptive=True, res=res).first()
    size = yt.streams.filter(adaptive=True, res=res).first().filesize
    print(f"File Size: {round(size* 0.000001, 2)} MB")
    print("Downloading video-----")
    try:
        video.download(download_path, filenamee+".mp4")
        print("Downloaded video!")
        return True, filenamee
    except Exception as e:
        print(e)
        print("Video Download Failed!!!")
        return False, filenamee


def download_yt_audio(yt_link, download_path):
    yt = YouTube(yt_link)
    filenamee = slugify(YouTube(yt_link).title)
    try:
        print("Downloading Audio-----")
        audio = yt.streams.filter(only_audio=True).last().download(download_path, filenamee+".webm")
        print("Converting to webm---")
        clip = moviepy.editor.AudioFileClip(os.path.join(download_path, filenamee+".webm"))
        print("Generating MP3-----")
        clip.write_audiofile(os.path.join(download_path, filenamee+".mp3"))
        clip.close()
        os.remove(audio)
        return True, filenamee
    except Exception as e:
        return False, filenamee


def combine_audio_video(yt_link, download_path, title):
    filename1 = YouTube(yt_link).title 
    print(filename1)
    filenamee = slugify(filename1)
    videofolder = os.path.join(download_path, filenamee+".mp4")
    audiofolder = os.path.join(download_path, filenamee+".mp3")

    
    inputvideo=videofolder
    inputaudio=audiofolder
    outputvideo=os.path.join(download_path, title+".mp4")
    with open(outputvideo, "wb") as f1:
        f1.close()

    videoclip=mymovie.VideoFileClip(inputvideo)
    audioclip=mymovie.AudioFileClip(inputaudio)
    finalclip=videoclip.set_audio(audioclip)
    finalclip.write_videofile(outputvideo,fps=60)
    
    os.remove(videofolder)
    os.remove(audiofolder)
    return True


download_path = os.path.dirname(os.path.realpath(__file__))
print("Current path is : ", download_path)
input_cont = "L"
while not(input_cont == "Y" or input_cont == "N"):
    input_cont = input("Do you want to continue with current path(Y/N):")
if input_cont == "N":
    download_path = input("Enter new path: ")
while not(os.path.isdir(download_path)):
    print("Not a valid path!!!")
    download_path = input("Enter new path: ")
yt_link = input("Provide YT link: ")
r = requests.get(yt_link) # random video id
while "This video isn't available anymore" in r.text:
    print("Invalid link provided")
    yt_link = input("Provide YT link: ")
    r = requests.get(yt_link) # random video id
# converting the text
res = "L"
while not(res == "1080p" or res == "720p" or res == "480p" or res == "360p" or res == "240p" or res == "144p"):
    res = input("Enter video resolution to download(1080p/720p/480p/360p/240p/144p):") 
s = BeautifulSoup(r.text, "html.parser") 
    
# finding meta info for title 
# title = s.find("yt-formatted-string", class_="style-scope ytd-watch-metadata").text
for title1 in s.find_all('title'):
    title = title1.get_text()
    break
title = title.replace(" - YouTube", "")
title = title.replace("/", "")
title = title.replace("\\", "")
print(title)
flag, filename = download_yt_video(yt_link, download_path, res=res)
if flag:
    flag1, filename = download_yt_audio(yt_link, download_path)
    if flag1:
        flag2 = combine_audio_video(yt_link, download_path, title)
print("Exiting...")
