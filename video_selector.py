from twelvelabs import TwelveLabs
import requests

client = TwelveLabs(api_key="tlk_241Z16H2R70KP22J4CV3K22801XG")
def find_video(prompt,wanted,quality):
  page = client.search.query(index_id="66f1cde8163dbc55ba3bb220", query_text=prompt, options=["visual"])
  video_vec = []
  for clip in page.data:
      if clip.confidence == "high":
        video_dict = {"id":clip.video_id,"start":clip.start, "end":clip.end}
        video_quality = get_comment(quality, video_dict)
        video_dict["quality"] =video_quality
        video_vec.append(video_dict)
  video_vec = sorted(video_vec, key=lambda x: x["quality"], reverse=True)[:wanted]
  return video_vec


headers = {
    "accept": "application/json",
    "x-api-key": "tlk_241Z16H2R70KP22J4CV3K22801XG",
    "Content-Type": "application/json"
}
from moviepy.editor import VideoFileClip

def get_video(video_info, duration=9999, save_file=None):
    url = f"https://api.twelvelabs.io/v1.2/indexes/{"66f1cde8163dbc55ba3bb220"}/videos/{video_info["id"]}"
    response = requests.get(url, headers=headers)
    video_url = response.json()["hls"]["video_url"]
    start = video_info["start"]
    end = video_info["end"]
    if duration < video_info["end"]-video_info["start"]:
        end = video_info["start"]+duration
    clip = VideoFileClip(video_url).subclip(start, end)

    if save_file:
        clip.write_videofile(save_file, codec='libx264', audio_codec='aac')
    else:
        clip.preview()

def get_comment(prompt, video):
    url = "https://api.twelvelabs.io/v1.2/generate"

    payload = {
        "temperature": 0.7,
        "prompt": f"only output a number from 0-100 evaluating the following clip on these measures: {prompt}",
        "stream": False,
        "video_id": video["id"]
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()["data"]



videos = find_video("forest",3,"suspense")

get_video(videos[0],9999,"night_forest.mp4")
get_video(videos[1])
get_video(videos[2])
