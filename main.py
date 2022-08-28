"""Reddit to Discord Mirror

Get your latest reddit updates right in Discord

Also with Imgur archiving to deal with those pesky deleted Reddit posts!

"""
import os
import time
import asyncio
from urllib.parse import urlparse
import asyncpraw
import discord
from discord.ext import tasks
import pyimgur
import aiohttp
import aiofiles
from config import Config
from db import does_post_exist, insert_post_to_db


FILES_PATH = "/tmp/discord_cache/"

if not os.path.exists(FILES_PATH):
    os.mkdir(FILES_PATH)

SUBREDDITS = [
    {"name": "pics", "channel_id": 1011474405368797184},
    {"name": "space", "channel_id": 1011788355237578285},
]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

reddit = asyncpraw.Reddit(
    client_id=Config.PRAW_CLIENT_ID,
    client_secret=Config.PRAW_SECRET_ID,
    user_agent=Config.PRAW_USER_AGENT,
    username=Config.PRAW_USERNAME,
)

im = pyimgur.Imgur(Config.IMGUR_CLIENT_ID)


async def download_file(url) -> None:
    """Download and save file

    This will download a file and save it
    to the FILE_PATH location by filename.

    Args:
        url (str): Full address of file to download
    """
    fname = url.split("/")[-1]
    sema = asyncio.BoundedSemaphore(5)
    async with sema, aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.read()

    async with aiofiles.open(os.path.join(FILES_PATH, fname), "wb") as outfile:
        await outfile.write(data)


async def send_channel_message(submission, channel_id) -> None:
    """Send message to Discord

    Args:
        submission (object): Praw submission object
        channel_id (int): Discord Channel ID Destination
    """
    channel_to_upload_to = client.get_channel(channel_id)
    try:
        embed = discord.Embed(
            title=submission.title,
            url=f"https://reddit.com{submission.permalink}",
            color=0xFF5733,
        )

        embed.set_image(url=submission.url)

        await channel_to_upload_to.send(embed=embed)
    except Exception as error:
        print(f"Message Send failed: {error}")


async def upload_to_imgur(file_name: str, post_title: str) -> object:
    """Upload to Imgur

    Args:
        file_name (str): Name of file to upload
        post_title (str): submission.title from Praw

    Returns:
        object: Imgur Response Object
    """
    imgur_resp = None

    try:
        imgur_resp = im.upload_image(file_name, title=post_title)
    except Exception as error:
        print(f"Failed to upload to Img:{file_name} error:{error}")

    return imgur_resp


async def update_subreddit_posts(subreddit_name: str, channel_id: int) -> None:
    """Process a subreddits posts

    Get all new posts in a subreddit and store
    then to a database if they don't already exist.

    If a submission.url exists on i.redd.it, it is
    mirrored to imgur for safe keeping.

    Args:
        subreddit_name (str): Name of the subreddit
        channel_id (int): Discord Channel Destnation
    """
    subreddit = await reddit.subreddit(subreddit_name)
    count = 0
    bad = 0
    async for submission in subreddit.new():
        if not does_post_exist(submission.id):
            # Check url for images
            if submission.url:

                # Is it an i.reddit.it url
                if urlparse(submission.url).netloc == "i.redd.it":
                    # Download the file, saves it locally as /tmp/{filename}
                    await download_file(submission.url)

                    # Get the url of the mirrored iamge
                    fname = submission.url.split("/")[-1]
                    imgur_response = await upload_to_imgur(
                        f"{FILES_PATH}{fname}", submission.title
                    )

                    # Update object with our new URL
                    submission.url = imgur_response.link

            # Store post to DB
            await insert_post_to_db(submission)

            # Send notification
            await send_channel_message(submission, channel_id)
            count = count + 1
            time.sleep(1)

        else:
            bad = bad + 1

    print(f"Update Complete for {subreddit_name}, new: {count} existing: {bad}")


async def subreddit_main():
    """Subreddit Iterator

    This iterates over each of our Subreddits.

    """
    for subreddit in SUBREDDITS:
        await update_subreddit_posts(subreddit["name"], subreddit["channel_id"])


async def cleanup_files() -> None:
    """Remove temp files

    This is to remove any files we've downloaded
    before pushing them to Imgur.
    """
    for file_name in os.listdir(FILES_PATH):
        try:
            os.remove(os.path.join(FILES_PATH, file_name))
        except Exception as error:
            print(f"Delete File Failed, file:{file_name} error:{error}")


@client.event
async def on_ready() -> None:
    """Start Tasks

    Now that we're connected to Discord, start
    the scheduled tasks.  If we don't wait, the
    firt send will fail.
    """
    print(f"{client.user} has connected to Discord, starting Tasks!")
    scheduled_tasks.start()


@tasks.loop(minutes=1.0)
async def scheduled_tasks() -> None:
    """Task loop to update Reddit posts"""
    await subreddit_main()
    await cleanup_files()


client.run(Config.DISCORD_TOKEN)
