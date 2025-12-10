"""
AI-powered commands cog for Jule bot
Handles Gemini LLM interactions, Wikipedia searches, and intelligent responses
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio
import aiohttp

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import GEMINI_API_KEY
import google.generativeai as genai


class AICommands(commands.Cog):
    """AI-powered commands using Gemini LLM and Wikipedia"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Configure Gemini API
        if not GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not found. AI commands will be limited.")
            self.model = None
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Wikipedia API endpoint
        self.wikipedia_api = "https://en.wikipedia.org/w/api.php"

        # Conversation history per user (for context)
        self.conversation_history = {}

    async def get_gemini_response(self, prompt: str, user_id: int = None, use_history: bool = False) -> str:
        """Get a response from Gemini with optional conversation history"""
        if not self.model:
            return "❌ AI service is not available. Please configure GEMINI_API_KEY."

        try:
            if use_history and user_id:
                # Get conversation history
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                # Add user message to history
                self.conversation_history[user_id].append({
                    "role": "user",
                    "parts": [prompt]
                })

                # Keep only last 10 messages to avoid token limits
                if len(self.conversation_history[user_id]) > 10:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-10:]

                # Create chat with history
                chat = self.model.start_chat(history=self.conversation_history[user_id][:-1])
                response = await asyncio.to_thread(chat.send_message, prompt)

                # Add assistant response to history
                self.conversation_history[user_id].append({
                    "role": "model",
                    "parts": [response.text]
                })
            else:
                # Single message without history
                response = await asyncio.to_thread(self.model.generate_content, prompt)

            return response.text if response else "I couldn't generate a response."

        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return f"❌ Error: {str(e)}"

    async def search_wikipedia(self, query: str, sentences: int = 3) -> dict:
        """Search Wikipedia and return a summary"""
        try:
            # Wikipedia requires a User-Agent header
            headers = {
                "User-Agent": "JuleBot/1.0 (Discord Bot; Python/aiohttp)"
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                # Search for the page
                search_params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": query,
                    "utf8": 1
                }

                async with session.get(self.wikipedia_api, params=search_params) as resp:
                    search_data = await resp.json()

                    if not search_data.get("query", {}).get("search"):
                        return {"error": "No results found"}

                    # Get the first result
                    page_title = search_data["query"]["search"][0]["title"]
                    page_id = search_data["query"]["search"][0]["pageid"]

                # Get page summary
                summary_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts|pageimages",
                    "exintro": 1,
                    "explaintext": 1,
                    "exsentences": sentences,
                    "pageids": page_id,
                    "piprop": "original"
                }

                async with session.get(self.wikipedia_api, params=summary_params) as resp:
                    summary_data = await resp.json()
                    page_data = summary_data["query"]["pages"][str(page_id)]

                    return {
                        "title": page_data.get("title", page_title),
                        "extract": page_data.get("extract", "No summary available."),
                        "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                        "image": page_data.get("original", {}).get("source")
                    }

        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return {"error": str(e)}

    @commands.command(name="explain", aliases=["eli5"], help="Ask the AI to explain something! Usage: !explain <topic>")
    async def explain(self, ctx: commands.Context, *, topic: str):
        """Explain a topic in simple terms using Gemini"""
        if not topic:
            await ctx.send("❌ Please provide a topic to explain!")
            return

        async with ctx.typing():
            prompt = f"""Explain the following topic in a clear, concise way that's easy to understand. 
Use simple language and provide practical examples if relevant. Keep it under 500 words.

Topic: {topic}

Explanation:"""

            response = await self.get_gemini_response(prompt)

            # Split response if too long for Discord (2000 char limit)
            if len(response) > 1900:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                embed = discord.Embed(
                    title=f"💡 Explaining: {topic}",
                    description=chunks[0],
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)

                for chunk in chunks[1:]:
                    await ctx.send(chunk)
            else:
                embed = discord.Embed(
                    title=f"💡 Explaining: {topic}",
                    description=response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Asked by {ctx.author.display_name}")
                await ctx.send(embed=embed)

    @commands.command(name="wiki", aliases=["wikipedia"], help="Search Wikipedia! Usage: !wiki <query>")
    async def wiki(self, ctx: commands.Context, *, query: str):
        """Search Wikipedia and return a summary"""
        if not query:
            await ctx.send("❌ Please provide a search query!")
            return

        async with ctx.typing():
            result = await self.search_wikipedia(query)

            if "error" in result:
                await ctx.send(f"❌ {result['error']}")
                return

            embed = discord.Embed(
                title=f"📖 {result['title']}",
                description=result['extract'][:2000],  # Limit to 2000 chars
                url=result['url'],
                color=discord.Color.green()
            )

            if result.get('image'):
                embed.set_thumbnail(url=result['image'])

            embed.set_footer(text="Source: Wikipedia")
            await ctx.send(embed=embed)

    @commands.command(name="topicstarter", aliases=["topic", "conversation"], help="Generate conversation starter ideas!")
    async def topicstarter(self, ctx: commands.Context, *, theme: Optional[str] = None):
        """Generate interesting conversation starters"""
        async with ctx.typing():
            if theme:
                prompt = f"""Generate 5 interesting and engaging conversation starters related to: {theme}

Make them thought-provoking, fun, and likely to spark good discussions. Format as a numbered list."""
            else:
                prompt = """Generate 5 interesting and engaging conversation starters on random topics.

Make them thought-provoking, fun, and likely to spark good discussions. Format as a numbered list."""

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title="💬 Conversation Starters" + (f" - {theme}" if theme else ""),
                description=response,
                color=discord.Color.purple()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)

    @commands.command(name="ask", aliases=["ai", "gemini"], help="Ask the AI anything! Usage: !ask <question>")
    async def ask(self, ctx: commands.Context, *, question: str):
        """Ask Gemini AI a question"""
        if not question:
            await ctx.send("❌ Please ask a question!")
            return

        async with ctx.typing():
            prompt = f"""Answer the following question helpfully and accurately. Be conversational but informative.

Question: {question}

Answer:"""

            response = await self.get_gemini_response(prompt, ctx.author.id, use_history=True)

            # Split if too long
            if len(response) > 1900:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                embed = discord.Embed(
                    title="🤖 AI Response",
                    description=chunks[0],
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Asked by {ctx.author.display_name}")
                await ctx.send(embed=embed)

                for chunk in chunks[1:]:
                    await ctx.send(chunk)
            else:
                embed = discord.Embed(
                    title="🤖 AI Response",
                    description=response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Asked by {ctx.author.display_name}")
                await ctx.send(embed=embed)

    @commands.command(name="clearcontext", aliases=["clearhistory"], help="Clear your conversation history with the AI")
    async def clearcontext(self, ctx: commands.Context):
        """Clear conversation history for the user"""
        if ctx.author.id in self.conversation_history:
            del self.conversation_history[ctx.author.id]
            await ctx.send("✅ Your conversation history has been cleared!")
        else:
            await ctx.send("ℹ️ You don't have any conversation history.")

    @commands.command(name="compare", help="Compare two things using AI! Usage: !compare <thing1> vs <thing2>")
    async def compare(self, ctx: commands.Context, *, comparison: str):
        """Compare two things using AI"""
        if " vs " not in comparison.lower() and " versus " not in comparison.lower():
            await ctx.send("❌ Please use format: `!compare <thing1> vs <thing2>`")
            return

        async with ctx.typing():
            prompt = f"""Compare the following two things in a balanced and informative way. 
Highlight key differences, similarities, pros and cons. Keep it under 600 words.

{comparison}

Comparison:"""

            response = await self.get_gemini_response(prompt)

            # Split if too long
            if len(response) > 1900:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                embed = discord.Embed(
                    title=f"⚖️ Comparison",
                    description=chunks[0],
                    color=discord.Color.gold()
                )
                await ctx.send(embed=embed)

                for chunk in chunks[1:]:
                    await ctx.send(chunk)
            else:
                embed = discord.Embed(
                    title=f"⚖️ Comparison",
                    description=response,
                    color=discord.Color.gold()
                )
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                await ctx.send(embed=embed)

    @commands.command(name="summarize", aliases=["tldr"], help="Summarize a topic or concept! Usage: !summarize <topic>")
    async def summarize(self, ctx: commands.Context, *, topic: str):
        """Provide a concise summary of a topic"""
        if not topic:
            await ctx.send("❌ Please provide a topic to summarize!")
            return

        async with ctx.typing():
            prompt = f"""Provide a concise, bullet-point summary of the following topic. 
Focus on the most important and interesting facts. Keep it under 300 words.

Topic: {topic}

Summary:"""

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title=f"📝 Summary: {topic}",
                description=response,
                color=discord.Color.teal()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)

    @commands.command(name="debate", help="Get debate points for a topic! Usage: !debate <topic>")
    async def debate(self, ctx: commands.Context, *, topic: str):
        """Generate debate points (for and against) on a topic"""
        if not topic:
            await ctx.send("❌ Please provide a debate topic!")
            return

        async with ctx.typing():
            prompt = f"""Generate balanced debate points for the following topic:

Topic: {topic}

Provide:
1. 3-5 strong arguments FOR this position
2. 3-5 strong arguments AGAINST this position

Be objective and present both sides fairly. Format clearly with headers.

Debate Points:"""

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title=f"⚔️ Debate: {topic}",
                description=response[:2000],
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name} • For educational purposes")
            await ctx.send(embed=embed)

    @commands.command(name="aifact", aliases=["smartfact"], help="Get an AI-generated interesting fact!")
    async def aifact(self, ctx: commands.Context, *, category: Optional[str] = None):
        """Generate a random interesting fact using AI"""
        async with ctx.typing():
            if category:
                prompt = f"Share one fascinating and verified fact about {category}. Make it interesting and surprising!"
            else:
                prompt = "Share one fascinating and verified fact about any topic. Make it interesting and surprising!"

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title="💡 Interesting Fact",
                description=response,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.command(name="brainstorm", help="Brainstorm ideas! Usage: !brainstorm <topic/problem>")
    async def brainstorm(self, ctx: commands.Context, *, topic: str):
        """Generate creative ideas for a topic or problem"""
        if not topic:
            await ctx.send("❌ Please provide a topic or problem to brainstorm!")
            return

        async with ctx.typing():
            prompt = f"""Help brainstorm creative ideas for the following:

{topic}

Generate 7-10 diverse, creative, and practical ideas. Be innovative and think outside the box.
Format as a numbered list with brief descriptions.

Ideas:"""

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title=f"💡 Brainstorming: {topic[:100]}",
                description=response[:2000],
                color=discord.Color.purple()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)

    @commands.command(name="howto", aliases=["guide"], help="Get a quick guide on how to do something! Usage: !howto <task>")
    async def howto(self, ctx: commands.Context, *, task: str):
        """Generate a step-by-step guide"""
        if not task:
            await ctx.send("❌ Please provide a task!")
            return

        async with ctx.typing():
            prompt = f"""Provide a clear, step-by-step guide on how to:

{task}

Make it practical and easy to follow. Include tips if relevant. Keep it under 500 words.

Guide:"""

            response = await self.get_gemini_response(prompt)

            # Split if too long
            if len(response) > 1900:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                embed = discord.Embed(
                    title=f"📚 How To: {task[:100]}",
                    description=chunks[0],
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)

                for chunk in chunks[1:]:
                    await ctx.send(chunk)
            else:
                embed = discord.Embed(
                    title=f"📚 How To: {task[:100]}",
                    description=response,
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                await ctx.send(embed=embed)

    @commands.command(name="quiz", help="Generate a quiz question! Usage: !quiz [topic]")
    async def quiz(self, ctx: commands.Context, *, topic: Optional[str] = None):
        """Generate a quiz question with multiple choice answers"""
        async with ctx.typing():
            if topic:
                prompt = f"""Create one interesting multiple-choice quiz question about: {topic}

Format:
Question: [question]

A) [option]
B) [option]
C) [option]
D) [option]

Answer: [letter] - [brief explanation]"""
            else:
                prompt = """Create one interesting multiple-choice quiz question about any topic.

Format:
Question: [question]

A) [option]
B) [option]
C) [option]
D) [option]

Answer: [letter] - [brief explanation]"""

            response = await self.get_gemini_response(prompt)

            # Split question and answer
            if "Answer:" in response:
                parts = response.split("Answer:")
                question_part = parts[0].strip()
                answer_part = parts[1].strip() if len(parts) > 1 else "Answer hidden"

                embed = discord.Embed(
                    title="🧩 Quiz Time!",
                    description=question_part,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="React with 🔍 to reveal the answer!")

                msg = await ctx.send(embed=embed)
                await msg.add_reaction("🔍")

                # Wait for reaction to reveal answer
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) == "🔍" and reaction.message.id == msg.id

                try:
                    await self.bot.wait_for('reaction_add', timeout=120.0, check=check)

                    answer_embed = discord.Embed(
                        title="✅ Answer Revealed!",
                        description=answer_part,
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=answer_embed)
                except asyncio.TimeoutError:
                    pass
            else:
                embed = discord.Embed(
                    title="🧩 Quiz Time!",
                    description=response,
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)

    @commands.command(name="dailychallenge", aliases=["challenge"], help="Get a daily challenge or prompt!")
    async def dailychallenge(self, ctx: commands.Context, *, category: Optional[str] = None):
        """Generate a daily challenge or creative prompt"""
        async with ctx.typing():
            if category:
                prompt = f"""Generate one interesting daily challenge or prompt related to: {category}

Make it:
- Achievable within a day
- Engaging and fun
- Clear and specific

Provide the challenge and why it's beneficial.

Challenge:"""
            else:
                prompt = """Generate one interesting daily challenge or prompt.

Make it:
- Achievable within a day
- Engaging and fun
- Clear and specific
- Could be creative, physical, mental, or social

Provide the challenge and why it's beneficial.

Challenge:"""

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title="🎯 Daily Challenge",
                description=response,
                color=discord.Color.magenta()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name} • Good luck!")
            await ctx.send(embed=embed)

    @commands.command(name="translate", help="Translate text! Usage: !translate <language> <text>")
    async def translate(self, ctx: commands.Context, language: str, *, text: str):
        """Translate text to another language"""
        if not language or not text:
            await ctx.send("❌ Usage: `!translate <language> <text>`")
            return

        async with ctx.typing():
            prompt = f"""Translate the following text to {language}. 
If {language} is not a valid language, respond with an error message.
Only provide the translation, nothing else.

Text to translate: {text}

Translation:"""

            response = await self.get_gemini_response(prompt)

            embed = discord.Embed(
                title=f"🌐 Translation to {language.title()}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Original", value=text[:1024], inline=False)
            embed.add_field(name="Translation", value=response[:1024], inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    await bot.add_cog(AICommands(bot))

