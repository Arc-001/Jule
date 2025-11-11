"""
Music commands cog for Jule bot
Handles voice channel operations, music playback, queue management, and listening stats
"""

import discord
from discord.ext import commands
from typing import Optional, List
import asyncio
import yt_dlp

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MAX_QUEUE_SIZE, MAX_SEARCH_RESULTS, MUSIC_INACTIVITY_TIMEOUT


# YouTube DL options for audio extraction
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class Song:
    """Represents a song in the queue"""

    def __init__(self, source: dict, requester: discord.Member):
        self.source = source
        self.requester = requester
        self.title = source.get('title', 'Unknown')
        self.url = source.get('url', '')
        self.webpage_url = source.get('webpage_url', '')
        self.duration = source.get('duration', 0)
        self.thumbnail = source.get('thumbnail', '')
        self.uploader = source.get('uploader', 'Unknown')

    def create_embed(self, status: str = "Now Playing") -> discord.Embed:
        """Create an embed for this song"""
        embed = discord.Embed(
            title=status,
            description=f"**[{self.title}]({self.webpage_url})**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Requested by", value=self.requester.mention, inline=True)
        embed.add_field(name="Uploader", value=self.uploader, inline=True)

        if self.duration:
            minutes, seconds = divmod(self.duration, 60)
            embed.add_field(name="Duration", value=f"{minutes}:{seconds:02d}", inline=True)

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)

        return embed


class MusicQueue:
    """Manages the music queue for a guild"""

    def __init__(self, bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.queue: List[Song] = []
        self.current: Optional[Song] = None
        self.loop = False
        self.voice_client: Optional[discord.VoiceClient] = None
        self.inactivity_task = None

    def add_song(self, song: Song):
        """Add a song to the queue"""
        if len(self.queue) >= MAX_QUEUE_SIZE:
            raise ValueError(f"Queue is full! Maximum {MAX_QUEUE_SIZE} songs allowed.")
        self.queue.append(song)

    def get_next(self) -> Optional[Song]:
        """Get the next song from the queue"""
        if self.loop and self.current:
            return self.current

        if self.queue:
            self.current = self.queue.pop(0)
            return self.current

        self.current = None
        return None

    def clear(self):
        """Clear the queue"""
        self.queue.clear()
        self.current = None

    def remove(self, index: int) -> Optional[Song]:
        """Remove a song from the queue by index"""
        if 0 <= index < len(self.queue):
            return self.queue.pop(index)
        return None

    def shuffle(self):
        """Shuffle the queue"""
        import random
        random.shuffle(self.queue)

    def get_queue_embed(self) -> discord.Embed:
        """Create an embed showing the current queue"""
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=discord.Color.blue()
        )

        if self.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{self.current.title}**\nRequested by {self.current.requester.mention}",
                inline=False
            )

        if self.queue:
            queue_text = []
            for i, song in enumerate(self.queue[:10], 1):  # Show first 10
                queue_text.append(f"`{i}.` **{song.title}** - {song.requester.mention}")

            embed.add_field(
                name=f"Up Next ({len(self.queue)} songs)",
                value="\n".join(queue_text),
                inline=False
            )

            if len(self.queue) > 10:
                embed.set_footer(text=f"And {len(self.queue) - 10} more songs...")
        else:
            embed.add_field(name="Queue", value="No songs in queue", inline=False)

        if self.loop:
            embed.add_field(name="Loop", value="✅ Enabled", inline=True)

        return embed


