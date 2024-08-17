from YMusic import app
from YMusic.core import userbot
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS

from pyrogram import filters

import asyncio
import random
import time
import spotdl
import config

PLAY_COMMAND = ["P", "PLAY"]

PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

async def download_spotify_audio(link):
    temp_file = f"temp{random.randint(1, 10000)}.mp3"
    spotdl_args = ["spotdl", "--output", temp_file, link]

    process = await asyncio.create_subprocess_exec(
        *spotdl_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        return None, None, None

    # Assuming SpotDL fetched details from Spotify successfully
    info = {
        "title": "Unknown Title",  # SpotDL doesn't provide title easily in its API
        "duration": "Unknown Duration",  # SpotDL doesn't provide duration directly
        "file": temp_file
    }

    return info["file"], info["title"], info["duration"]

async def processReplyToMessage(message):
    msg = message.reply_to_message
    if msg.audio or msg.voice:
        m = await message.reply_text("Rukja...Tera Audio Download kar raha hu...")
        audio_original = await msg.download()
        input_filename = audio_original
        return input_filename, m
    return None

@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    if (message.reply_to_message) is not None:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            input_filename, m = await processReplyToMessage(message)
            if input_filename is None:
                await message.reply_text(
                    "Audio pe reply kon karega mai? ya phir song link kon dalega mai? 🤔"
                )
                return
            await m.edit("Rukja...Tera Audio Play karne vala hu...")
            Status, Text = await userbot.playAudio(chat_id, input_filename)
            if Status == False:
                await m.edit(Text)
            else:
                if chat_id in QUEUE:
                    queue_num = add_to_queue(
                        chat_id,
                        message.reply_to_message.audio.title[:19],
                        message.reply_to_message.audio.duration,
                        message.reply_to_message.audio.file_id,
                        message.reply_to_message.link,
                    )
                    await m.edit(
                        f"# {queue_num}\n{message.reply_to_message.audio.title[:19]}\nTera gaana queue me daal diya hu"
                    )
                    return
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Tera gaana play kar rha hu aaja vc\n\nSongName:- [{message.reply_to_message.audio.title[:19]}]({message.reply_to_message.link})\nDuration:- {message.reply_to_message.audio.duration}\nTime taken to play:- {total_time_taken}",
                    disable_web_page_preview=True,
                )
    elif (len(message.command)) < 2:
        await message.reply_text("Song name kon dalega mai? 🤔")
    else:
        m = await message.reply_text("Rukja...Tera gaana dhund raha hu...")
        query = message.text.split(maxsplit=1)[1]
        try:
            audio_file, title, duration = await download_spotify_audio(query)
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")
            return

        if not audio_file:
            await m.edit(f"❌ Error downloading from Spotify")
        else:
            if chat_id in QUEUE:
                queue_num = add_to_queue(chat_id, title[:19], duration, audio_file, query)
                await m.edit(
                    f"# {queue_num}\n{title[:19]}\nTera gaana queue me daal diya hu"
                )
                return

            Status, Text = await userbot.playAudio(chat_id, audio_file)
            if Status == False:
                await m.edit(Text)
            else:
                add_to_queue(chat_id, title[:19], duration, audio_file, query)
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Tera gaana play kar rha hu aaja vc\n\nSongName:- [{title[:19]}]({query})\nDuration:- {duration}\nTime taken to play:- {total_time_taken}",
                    disable_web_page_preview=True,
                )

@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & SUDOERS)
async def _raPlay(_, message):
    start_time = time.time()
    if (message.reply_to_message) is not None:
        await message.reply_text("Currently this is not supported")
    elif (len(message.command)) < 3:
        await message.reply_text("You Forgot To Pass An Argument")
    else:
        m = await message.reply_text("Searching Your Query...")
        query = message.text.split(" ", 2)[2]
        msg_id = message.text.split(" ", 2)[1]
        try:
            audio_file, title, duration = await download_spotify_audio(query)
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")
            return
        
        if not audio_file:
            await m.edit(f"❌ Error downloading from Spotify")
        else:
            Status, Text = await userbot.playAudio(msg_id, audio_file)
            if Status == False:
                await m.edit(Text)
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit(
                f"Tera gaana play kar rha hu aaja vc\n\nSongName:- [{title[:19]}]({query})\nDuration:- {duration}\nTime taken to play:- {total_time_taken}",
                disable_web_page_preview=True,
            )
