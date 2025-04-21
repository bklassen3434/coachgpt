import requests
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import json
from helper import is_garbage
from llms import summarize_chunks
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


# ------------------ Input Channel & Get Channel ID ------------------ #
handle = "antonellisoftball"
url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={handle}&key={YOUTUBE_API_KEY}"
res = requests.get(url).json()
CHANNEL_ID = res["items"][0]["snippet"]["channelId"]



# ------------------ Get Channel Uploads Playlist ------------------ #  
def get_channel_uploads_playlist(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={YOUTUBE_API_KEY}"
    res = requests.get(url).json()
    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]



# ------------------ Get All Video IDs ------------------ #
def get_all_video_ids(playlist_id):
    video_ids = []
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
    while url:
        res = requests.get(url).json()
        video_ids += [item["contentDetails"]["videoId"] for item in res["items"]]
        next_page_token = res.get("nextPageToken")
        if next_page_token:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={next_page_token}&key={YOUTUBE_API_KEY}"
        else:
            url = None
    return video_ids



# ------------------ Get Video Details ------------------ #
def get_video_details(video_ids, handle = handle):
    video_details = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        ids = ",".join(chunk)
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={ids}&key={YOUTUBE_API_KEY}"
        res = requests.get(url).json()
        for item in res["items"]:
            video_id = item["id"]
            duration = item["contentDetails"]["duration"]
            if "PT" in duration and "M" not in duration:
                title = item["snippet"]["title"]
                try:
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript_text = " ".join([entry["text"] for entry in transcript_data])
                    if is_garbage(transcript_text):
                        continue

                    video_details.append({
                        "transcript": transcript_text, # transcript text
                        "title": title,
                        "video_id": video_id,
                    })
                    
                except Exception as e:
                    continue

                
    return video_details



# ------------------ Add Metadata ------------------ #
def add_metadata(video_details, summaries, handle = handle, channel_id = CHANNEL_ID):
    formatted = []
    for video, summary in zip(video_details, summaries):
        # Create unique ID from channel name and video ID
        chunk_id = f"{handle.lower().replace(' ', '_')}_{video['video_id']}"
        
        metadata = {
            "id": chunk_id,
            "source": "Youtube Transcript", 
            "channel_name": handle,
            "channel_id": channel_id,
            "collection": "Coaching Videos",
            "video_title": video["title"],
            "video_id": video["video_id"],
            "url": f"https://www.youtube.com/watch?v={video['video_id']}",
            "summary": summary
        }
        formatted.append({
            "content": video["transcript"],
            "metadata": metadata
        })
    return formatted



# ------------------ Main Pipeline ------------------ #
def main():
    playlist_id = get_channel_uploads_playlist(CHANNEL_ID)
    video_ids = get_all_video_ids(playlist_id)
    video_details = get_video_details(video_ids)

    transcripts = [video["transcript"] for video in video_details]
    summaries = summarize_chunks(transcripts)

    youtube_chunks = add_metadata(video_details, summaries)

    with open(f"preprocessed/youtube_shorts_{handle.strip().lower()}_.json", "w") as f:
        json.dump(youtube_chunks, f, indent=2)


if __name__ == "__main__":
    main()
