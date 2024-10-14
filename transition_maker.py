from twelvelabs import TwelveLabs
import requests
 
client = TwelveLabs(api_key=# <use your own API key please :)>)
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
    "x-api-key": # <use your own API key :)>,
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

def get_comment(prompt, video, headers=headers):
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

headers_mine = { #needed because the general credits ran out
    "accept": "application/json",
    "x-api-key": ##<use your own API key :)>,
    "Content-Type": "application/json"
}

""" ONLY NECESSARY WHEN CREATING A NEW INDEX
url = "https://api.twelvelabs.io/v1.2/indexes"

payload = {"engines":[{"engine_options": ["visual", "conversation"],"engine_name": "pegasus1.1"}],"index_name": "edit"}

response = requests.post(url, json=payload, headers=headers_mine)

upload_id = response.json()["_id"]
print(upload_id)
"""

upload_id = "670b8081eaac6725641d68b8"

client_mine = TwelveLabs(api_key=# <use your own API key :)>)

from twelvelabs.models.task import Task
def on_task_update(task: Task):
    print(f"  Status={task.status}")

def compare_transition(videos1,videos2,transition_name,wanted=2):
    combined_videos = []

    # Iterate over all combinations of videos1 and videos2
    for i, video1 in enumerate(videos1):
        for j, video2 in enumerate(videos2):
            concatenate_videos([video1,video2],f"{transition_name}{i}{j}.mp4")
            task = client_mine.task.create(index_id=upload_id, file=f"{transition_name}{i}{j}.mp4", language="en")
            task.wait_for_done(sleep_interval=10, callback=on_task_update)
            quality = get_comment("smoothness of the transition between the two stitched videos", {"id":task.video_id},headers_mine)
            video_props = {"name": f"{transition_name}{i}{j}.mp4", "id":task.video_id,"quality":quality}
            combined_videos.append(video_props)

    combined_videos = sorted(combined_videos, key=lambda x: x["quality"], reverse=True)[:wanted]

    return combined_videos

prompt1 = "clown"
quality1 = "scary"

prompt2 = "forest"
quality2 = "calm"

videos = find_video(prompt1,2,quality1)
videos2 = find_video(prompt2,2,quality2)

for i,video in enumerate(videos):
    get_video(videos[i],f"{prompt1}{i}.mp4")
    get_video(videos2[i], f"{prompt2}{i}.mp4")

sorted_videos = compare_transition([f"{prompt1}0.mp4",f"{prompt1}1.mp4"],[f"{prompt2}0.mp4",f"{prompt2}1.mp4"],"edited")
print(f"1st:{sorted_videos[0]["name"]}")
print(f"2nd:{sorted_videos[1]["name"]}")
