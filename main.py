from pytubefix import YouTube

url = input("url >")

yt = YouTube(url, 'WEB')
print(yt.title)

ys = yt.streams.get_highest_resolution()
ys.download()