class MusicCommands(commands.Cog):
    """Music playback and queue management commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, MusicQueue] = {}
        self.ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def get_queue(self, guild_id: int) -> MusicQueue:
        """Get or create a queue for a guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue(self.bot, guild_id)
        return self.queues[guild_id]

    async def search_youtube(self, query: str, max_results: int = MAX_SEARCH_RESULTS) -> List[dict]:
        """Search YouTube for songs"""
        try:
            loop = asyncio.get_event_loop()
            # Search for multiple results
            search_query = f"ytsearch{max_results}:{query}"
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(search_query, download=False))

            if 'entries' in data:
                return data['entries']
            return []
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []

    async def get_song_info(self, url_or_query: str) -> Optional[dict]:
        """Get song information from URL or search query"""
        try:
            loop = asyncio.get_event_loop()

            # Check if it's a URL
            if url_or_query.startswith(('http://', 'https://', 'www.')):
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url_or_query, download=False))
            else:
                # Search YouTube
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(f"ytsearch1:{url_or_query}", download=False))

            if 'entries' in data:
                return data['entries'][0]
            return data
        except Exception as e:
            print(f"Error getting song info: {e}")
            return None

    async def play_next(self, guild_id: int, text_channel: discord.TextChannel):
        """Play the next song in the queue"""
        queue = self.get_queue(guild_id)

        if not queue.voice_client or not queue.voice_client.is_connected():
            return

        next_song = queue.get_next()

        if not next_song:
            # Queue is empty, start inactivity timer
            await text_channel.send("⏹️ Queue finished! I'll leave after 5 minutes of inactivity.")
            queue.inactivity_task = asyncio.create_task(self.handle_inactivity(guild_id))
            return

        # Cancel inactivity timer if active
        if queue.inactivity_task:
            queue.inactivity_task.cancel()
            queue.inactivity_task = None

        # Get audio source
        try:
            audio_source = discord.FFmpegPCMAudio(next_song.url, **FFMPEG_OPTIONS)
            
            def after_playing(error):
                if error:
                    print(f"Player error: {error}")
                # Play next song
                coro = self.play_next(guild_id, text_channel)
                asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

            queue.voice_client.play(audio_source, after=after_playing)

            # Send now playing embed
            embed = next_song.create_embed("🎵 Now Playing")
            await text_channel.send(embed=embed)

            # Log to database
            if hasattr(self.bot, 'music_service'):
                self.bot.music_service.log_play(
                    user_id=next_song.requester.id,
                    song_title=next_song.title,
                    song_url=next_song.webpage_url,
                    artist=next_song.uploader,
                    duration=next_song.duration,
                    guild_id=guild_id
                )

        except Exception as e:
            await text_channel.send(f"❌ Error playing song: {str(e)}")
            # Try next song
            await self.play_next(guild_id, text_channel)

    async def handle_inactivity(self, guild_id: int):
        """Handle voice client inactivity"""
        await asyncio.sleep(MUSIC_INACTIVITY_TIMEOUT)
        queue = self.get_queue(guild_id)
        if queue.voice_client and queue.voice_client.is_connected():
            await queue.voice_client.disconnect()
            del self.queues[guild_id]

    @commands.command(name="join", help="Make Jule join your voice channel")
    async def join(self, ctx: commands.Context):
        """Join the user's voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel!")
            return

        channel = ctx.author.voice.channel
        queue = self.get_queue(ctx.guild.id)

        if queue.voice_client and queue.voice_client.is_connected():
            if queue.voice_client.channel == channel:
                await ctx.send("✅ I'm already in your channel!")
                return
            await queue.voice_client.move_to(channel)
        else:
            queue.voice_client = await channel.connect()

        await ctx.send(f"🎵 Joined **{channel.name}**!")

    @commands.command(name="leave", aliases=["disconnect", "dc"], help="Make Jule leave the voice channel")
    async def leave(self, ctx: commands.Context):
        """Leave the voice channel"""
        queue = self.get_queue(ctx.guild.id)

        if not queue.voice_client:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        await queue.voice_client.disconnect()
        queue.clear()
        if queue.inactivity_task:
            queue.inactivity_task.cancel()
        del self.queues[ctx.guild.id]

        await ctx.send("👋 Left the voice channel!")

    @commands.command(name="music", aliases=["play", "p"], help="Search and play music! Usage: !music <song name or URL>")
    async def music(self, ctx: commands.Context, *, query: str):
        """Search for music and display results"""
        if not query:
            await ctx.send("❌ Please provide a song name or URL!")
            return

        # Check if user is in voice channel
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to play music!")
            return

        async with ctx.typing():
            # Search for songs
            results = await self.search_youtube(query)

            if not results:
                await ctx.send("❌ No results found!")
                return

            # Create search results embed
            embed = discord.Embed(
                title="🔍 Search Results",
                description=f"Showing top {len(results)} results for: **{query}**",
                color=discord.Color.green()
            )

            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                uploader = result.get('uploader', 'Unknown')
                duration = result.get('duration', 0)

                duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"

                embed.add_field(
                    name=f"{i}. {title[:50]}",
                    value=f"**By:** {uploader}\n**Duration:** {duration_str}",
                    inline=False
                )

            embed.set_footer(text="Reply with a number (1-5) to play, or 'cancel' to cancel")

            await ctx.send(embed=embed)

            # Wait for user response
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)

                if msg.content.lower() == 'cancel':
                    await ctx.send("❌ Cancelled!")
                    return

                try:
                    choice = int(msg.content)
                    if 1 <= choice <= len(results):
                        selected = results[choice - 1]
                        # Add to queue and play
                        await self.add_to_queue(ctx, selected)
                    else:
                        await ctx.send("❌ Invalid choice!")
                except ValueError:
                    await ctx.send("❌ Please enter a valid number!")

            except asyncio.TimeoutError:
                await ctx.send("⏱️ Search timed out!")

    async def add_to_queue(self, ctx: commands.Context, song_data: dict):
        """Add a song to the queue and start playing if needed"""
        queue = self.get_queue(ctx.guild.id)

        # Join voice channel if not connected
        if not queue.voice_client or not queue.voice_client.is_connected():
            if not ctx.author.voice:
                await ctx.send("❌ You need to be in a voice channel!")
                return
            queue.voice_client = await ctx.author.voice.channel.connect()

        # Create song object
        song = Song(song_data, ctx.author)

        # Add to queue
        try:
            queue.add_song(song)

            embed = discord.Embed(
                title="✅ Added to Queue",
                description=f"**[{song.title}]({song.webpage_url})**",
                color=discord.Color.green()
            )
            embed.add_field(name="Position", value=f"{len(queue.queue)}", inline=True)
            embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)

            if song.thumbnail:
                embed.set_thumbnail(url=song.thumbnail)

            await ctx.send(embed=embed)

            # Start playing if nothing is currently playing
            if not queue.voice_client.is_playing():
                await self.play_next(ctx.guild.id, ctx.channel)

        except ValueError as e:
            await ctx.send(f"❌ {str(e)}")

    @commands.command(name="pause", help="Pause the current song")
    async def pause(self, ctx: commands.Context):
        """Pause playback"""
        queue = self.get_queue(ctx.guild.id)

        if not queue.voice_client or not queue.voice_client.is_playing():
            await ctx.send("❌ Nothing is playing!")
            return

        queue.voice_client.pause()
        await ctx.send("⏸️ Paused!")

    @commands.command(name="resume", help="Resume the paused song")
    async def resume(self, ctx: commands.Context):
        """Resume playback"""
        queue = self.get_queue(ctx.guild.id)

        if not queue.voice_client or not queue.voice_client.is_paused():
            await ctx.send("❌ Nothing is paused!")
            return

        queue.voice_client.resume()
        await ctx.send("▶️ Resumed!")

    @commands.command(name="skip", aliases=["next"], help="Skip the current song")
    async def skip(self, ctx: commands.Context):
        """Skip the current song"""
        queue = self.get_queue(ctx.guild.id)

        if not queue.voice_client or not queue.voice_client.is_playing():
            await ctx.send("❌ Nothing is playing!")
            return

        queue.voice_client.stop()
        await ctx.send("⏭️ Skipped!")

    @commands.command(name="queue", aliases=["q"], help="Show the current music queue")
    async def show_queue(self, ctx: commands.Context):
        """Display the current queue"""
        queue = self.get_queue(ctx.guild.id)
        embed = queue.get_queue_embed()
        await ctx.send(embed=embed)

    @commands.command(name="clearqueue", aliases=["cq"], help="Clear the music queue")
    async def clear_queue(self, ctx: commands.Context):
        """Clear the queue"""
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        await ctx.send("🗑️ Queue cleared!")

    @commands.command(name="loop", help="Toggle loop mode for current song")
    async def loop(self, ctx: commands.Context):
        """Toggle loop mode"""
        queue = self.get_queue(ctx.guild.id)
        queue.loop = not queue.loop

        if queue.loop:
            await ctx.send("🔁 Loop enabled!")
        else:
            await ctx.send("➡️ Loop disabled!")

    @commands.command(name="nowplaying", aliases=["np", "current"], help="Show the currently playing song")
    async def nowplaying(self, ctx: commands.Context):
        """Show currently playing song"""
        queue = self.get_queue(ctx.guild.id)

        if not queue.current:
            await ctx.send("❌ Nothing is playing!")
            return

        embed = queue.current.create_embed("🎵 Now Playing")
        await ctx.send(embed=embed)

    @commands.command(name="shuffle", help="Shuffle the queue")
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the queue"""
        queue = self.get_queue(ctx.guild.id)

        if not queue.queue:
            await ctx.send("❌ Queue is empty!")
            return

        queue.shuffle()
        await ctx.send("🔀 Queue shuffled!")

    @commands.command(name="musicstats", aliases=["ms"], help="Show your music listening statistics")
    async def musicstats(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display user music statistics"""
        target = member if member else ctx.author

        if not hasattr(self.bot, 'music_service'):
            await ctx.send("❌ Music stats are not available!")
            return

        stats = self.bot.music_service.get_user_stats(target.id)

        if not stats or stats['total_songs'] == 0:
            await ctx.send(f"📊 {target.mention} hasn't played any songs yet!")
            return

        # Format listening time
        total_seconds = stats['total_time']
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        embed = discord.Embed(
            title=f"🎵 Music Stats for {target.display_name}",
            color=discord.Color.purple()
        )

        embed.add_field(name="Total Songs Played", value=f"🎵 {stats['total_songs']}", inline=True)
        embed.add_field(name="Total Listening Time", value=f"⏱️ {hours}h {minutes}m", inline=True)

        if stats['favorite_song']:
            embed.add_field(name="Favorite Song", value=f"❤️ {stats['favorite_song']}", inline=False)

        if stats['last_played']:
            embed.add_field(name="Last Played", value=f"🕒 {stats['last_played'].strftime('%Y-%m-%d %H:%M')}", inline=False)

        # Get top songs
        top_songs = self.bot.music_service.get_top_songs(target.id, limit=5)
        if top_songs:
            top_songs_text = []
            for i, song in enumerate(top_songs, 1):
                artist = f" - {song['artist']}" if song['artist'] else ""
                top_songs_text.append(f"`{i}.` **{song['title'][:40]}**{artist} ({song['plays']} plays)")

            embed.add_field(name="Top Songs", value="\n".join(top_songs_text), inline=False)

        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="musicleaderboard", aliases=["mlb"], help="Show the music listening leaderboard")
    async def musicleaderboard(self, ctx: commands.Context):
        """Display music listening leaderboard"""
        if not hasattr(self.bot, 'music_service'):
            await ctx.send("❌ Music leaderboard is not available!")
            return

        leaderboard = self.bot.music_service.get_leaderboard(limit=10)

        if not leaderboard:
            await ctx.send("📊 No music stats yet! Start playing some songs!")
            return

        embed = discord.Embed(
            title="🎵 Music Listening Leaderboard",
            description="Top music listeners in the server!",
            color=discord.Color.gold()
        )

        leaderboard_text = []
        for i, (user_id, total_songs) in enumerate(leaderboard, 1):
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`{i}.`"

            # Get cached user info
            cached_user = self.bot.db.get_user_cache(user_id)
            display_name = cached_user['display_name'] if cached_user else (user.display_name if user else "Unknown")

            leaderboard_text.append(f"{medal} **{display_name}** - {total_songs} songs")

        embed.add_field(name="Rankings", value="\n".join(leaderboard_text), inline=False)
        embed.set_footer(text="Keep listening to climb the ranks!")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    await bot.add_cog(MusicCommands(bot))

