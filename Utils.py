import openai
from youtubesearchpython import *
from youtube_transcript_api import YouTubeTranscriptApi
import pprint

API_KEY = "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"
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

    print(f"got Thumbnail for {title}")
    thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    
    # video_id = get_video_id(video_url)
    if not video_id:
        return False
    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id)
        subtitleText = " ".join(getSubTitleText(srt))
    except:
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



