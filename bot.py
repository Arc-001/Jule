import discord

import google.generativeai as gemini


gemini.configure(api_key="AIzaSyBShrIVy_UqwUpWZeIiMirTY5sGSs9HbgI")
model = gemini.GenerativeModel("gemini-1.5-flash")

r = {
    "18-20": 123456789012345678,  # Replace with actual role IDs
    "21-25": 234567890123456789,
    "25-30":
    "30-35":
    ">35":
    "he/him": 234567890123456789,
    "she/her": 234567890123456789,
    "they/them": 234567890123456789
    "work":
    "college":
    # Add more roles as needed
}

def get_str(prompt):
    response = model.generate_content(prompt)
    buffer = []
    
    for chunk in response:
        for part in chunk.parts:
            buffer.append(part.text)
        gemReply = str(''.join(buffer))
    
    return gemReply

def get_roles(intro):
    prompt = "Make a list roles in the following range  of valid roles",str(list(r.keys())),' You must only respond with a python like formated list of valid roles ONLY based on the given introduction :',intro)
    reply = get_str(prompt)
    role = []
    try:
        reply = list(reply)
        for i in reply:
            role.append(r[i.lower().strip()])
    except:
        return role


#setting up the client class

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} ! \n I am alive!!')

    async def on_message(self,message):

        #Prevents self referential loop
        if message.author == self.user:
            return
        
        
        #All Universal on messages

        #Command to get avatar if user demands
        if "avatar" in message.content:
            await message.channel.send(message.author.avatar)
        
        '''
        if 'jule' in str(message.content).lower():
            print(f"Called by {message.author} for : {message.content}")
        '''

        #All Introduction based commands
        if message.channel.id == 1316681600808915016:



    async def on_member_join(self, member):
        #setting up the greet channel
        greet = member.guild.get_channel(1316443021981515817)

        #sending greer message
        await greet.send(f"Welcome to this simple side of world {member.name}")
        try:
            await greet.send(member.avatar)
        except:
            await greet.send(self.user.avatar)
        finally:
            await greet.send("Please note that this server is still under construction so watch your head")


        #setting up the roles to be given on default
        role = member.guild.get_role(1316483824854634586)

        #assigning role
        await member.add_roles(role)





# Set up bot prefix and intents
intents = discord.Intents.default()             # Default intents
intents.message_content = True                         # Enable message intents if needed
intents.members = True

# Run the bot
TOKEN = "MTMxNjQwNjg3NzU5MjIyMzc1NQ.Gk5c2F.mKf8K8kLrpkUHfMl_39DoIsbLnYoLe4lyKYB3g"
client = Client(intents = intents)
client.run(TOKEN)


