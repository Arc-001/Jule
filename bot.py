import discord
import google.generativeai as gemini
from collections import deque
import subprocess
import json

gemini.configure(api_key="ENTER YOUR API KEY")
model = gemini.GenerativeModel("gemini-2.0-flash-exp")

# Role mapping name(str) -> role id(int)
#example role mapping with role to role id maping

#TODO make a simple class and input for this
r = {
    "18-20": 1316707496974618644,
    "21-25": 1316707726780534795,
    "25-30": 1316707851363684354,
    "30-35": 1316707965990080522,
    ">35": 1316708075603759114,
    "he/him": 1316708175860338708,
    "she/her": 1316708329208156191,
    "they/them": 234567890123456789,
    "work": 1316708586344284211,
    "college": 1316708465602990100
    # Add more roles as needed
}

#location of server and its config files
SERVER_DIRECTORY = "/home/mcserver/minecraft_bedrock"
SERVER_PROPERTIES = f"{SERVER_DIRECTORY}/server.properties"


def edit_server_properties(settings):
    # Update server.properties file based on the provided settings
    try:
        with open(SERVER_PROPERTIES, "r") as file:
            lines = file.readlines()

        updated_lines = []
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                if key in settings:
                    updated_lines.append(f"{key}={settings[key]}\n")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add new keys if they do not exist
        for key, value in settings.items():
            if f"{key}=" not in "".join(lines):
                updated_lines.append(f"{key}={value}\n")

        with open(SERVER_PROPERTIES, "w") as file:
            file.writelines(updated_lines)
        return True
    except Exception as e:
        print(f"Failed to edit server.properties: {e}")
        return False

def restart_server():
    try:
        subprocess.run(["systemctl", "restart", "minecraft-bedrock.service"], check=True)
        print("Server restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart server: {e}")

def get_str(prompt):
    response = model.generate_content(prompt)
    buffer = []

    for chunk in response:
        for part in chunk.parts:
            buffer.append(part.text)
        gemReply = str(''.join(buffer))

    return gemReply

def get_roles(intro):
    prompt = (
        "From the following list of valid roles: " + str(list(r.keys())) + ", "
        "identify the roles mentioned in the given introduction text strictly. "
        "Ensure you respond with a Python-formatted list containing only valid role names. "
        "Do not include any other text or explanation. Introduction: " + str(intro)
    )
    reply = get_str(prompt)
    print(reply)
    role = []
    try:
        reply = eval(reply)
        print(reply)
        for i in reply:
            role.append(r[i.lower().strip()])
    except:
        return role

    return role


# Setting up the client class

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_context = {}  # To store user-specific contexts

    async def on_ready(self):
        print(f'Logged in as {self.user} ! \n I am alive!!')

    async def on_message(self, message):

        # Prevents self referential loop
        if message.author == self.user:
            return

        # All Universal on messages

        # Command to get avatar if user demands
        if "avatar" in message.content:
            await message.channel.send(message.author.avatar)

        if message.content.lower().startswith("hey jule"):
            user_id = message.author.id

            # Initialize or update context
            if user_id not in self.user_context:
                self.user_context[user_id] = deque(maxlen=1000)

            self.user_context[user_id].append(message.content)
            context = "\n".join(list(self.user_context[user_id]))

            # Dynamic personality
            tone = "friendly and helpful"
            if "formal" in message.content.lower():
                tone = "formal and professional"
            elif "funny" in message.content.lower():
                tone = "humorous and lighthearted"

            prompt = (
                f"You are Jule, a {tone} assistant. "
                f"Here is the ongoing context of your interaction with {message.author.display_name}: \n{context}\n"
                f"Respond to the latest query: {message.content}. "
                "Provide a response that aligns with the tone."
            )
            reply = get_str(prompt)
            await message.channel.send(reply)

        '''
        if 'jule' in str(message.content).lower():
            print(f"Called by {message.author} for : {message.content}")
        '''

        # All Introduction based commands
        if message.channel.id == 1316681600808915016:
            print('triggered 1')
            if message.content.startswith("!intro"):
                print('triggered 2')
                intro_role_lst = get_roles(message.content)
                print(intro_role_lst)
                for role_id in intro_role_lst:
                    role = discord.utils.get(message.guild.roles, id=role_id)
                    if role:
                        await message.author.add_roles(role)
        
        if message.channel.id == 1316478464294912010:
            if any(role.id == 1316955480702320670 for role in message.author.roles):
                prompt = (
                    f"Extract the desired Minecraft Bedrock server settings changes from this message:\n\n"
                    f"Message: {message.content}\n\n"
                    "Respond with a python dictionary which can be directly evaled to a dictionary with no text formatting only the dictionary where keys are property names and values are the desired settings."
                )
                response = get_str(prompt).split('\n')
                print(response[1])
                try:
                            # Extract JSON content from the respons
                    settings = eval(response[1])
                    for i in settings:
                        settings[i] = str(settings[i]).lower()
                    print(settings)
                    if (len(settings) == 0):
                        await message.channel.send("Invalid setting")
                    if isinstance(settings, dict):
                        success = edit_server_properties(settings)
                        if success:
                            await message.channel.send("Settings updated. Restarting the server...")
                            restart_server()
                        else:
                            await message.channel.send("Failed to update settings. Please check the logs.")
                    else:
                        await message.channel.send("Unable to parse settings. Please rephrase your request.")
                except json.JSONDecodeError as e:
                    await message.channel.send(f"Error processing request: Invalid JSON format. {e}")
                except Exception as e:
                    await message.channel.send(f"Error processing request: {e}")

    '''
    async def on_member_join(self, member):
        # Setting up the greet channel
        greet = member.guild.get_channel(1316443021981515817)

        # Sending greet message
        await greet.send(f"Welcome to this simple side of world {member.name}")
        try:
            await greet.send(member.avatar)
        except:
            await greet.send(self.user.avatar)
        finally:
            await greet.send("Please note that this server is still under construction so watch your head")


        # Setting up the roles to be given on default
        role = member.guild.get_role(1316483824854634586)

        # Assigning role
        await member.add_roles(role)
    '''
    
    async def on_member_join(self, member):
        # Setting up the greet channel
        greet = member.guild.get_channel(1316443021981515817)

        # Sending aesthetic greet message
        embed = discord.Embed(
            title="🌟 Welcome to Our Community! 🌟",
            description=(
                f"Hello, {member.name}! We're thrilled to have you join us.\n\n"
                "Explore the channels, make new connections, and enjoy your stay!"
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else self.user.avatar.url)
        embed.set_footer(text="Feel free to ask questions or introduce yourself!")

        await greet.send(embed=embed)

        # Setting up the roles to be given on default
        role = member.guild.get_role(1316483824854634586)

        # Assigning role
        await member.add_roles(role)



# Set up bot prefix and intents
intents = discord.Intents.default()         # Default intents
intents.message_content = True              # Enable message intents if needed
intents.members = True

# Run the bot
TOKEN = ""
client = Client(intents = intents)
client.run(TOKEN)

