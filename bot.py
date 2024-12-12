import discord

#setting up the client class

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} ! \n I am alive!!')

    async def on_message(self,message):
        if message.author == self.user:
            return
        if "avatar" in message.content:
            await message.channel.send(message.author.avatar)
        if 'jule' in str(message.content).lower():
            print(f"Called by {message.author} for : {message.content}")


    async def on_member_join(self, member):
        greet = member.guild.get_channel(1316443021981515817)
        role = member.guild.get_role(1316483824854634586)
        await member.add_roles(role)
        await greet.send(f"Welcome to this simple side of world {member.name}")
        
        try:
            await greet.send(member.avatar)
        except:
            await greet.send(self.user.avatar)
        finally:
            await greet.send("Please note that this server is still under construction so watch your head")




# Set up bot prefix and intents
intents = discord.Intents.default()             # Default intents
intents.message_content = True                         # Enable message intents if needed
intents.members = True

# Run the bot
TOKEN = "MTMxNjQwNjg3NzU5MjIyMzc1NQ.Gk5c2F.mKf8K8kLrpkUHfMl_39DoIsbLnYoLe4lyKYB3g"
client = Client(intents = intents)
client.run(TOKEN)

