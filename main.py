import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp
import time
import os

# Instalacja FFmpeg (na hostingach Linux)
os.system("apt-get update && apt-get install -y ffmpeg")

TOKEN = os.getenv("TOKEN")  # Discord bot token z Railway

# Lista utworów z YouTube
YOUTUBE_LINKI = [
    "https://youtu.be/dQw4w9WgXcQ?si=ZK1A2AbKNUjngZ-c",
    "https://youtu.be/dQw4w9WgXcQ?si=ZK1A2AbKNUjngZ-c",
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()
broadcast_start = None
current_title = None

# Opcje dla yt-dlp i FFmpeg
YDL_OPTIONS = {'format': 'bestaudio', 'quiet': True}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_music(vc):
    global current_title
    index = 0
    while True:
        url = YOUTUBE_LINKI[index % len(YOUTUBE_LINKI)]
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            current_title = info['title']
        vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        while vc.is_playing():
            await asyncio.sleep(1)
        index += 1
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Zsynchronizowano {len(synced)} komendy slash.")
    except Exception as e:
        print(e)

@bot.tree.command(name="ping", description="check what the bot is playing and some other cool stuff")
async def ping(interaction: discord.Interaction):
    uptime = time.time() - start_time
    broadcast_time = 0 if not broadcast_start else time.time() - broadcast_start

    def fmt(sec):
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        return f"{h}h {m}m {s}s"

    embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
    embed.add_field(name="Bot deployed in", value="**Poland 🇵🇱**", inline=False)
    embed.add_field(name="Uptime", value=f"**{fmt(uptime)}**", inline=False)
    embed.add_field(name="Broadcasting for", value=f"**{fmt(broadcast_time)}**", inline=False)
    embed.add_field(name="Now playing", value=f"**{current_title or 'no song playing silly'}**", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="deploy", description="starts broadcast.")
@app_commands.describe(kanal="channel where broadcast")
async def deploy(interaction: discord.Interaction, kanal: discord.VoiceChannel):
    global broadcast_start
    try:
        if interaction.user.guild_permissions.connect:
            await interaction.response.send_message(
                f"🎵 connected to **{kanal.name}** starting broadcast now."
            )
            vc = await kanal.connect()
            broadcast_start = time.time()
            await play_music(vc)
        else:
            await interaction.response.send_message(
                "❌ you didnt place enough pixels.", ephemeral=True
            )
    except Exception as e:
        await interaction.response.send_message(f"❌ error (i thought i dont do mistakes - uzum): {e}", ephemeral=True)

bot.run(TOKEN)
