"""
This module contains the backend logic for the Gemini chatbot.
"""

import os
import time
import base64
import traceback
import requests
from musicpy import chord, play
import google.generativeai as genai
from configuration import (
    GOOGLE_API_KEY,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    USER_INSTRUCTION,
    SYSTEM_INSTRUCTION,
    SAFETY_SETTINGS,
)


def save_uploaded_file(uploaded_file):
    """Save uploaded file"""
    path_name = os.path.join("uploads", uploaded_file.name)
    with open(path_name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path_name


# Configure Generative AI
genai.configure(api_key=GOOGLE_API_KEY)


class GeminiChat:
    """Gemini Chat class"""

    def __init__(self):
        """Initialize Gemini Chat object with user module"""
        self.model = genai.GenerativeModel(
            "models/gemini-1.5-pro-latest",
            safety_settings=SAFETY_SETTINGS,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.GenerationConfig(temperature=0.9),
        )
        self.chat_model = self.model.start_chat()

    def ask_response(self, prompt_content):
        """Ask response from Gemini chat model"""
        response = self.chat_model.send_message([USER_INSTRUCTION] + prompt_content)
        return response.text

    def upload_files_to_genai(self, uploaded_files):
        """Upload files to Generative AI"""
        prompt_content = []
        relative_path = []
        for uploaded_file in uploaded_files:
            path_name = save_uploaded_file(uploaded_file)
            relative_path.append(path_name)
            prompt_content.append(genai.upload_file(path_name))
        return prompt_content, relative_path

    def close(self):
        """Close chat model"""
        print("Chat history is ended.")


class SpotifyAPI:
    """Spotify API class"""

    def __init__(self):
        self.access_token = self._get_access_token(
            SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
        )

    def _get_access_token(self, client_id, client_secret):
        """Get Spotify access token"""
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic "
            + base64.b64encode((client_id + ":" + client_secret).encode()).decode(),
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(url, headers=headers, data=data, timeout=2)
        access_token = response.json()["access_token"]
        return access_token

    def extract_detailed_info(self, response):
        """Extract detailed information from Spotify response"""
        detailed_info = {}
        detailed_info["artist_name"] = [
            (artist["name"], list(artist["external_urls"].values())[0])
            for artist in response["artists"]
        ]
        detailed_info["album_id"] = response["id"]
        detailed_info["name"] = response["name"].title()
        detailed_info["url"] = list(response["external_urls"].values())[0]
        detailed_info["release_date"] = response["release_date"]
        detailed_info["image"] = response["images"][0]["url"]
        return detailed_info

    def _search_one_song(self, song_name):
        """Spotify search for a song"""
        print("Searching for song...", song_name)
        url = "https://api.spotify.com/v1/search"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"q": song_name, "type": "album"}
        response = requests.get(url, headers=headers, params=params, timeout=2).json()
        response = response["albums"]["items"][0]
        time.sleep(0.2)
        return self.extract_detailed_info(response)

    def search_songs(self, song_names):
        """Search for songs"""
        print("Searching for songs...", song_names)
        existing_songs = set()
        song_infos = []
        for song_name in song_names:
            song = self._search_one_song(song_name)
            if song["album_id"] not in existing_songs:
                song_infos.append(song)
                existing_songs.add(song["album_id"])
        print(len(song_infos), "songs found.")
        return song_infos


class Counter:
    """Counter class for session state"""

    def __init__(self):
        self.count = 0

    def increment(self):
        """Increment counter"""
        self.count += 1
        print("State:", self.count)
        return self.count


def create_music(music):
    """Create a small piece of music from music data"""
    try:
        num_repeat = 2
        notes = music["note"] * num_repeat
        durations = music["duration"] * num_repeat
        bpm = int(music["bpm"])
        music = chord(notes=notes, interval=durations)
        play(music, bpm * 4)
        os.system("mv temp.mid uploads/music.mid")
        return "uploads/music.mid"
    except Exception as e:
        traceback.print_exc()
        return "music.mid"
