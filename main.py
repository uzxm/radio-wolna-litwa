import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp
import time
import os

# Instalacja FFmpeg (na hostingach Linux jak Railway)
os.system("apt-get update && apt-get install -y ffmpeg")

TOKEN = os.getenv("TOKEN")  # Discord bot token z Railway

# Lista utworów YouTube
YOUTUBE_LINKI = [
    "https://youtu.be/T_NKi5KHUdI?si=O_mGQvqF5QE-NHKx",
    "https://www.youtube.com/watch?v=DWcJFNfaw9c",
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()
broadcast_start = None
current_title = None

# Opcje yt-dlp i FFmpeg
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'noplaylist': True
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_music(vc):
    global current_title
    index = 0
    while True:
        url = YOUTUBE_LINKI[index % len(YOUTUBE_LINKI)]
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                current_title = info['title']

            vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
            while vc.is_playing():
                await asyncio.sleep(1)
        except Exception as e:
            print(f"⚠️ no: {url} | ror: {e}")
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

@bot.tree.command(name="ping", description="i broke leg playing pongpi g")
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
    embed.add_field(name="Now playing", value=f"**{current_title or 'not playing'}**", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="deploy", description="starts the yap on a channel")
@app_commands.describe(kanal="channel where yap")
async def deploy(interaction: discord.Interaction, kanal: discord.VoiceChannel):
    global broadcast_start
    try:
        if interaction.user.guild_permissions.connect:
            # Pierwsza odpowiedź
            await interaction.response.send_message(
                f"🎵 connecting to **{kanal.name}** and starting the broadcast.."
            )
            vc = await kanal.connect()
            broadcast_start = time.time()
            await play_music(vc)
        else:
            await interaction.response.send_message(
                "❌ no.", ephemeral=True
            )
    except Exception as e:
        # używamy followup jeśli interaction został już "responded"
        await interaction.followup.send(f"❌ followip: {e}", ephemeral=True)

bot.run(TOKEN)
