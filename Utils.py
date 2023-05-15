import openai
from youtubesearchpython import *
from youtube_transcript_api import YouTubeTranscriptApi
import pprint
import yt_dlp as youtube_dl
import time
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

API_KEY = os.environ.get("Open_AI_Key")
print(API_KEY)
pp = pprint.PrettyPrinter(indent=4)
openai.api_key = API_KEY




def get_video_id(link):

    if 'youtube.com/watch?v=' in link:
        video_id = link.split('youtube.com/watch?v=')[1]
        if '&' in video_id:
            video_id = video_id.split('&')[0]
    elif 'youtu.be/' in link:
        video_id = link.split('youtu.be/')[1]
        if '?' in video_id:
            video_id = video_id.split('?')[0]
    else:
        print('Invalid YouTube video link.')
        return None
    return video_id

def getSubTitleText(srtFile):
    final_text = [ d.get("text") for d in srtFile]
    return final_text

def get_info(video_url):

    videoInfo = Video.getInfo(video_url, mode = ResultMode.json)

    channel = videoInfo["channel"]["name"]
    pubLishDate = videoInfo["publishDate"]
    title = videoInfo["title"]
    viewCount = videoInfo["viewCount"]["text"]
    video_id = videoInfo["id"]
    duration = int(videoInfo["duration"]["secondsText"])

    print(f"got Thumbnail for {title}")
    print(API_KEY)
    thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    
    # video_id = get_video_id(video_url)
    if not video_id:
        return False
    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id)
        subtitleText = " ".join(getSubTitleText(srt))
        print(subtitleText)
    except:
        if duration < 25 * 60:
            # try:
            subtitleText = get_transcript_audio(video_url)
            # except:
            #     print("HERE")
            #     subtitleText = "None"
        else:
            print("here")
            subtitleText = "None"

    
    info2send = {
        "channel": channel, 
        "title": title,
        "viewCount": viewCount,
        "pubLishDate": pubLishDate,
        "subtitles": str(subtitleText)
        }
    
    return (title, channel, thumbnail, info2send)

def get_summary(info2send):

    
    title = info2send["title"]
    print(f"Getting Summary for {title}")


    messages = [{"role": "system",
                 "content": "You are a YouTube video summarizer. Your name is 'Summarizer' and you were created by 'Shrey'. You are upbeat and fun. In the next message, I will send information of a YouTube vide in a dictionary format. This will have the channel name, the title, view count, publish date, and the subtitles of the video. You will summarize this video, mainly by the subtitles, and reply with that summary. You can use the context provided by the channel name and other info you have if needed.  My following questions may be based on the video summary/description you provide."},
                {"role": "user",
                 "content": str(info2send)}]
    
    if info2send["subtitles"] == "None":
        print(1)
        return "Summary not available for this video", messages

    completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = messages)

    response = completion["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": response})

    return response, messages

def get_response(user_message, messages):
    print(f"getting response for {user_message}")
    user_message = {"role": "user", "content": user_message}
    messages.append(user_message)

    completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = messages)

    response = completion["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": response})

    return response, messages

def download_youtube_audio(url):
    filename = str(time.time())
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'tempAudio' +filename+'.%(ext)s',
    }

    # Download the audio
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Return the local mp3 file path
    
    mp3_file_path = "tempAudio" + filename + ".mp3"
    return mp3_file_path


def get_transcript_audio(URL):

    # audio_obj = open("temp_audio_file.mp3", "rb")
    audio_obj = open(download_youtube_audio(URL), "rb")
    print("GOT AUDIO")
    response = openai.Audio.transcribe(
        api_key=API_KEY,
        model="whisper-1",
        file = audio_obj
    )

    return response["text"]


