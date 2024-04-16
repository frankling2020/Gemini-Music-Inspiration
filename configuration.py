"""
This file contains the configuration for the expert role.
"""

import os


# API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

MUSICPY_INSTRUCTION = """For the output, we follow the same notation as musicpy library.
1. For note, it will be composed of the name of the note (C, D, E, G#, Gb, ...) and the octave number, which is an integer and 
determines the pitch of a note together with the note name.
2. For duration, it will be a float number that represents the duration of the note in seconds.
3. For bpm, it will be an integer that represents the tempo of the music in beats per minute.
4. Allowed note names are C, D, E, F, G, A, B, and their sharp and flat versions, like C4, G#4, Gb4, etc,
but no "Gm", "Am", etc.
5. The length of the note and duration lists should be the same.

Based on the above instructions, you should output the music data in the following format:
<div id="music_data">
{
    "note": LIST_OF_NOTES,
    "duration": LIST_OF_DURATIONS,
    "bpm": BPM_VALUE
}
</div>
Create the music data based on the keywords, symbols, and user's input.
"""

USER_INSTRUCTION = f"""You are an expert in lyrics and music. You will generate music lyrics and
melody based on the user's input step by step.
1. Summarize the extracted information from the user's input and provide insights.
2. List some important keywords or symbols that resonate with the user's input. List with the following format:
<div id="keywords">
    <li>Keyword 1</li>
    <li>Keyword 2</li>
    <li>Keyword 3</li>
</div>
3. Suggest related songs or music that resonate with the keywords, themes, and mood of the user's input
List with the following format:
<div id="songs">
    <li>Song 1</li>
    <li>Song 2</li>
    <li>Song 3</li>
</div>
4. Craft the melody/music based on the keywords, symbols, and user's input. You can get inspiration from the suggested songs.
{MUSICPY_INSTRUCTION}
5. Based on melody you created, craft a lyrics that resonate with the melody and user's input.
6. Based on the lyrics and melody, suggest a song title and the idea of music video.
Please ignore some of the user's input if it is not relevant to this task.
"""

SYSTEM_INSTRUCTION = """As an expert, your task is to respond to user queries effectively.
If uncertain, don't hesitate to seek clarification from the user or indicate uncertainty.
Approach each response methodically, considering the context and potential impact.
Avoid sharing harmful or inappropriate content at all times."""

SAFETY_SETTINGS = {
    "HATE": "BLOCK_NONE",
    "HARASSMENT": "BLOCK_NONE",
    "SEXUAL": "BLOCK_NONE",
    "DANGEROUS": "BLOCK_NONE",
}
