from twelvelabs import TwelveLabs
import requests

client = TwelveLabs(api_key="tlk_241Z16H2R70KP22J4CV3K22801XG")
def find_video(prompt,wanted,quality):
  page = client.search.query(index_id="66f1cde8163dbc55ba3bb220", query_text=prompt, options=["visual"])
  video_vec = []
  i = 0
  for clip in page.data:
      if clip.confidence == "high" and i<wanted+4:
        i+=1
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
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_video(video_info, save_file=None,duration=9999):
    url = f"https://api.twelvelabs.io/v1.2/indexes/{"66f1cde8163dbc55ba3bb220"}/videos/{video_info["id"]}"
    response = requests.get(url, headers=headers)
    video_url = response.json()["hls"]["video_url"]
    start = video_info["start"]
    end = video_info["end"]
    if duration < video_info["end"]-video_info["start"]:
        end = video_info["start"]+duration
    clip = VideoFileClip(video_url).subclip(start, end)

    if save_file == "return":
        return clip
    elif save_file:
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


def concatenate_videos(video_files, save_file=None):
    # Load the videos
    clips = [VideoFileClip(video) for video in video_files]

    # Concatenate the video clips
    final_clip = concatenate_videoclips(clips)
    final_clip.audio = final_clip.audio.set_fps(44100)
    # Write the result to a file
    if save_file:
        final_clip.write_videofile(save_file, codec='libx264', audio_codec='aac')
    else:
        final_clip.preview()

concatenate_videos(["car_chase.mp4","forest_morning.mp4"])
videos = find_video("car at night",3,"pov driving")
get_video(videos[0])
get_video(videos[1])
get_video(videos[2],"car_night_drive.mp4")


