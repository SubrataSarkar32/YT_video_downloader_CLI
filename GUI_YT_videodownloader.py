# GUI YT video downloader
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
from moviepy.editor import *
from slugify import slugify
from pytube import YouTube
from proglog import ProgressBarLogger
from pytube import*
import moviepy
from bs4 import BeautifulSoup 
import moviepy.editor as mymovie
import requests


window = tk.Tk()
window.geometry("550x180")
window.title("YT Video Downloader")

barVar1 = tk.DoubleVar()
barVar1.set(0)
barVar2 = tk.DoubleVar()
barVar2.set(0)
barVar3 = tk.DoubleVar()
barVar3.set(0)
downloadURL = tk.StringVar()
downloadURL.set("")
downloadLocation = tk.StringVar()
downloadLocation.set("")
downloadResolution = tk.StringVar()
downloadResolution.set("")
dfilename = tk.StringVar()
dfilename.set("")
yttitle = tk.StringVar()
yttitle.set("")


class MyBarLogger(ProgressBarLogger):
    def __init__(self, init_state=None, bars=None, ignored_bars=None,
                 logged_bars='all', min_time_interval=0, ignore_bars_under=0,
                 percent=0):
        super().__init__(init_state=None, bars=None, ignored_bars=None,
                         logged_bars='all', min_time_interval=0, ignore_bars_under=0)
        self.percent = percent
    def bars_callback(self, bar, attr, value,old_value=None):
        # Every time the logger progress is updated, this function is called        
        self.percent = (value / self.bars[bar]['total']) * 100
        print(self.percent)
        # print(bar,attr,percentage)
        # barVar.set(self.percent)

class DummyLogger():
    def __init__(self, percent=0):
        self.percent = 0


logger1 = DummyLogger()
logger2 = MyBarLogger()
logger3 = MyBarLogger()


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    logger1.percent = percentage_of_completion
    # barVar1.set(percentage_of_completion)


def on_complete(stream, file_path):
    logger1.percent = 100.0
    # barVar1.set(100.0)


def download_yt_video(yt_link, download_path, logger1, res="1080p"):
    yt = YouTube(yt_link, on_progress_callback=on_progress, on_complete_callback=on_complete)
    # yt.register_on_progress_callback(on_progress)
    filenamee = slugify(YouTube(yt_link).title)
    stream_list = []
    sel_res = 0
    for stream in yt.streams:
        if stream.resolution:
            resy = int(stream.resolution[:-1])
            stream_list +=[resy]
    stream_list = sorted(stream_list)
    print(stream_list)
    sel_res = stream_list[0]
    for entry in stream_list:
        if entry > int(res[:-1]):
            pass
        elif entry <= int(res[:-1]):
            sel_res = entry
    res = f"{sel_res}p"
    print(res)
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


def download_yt_audio(yt_link, download_path, logger2):
    yt = YouTube(yt_link)
    filenamee = slugify(YouTube(yt_link).title)
    try:
        print("Downloading Audio-----")
        audio = yt.streams.filter(only_audio=True).last().download(download_path, filenamee+".webm")
        print("Converting to webm---")
        clip = moviepy.editor.AudioFileClip(os.path.join(download_path, filenamee+".webm"))
        print("Generating MP3-----")
        clip.write_audiofile(os.path.join(download_path, filenamee+".mp3"), logger=logger2)
        clip.close()
        os.remove(audio)
        return True, filenamee
    except Exception as e:
        return False, filenamee


def combine_audio_video(yt_link, download_path, title, logger3):
    yt_obj = YouTube(yt_link)
    filename1 = yt_obj.title 
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
    finalclip.write_videofile(outputvideo, fps=60, logger=logger3)

    caption = yt_obj.captions.get_by_language_code('en')
    if caption:
        outputsrt=os.path.join(download_path, title+".srt")
        with open(outputsrt, "wb") as f2:
            f2.write(caption.generate_srt_captions())
            f2.close()
    
    os.remove(videofolder)
    os.remove(audiofolder)
    return True

