from YMusic import app
from YMusic.core import userbot
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS

from pyrogram import filters
import asyncio
import random
import time
import config

PLAY_COMMAND = ["P", "PLAY"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

# Set up Spotify API client
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id="e319091f771445b18c029299505d5d4f",
    client_secret="293c334a2861415197a697b2d11dd4de"
))

def search_spotify_track(query):
    # Search for the track on Spotify
    results = spotify.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        title = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        duration = track['duration_ms'] // 1000  # Duration in seconds
        link = track['external_urls']['spotify']
        return title, artists, duration, link
    return None, None, None, None

async def download_spotify_audio(link):
    # Simulate downloading a track
    # Implement actual downloading logic here
    temp_file = f"temp{random.randint(1, 10000)}.mp3"
    # For demonstration, we simulate successful download
    return temp_file, "Sample Title", 180  # Duration in seconds

@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def play_spotify(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply_text("Song name kon dalega mai? 🤔")
        return

    query = message.text.split(maxsplit=1)[1]
    await message.reply_text("Rukja...Tera gaana dhund raha hu...")

    try:
        # Search for the track
        title, artists, duration, link = search_spotify_track(query)
        if not title:
            await message.reply_text("No results found.")
            return

        # Download the track
        audio_file, title, duration = await download_spotify_audio(link)
        if not audio_file:
            await message.reply_text("❌ Error downloading from Spotify")
            return

        # Play the audio in voice chat
        if chat_id in QUEUE:
            queue_num = add_to_queue(chat_id, title[:19], duration, audio_file, link)
            await message.reply_text(f"# {queue_num}\n{title[:19]}\nTera gaana queue me daal diya hu")
            return

        Status, Text = await userbot.playAudio(chat_id, audio_file)
        if Status == False:
            await message.reply_text(Text)
        else:
            add_to_queue(chat_id, title[:19], duration, audio_file, link)
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await message.reply_text(
                f"Tera gaana play kar rha hu aaja vc\n\nSongName:- [{title[:19]}]({link})\nDuration:- {duration // 60}:{duration % 60:02d} mins\nTime taken to play:- {total_time_taken}",
                disable_web_page_preview=True,
            )
    except Exception as e:
        await message.reply_text(f"Error: {e}")
