import os
from pytubefix import YouTube
import ffmpeg

url = input("url >")

yt = YouTube(url, 'WEB')
print(yt.title)

# progressive audio files contain both audio and video but the quality is 480p

# download video track
video = yt.streams.filter(progressive=False, file_extension="mp4", res="1080p").first()
video.download()
os.rename(video.title+".mp4","video.mp4")

# download audio track
audio = yt.streams.filter(only_audio=True).first()
audio.download()
os.rename(audio.title+".m4a","audio.m4a")

# merge audio and video using ffmpeg
video_stream = ffmpeg.input('video.mp4')
audio_stream = ffmpeg.input('audio.m4a')

#ffmpeg.output(audio_stream, video_stream, 'out.mp4',  crf=30,  preset='veryfast').run()
# using multiple threads
ffmpeg.output(audio_stream, video_stream, 'out.mp4',  crf=36,  preset='superfast', threads=5).run()    

os.remove('video.mp4')
os.remove('audio.m4a')