def start_download():
    yt_link = downloadURL.get()
    if yt_link.startswith("https://www.youtube.com/watch?v="):
        r = requests.get(yt_link) # random video id
        if ("This video isn't available anymore" in r.text):
            messagebox.showwarning("showwarning", "Invalid YT link") 
        else:
            s = BeautifulSoup(r.text, "html.parser")
            for title1 in s.find_all('title'):
                title = title1.get_text()
                break
            title = title.replace(" - YouTube", "")
            title = title.replace("/", "")
            title = title.replace("\\", "")
            title = title.replace("|", "")
            print(title)
            yttitle.set(title)
            update_progress_bar1()
            flag, filename = download_yt_video(yt_link, download_path,  logger1=logger1, res=downloadResolution.get())
            dfilename.set(filename)
            if not flag:
                messagebox.showwarning("showwarning", "Video could not be downloaded")
    else:
        messagebox.showwarning("showwarning", "Invalid link") 
    
def update_progress_bar1():
    x = logger1.percent
    print("Bar Var1", x)
    if x < 100:
        barVar1.set(x)
        window.update_idletasks()
        window.after(1000, update_progress_bar1)
    else:
        window.update_idletasks()
        update_progress_bar2()
        yt_link = downloadURL.get()
        flag1, filename = download_yt_audio(yt_link, download_path, logger2=logger2)
        dfilename.set(filename)
        if not flag1:
            messagebox.showwarning("showwarning", "Audio could not be downloaded") 


def update_progress_bar2():
    x = logger2.percent
    print("Bar Var2", x)
    if x < 100:
        barVar2.set(x)
        window.update_idletasks()
        window.after(1000, update_progress_bar2)
    else:
        window.update_idletasks()
        update_progress_bar3()
        yt_link = downloadURL.get()
        title = yttitle.get()
        flag2 = combine_audio_video(yt_link, download_path, title, logger3= logger3)
        if not flag2:
            messagebox.showwarning("showwarning", "Audio Video mixixng Failed") 


def update_progress_bar3():
    x = logger3.percent
    print("Bar Var3", x)
    if x < 100:
        barVar3.set(x)
        window.update_idletasks()
        window.after(1000, update_progress_bar3)
    else:
        window.update_idletasks()
        messagebox.showinfo("showinfo", "Video downloaded successfully")


download_path = os.path.dirname(os.path.realpath(__file__))
downloadLocation.set(download_path)


def select_download_dir():
    global download_path
    # Show the open file dialog by specifying path
    f = filedialog.askdirectory(initialdir=download_path)
    download_path = f
    downloadLocation.set(f)

downloadResolution.set("1080p")
label1 = tk.Label(window, text='Current Download Location')
label1.place(x=50, y=5)
entry1 = tk.Entry(window, textvariable=downloadLocation, width="55")
entry1.place(x=200, y=5)
button= tk.Button(window, text='Change Download Path', command=select_download_dir)
button.place(x=400, y=25)
label2 = tk.Label(window, text='Select Download Resolution')
label2.place(x=50, y=30)
reschoosen = ttk.Combobox(window, width = 10, state="readonly", textvariable=downloadResolution)
reschoosen['values'] = ["1080p", "720p", "480p", "360p", "240p", "144p"]
reschoosen.place(x=50, y=50)
# entry3 = tk.Entry(window, textvariable=downloadResolution)
# entry3.pack()
label3 = tk.Label(window, text='YT Download URL')
label3.place(x=50, y=70)
entry2 = tk.Entry(window, textvariable=downloadURL, width="52")
entry2.place(x=150, y=70)
button= tk.Button(window, text='Download', command=start_download)
button.place(x=470, y=70)
bar1 = ttk.Progressbar(window, length=200, style='black.Horizontal.TProgressbar', variable=barVar1, mode='determinate')
bar1.place(x=0, y=95)
label4 = tk.Label(window, text='Downloading video')
label4.place(x=200, y=95)
bar2 = ttk.Progressbar(window, length=200, style='black.Horizontal.TProgressbar', variable=barVar2, mode='determinate')
bar2.place(x=0, y=115)
label5 = tk.Label(window, text='Downloading audio')
label5.place(x=200, y=115)
bar3 = ttk.Progressbar(window, length=200, style='black.Horizontal.TProgressbar', variable=barVar3, mode='determinate')
bar3.place(x=0, y=135)
label6 = tk.Label(window, text='Combining audio video')
label6.place(x=200, y=135)
# Start the event loop.
window.mainloop()