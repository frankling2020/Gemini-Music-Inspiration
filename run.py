"""
This module contains the backend logic for the Gemini chatbot.
"""

import os
import pyperclip
import streamlit as st
from bs4 import BeautifulSoup
from backend import GeminiChat, SpotifyAPI, Counter, create_music


def assign_if_not_exists(attr_name, attr_value):
    """Create attribute if it does not exist"""
    if (
        not hasattr(st.session_state, attr_name)
        or getattr(st.session_state, attr_name) is None
    ):
        setattr(st.session_state, attr_name, attr_value)


def reset_if_exists(attr_name, attr_value):
    """Reset attribute if it exists"""
    if hasattr(st.session_state, attr_name):
        if attr_name == "gemini_chat" and st.session_state.gemini_chat:
            st.session_state.gemini_chat.close()
        setattr(st.session_state, attr_name, attr_value)


def pre_session_state():
    """Pre-session state initialization"""
    # Create the directory for uploads
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    # 'counter' object
    assign_if_not_exists("counter", Counter())
    # Initialize session state to persist chat history
    assign_if_not_exists("chat_history", [])


def init_session_state():
    """Initialize session state"""
    reset_chat_history()
    # Initialize Gemini Chat object
    assign_if_not_exists("gemini_chat", GeminiChat())
    # Initialize Spotify API object
    assign_if_not_exists("spotify_api", SpotifyAPI())
    assign_if_not_exists("started", True)


def reset_chat_history():
    """Reset chat history"""
    reset_if_exists("chat_history", [])
    reset_if_exists("gemini_chat", None)
    reset_if_exists("spotify_api", None)
    reset_if_exists("started", False)
    if os.path.exists("uploads"):
        for file in os.listdir("uploads"):
            os.remove(os.path.join("uploads", file))


def display_song_info(song_info):
    """Display song information with a Spotify-like format"""
    with st.container(border=True):
        st.image(song_info["image"], use_column_width=True)
        st.markdown(f"[**{song_info['name']}**]({song_info['url']})")
        st.markdown(f"**Release Date**: {song_info['release_date']}")
        st.markdown("**Artists**")
        for artist in song_info["artist_name"]:
            st.markdown(f"- [{artist[0]}]({artist[1]})")


def extract_infos(bot_response):
    """Extract information from bot response"""
    soup = BeautifulSoup(bot_response, "html.parser")
    infos = []
    music = ""
    for div in soup.find_all("div"):
        if div.get("id").startswith("keyword"):
            infos += [li.text.strip() for li in div.find_all("li")]
        elif div.get("id").startswith("song"):
            infos += [li.text.strip() for li in div.find_all("li")]
        elif div.get("id").startswith("music"):
            music = eval(div.text.strip())
            print(music)
    infos = [info.lower() for info in infos if len(info) > 0]
    return list(set(infos)), music


def create_chat_history():
    """Create chat history"""
    # Display chat history
    st.subheader("Chat History")
    num_history = len(st.session_state.chat_history)
    for mid, entry in enumerate(st.session_state.chat_history):
        message = entry["response"]
        need_expanded = mid == num_history - 1
        with st.expander(f"Message {mid}", expanded=need_expanded):
            for media in entry["media"]:
                if media.endswith((".png", ".jpg", ".jpeg")):
                    st.image(media, use_column_width=True)
                elif media.endswith((".mp3")):
                    st.audio(media, format="audio/wav")
                elif media.endswith((".mp4")):
                    st.video(media)
            st.markdown(message, unsafe_allow_html=True)
            copy_button_id = f"copy_button_{mid}"
            with open(entry["music"], "rb") as f:
                st.download_button(
                    label="Download Midi File",
                    data=f.read(),
                    file_name="music.mid",
                )
            google_music_generation_link = "https://aitestkitchen.withgoogle.com/tools/music-fx"
            st.write(f"### [Go to Google Music Generation]({google_music_generation_link})")
            if st.button(label="📋", key=copy_button_id):
                pyperclip.copy(message)
            cols = st.columns([3, 3, 3])
            for i, col in enumerate(cols):
                with col:
                    for song_info in entry["song_infos"][i::3]:
                        display_song_info(song_info)


def prompt_file_uploader():
    """Prompt file uploader"""
    figure_file = st.file_uploader(
        "Upload Figure or Audio File",
        type=["png", "jpg", "jpeg", "mp3", "mp4"],
        accept_multiple_files=True,
    )
    return figure_file


def main():
    """Main function for Streamlit app"""
    st.image("title.jpg", use_column_width=True)
    st.title("Music Inspiration with Gemini Chat")
    # Initialize session state
    pre_session_state()
    # Create sidebar to upload and call functions
    with st.form("user_input_form", clear_on_submit=True):
        # File uploader for figure
        files = prompt_file_uploader()
        # Button to send the user input to Gemini Chat and display the response
        b1, b2, _ = st.columns([1, 1, 7])
        with b1:
            if st.form_submit_button("Send"):
                if not getattr(st.session_state, "started", False):
                    init_session_state()
                gemini_chat = st.session_state.gemini_chat
                spotify_api = st.session_state.spotify_api
                history = st.session_state.chat_history
                st.session_state.counter.increment()
                files, file_paths = gemini_chat.upload_files_to_genai(files)
                bot_response = gemini_chat.ask_response(files)
                song_keywords, music = extract_infos(bot_response)
                music_path = create_music(music)
                song_infos = spotify_api.search_songs(song_keywords)
                history.append(
                    {
                        "song_infos": song_infos,
                        "media": file_paths,
                        "music": music_path,
                        "response": bot_response,
                    }
                )
        with b2:
            if st.form_submit_button("Reset"):
                reset_chat_history()
    # Display chat history
    create_chat_history()


if __name__ == "__main__":
    main()
