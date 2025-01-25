from pytubefix import YouTube

url = input("url >")

yt = YouTube(url, 'WEB')
print(yt.title)

ys = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
ys.download()