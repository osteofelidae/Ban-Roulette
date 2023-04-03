# TODO finish about command

# DEPENDENCIES

import discord
import json
import random
import datetime
import asyncio



# CONSTANTS

# Bot token
BOT_TOKEN = open("token.config").read()

# Savefile name
SAVEFILE_NAME = "data.json"
LANGUAGEFILE_NAME = "lang.json"
ERROR_FILE_NAME = "dump.json"
LOG_FILE_NAME = "log.log"



# VARIABLES

# User data
user_data = {"user_stats":{},
             "bans":{}}
user_data_default = {"user_stats":{"example_user":{"points": 0,
                                                   "banned_minutes": 0}},
                     "bans": {"example_user":{"(server_id)":{"(UNIX date)"}}}
                     }
language_dict = {}
bot_ready = False

# Logging file
log_queue = []

# Discord bot object
intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)



# FUNCTIONS

# Console print
def console_print(msgType: str, msgText: str):

    # Globals
    global log_queue

    # Save to file
    log_queue.append(f"[{str(datetime.datetime.now())}][{msgType.upper()}] {msgText}\n")

    # Print
    print(f"[{str(datetime.datetime.now())}][{msgType.upper()}] {msgText}")

# Import savefile
def import_savefile(file_name: str,
                    error_file_name = "dump.json"):

    # Console print
    console_print("info", f"Attempting to open {file_name}")

    # Temp var
    temp_dict = {}

    # Try open file
    try:

        # Open file
        file_object = open(file_name, "r")

        # Console print
        console_print("success", f"Opened {file_name}")

    # If file not found
    except FileNotFoundError:

        # Console print
        console_print("error", f"Could not find file {file_name}, attempting to make a new file")

        # Create file
        file_object = open(file_name, "w")

        # Write brackets to file
        file_object.write(str(user_data_default))

        # Open file for read
        file_object.close()
        file_object = open(file_name, "r")

        # Console print
        console_print("success", f"Created file {file_name}")

    # Try import from file
    try:

        # Console print
        console_print("info", f"Attempting to import dict from {file_name}")

        # Import dict from file
        temp_dict = json.loads(file_object.read())

        # Console print
        console_print("success", f"Imported dict from {file_name}")

    # If formatting is incorrect
    except json.decoder.JSONDecodeError:

        # Console print
        console_print("error", f"Could not parse json in {file_name}")

        # TODO Dump data to error file
        error_file_object = open(error_file_name, "w")
        error_file_object.write(file_object.read())
        error_file_object.close()

        # Initialize save file
        file_object.close()
        file_object = open(file_name, "w")
        file_object.write("{}")
        file_object.close()

    # Return resulting dict
    return temp_dict

# Export savefile
def export_savefile(file_name: str,
                    dict_in: dict):

    # Console print
    console_print("info", f"Attempting to save dict to {file_name}")

    # Open file for write
    file_object = open(file_name, "w")

    # Try dumping data
    try:

        # Dump to file
        json.dump(dict_in, file_object)

        # Console print
        console_print("success", f"Saved dict to {file_name}")

    # On error
    except:

        # Return error
        console_print("error", "Error writing to savefile.")

    # Close file
    file_object.close()

# Increment points
async def process_ban_data(server_id: int,
                     user_id: int,
                     minutes: int,
                     chance: int,
                     banned: bool):

    # Globals
    global user_data

    # Console print
    console_print("info", f"Processing ban data for user {user_id} in server {server_id}")

    # See if dict entry exists
    try:

        # Access required stuff
        user_data["user_stats"][str(user_id)]
        user_data["bans"][str(user_id)]

    except:

        # Console print
        console_print("info", f"User entry not found, intializing profile for {user_id}")

        # Initialize profile
        user_data["user_stats"][str(user_id)] = {"points": 0,
                                            "banned_minutes": 0}
        user_data["bans"][str(user_id)] = {}

        # Console print
        console_print("success", f"Initialized profile for {user_id}")

    # Increment user points
    user_data["user_stats"][str(user_id)]["points"] += minutes * chance

    # Make sure it is int
    user_data["user_stats"][str(user_id)]["banned_minutes"] = int(user_data["user_stats"][str(user_id)]["banned_minutes"])

    # If user is banned:
    if banned:

        # Increment minutes
        user_data["user_stats"][str(user_id)]["banned_minutes"] += minutes

        # Calculate ban end time
        ban_end_time = datetime.datetime.now() + datetime.timedelta(0, minutes * 60)

        # Add to time
        user_data["bans"][str(user_id)][str(server_id)] = str(ban_end_time)

    # Console print
    console_print("success", f"Added ban data for {user_id} in {server_id}")

# Process ban response
async def process_ban_response(ctx,
                         user_name: str,
                         minutes: int,
                         chance: int,
                         banned: bool):

    # Set variables
    if banned:

        # Set embed fields
        embed_title = get_random(language_dict, "laugh")
        embed_description = f"{get_random(language_dict, 'laugh')} {user_name} got banned"
        # TODO color

    # If not banned:
    else:

        # Set embed fields
        embed_title = get_random(language_dict, "exclaim")
        embed_description = f"{get_random(language_dict, 'laugh')} {user_name} dodged the ban!"
        # TODO color

    # Create embed
    response_embed = discord.Embed(title=embed_title,
                                   description=embed_description)

    # Add fields
    response_embed.add_field(name="Points",
                             value=f"{minutes * chance} points gained")
    response_embed.add_field(name="Duration",
                             value=f"{minutes} minutes")

    # Respond
    await ctx.respond(embed=response_embed)

    # Create embed and send dm if banned
    if banned:

        # Set embed fields
        embed_title = get_random(language_dict, 'laugh')
        embed_description = f"{get_random(language_dict, 'laugh')} you got banned from {ctx.guild.name}\nClick the title of this embed to rejoin when the ban expires"
        # TODO color

        # Edit embed description
        response_embed = discord.Embed(title=embed_title,
                                       description=embed_description,
                                       url=str(await ctx.guild.text_channels[0].create_invite(max_age=minutes * 60 + (60 * 60))))

        # Add fields
        response_embed.add_field(name="Points",
                                 value=f"{minutes * chance} points gained")
        response_embed.add_field(name="Duration",
                                 value=f"{minutes} minutes")

        # Send embed
        await ctx.user.send(embed=response_embed)

# Function to get random thing from lang
def get_random(dict_in: dict,
               field: str):

    # Return random choice from field
    return random.choice(dict_in[field])

# Process ban action
async def process_ban_action(user: discord.Member,
                       banned: bool): # TODO this might ban globally?

    # Console print
    console_print("info", f"Attempting to ban {user.id}")

    # If user is banned
    if banned:

        # Try
        try:

            # Ban user
            await user.ban(reason="Ban roulette")

            # Console print
            console_print("success", f"Banned {user.id}")

        # if failed
        except discord.errors.Forbidden:

            console_print("error", f"Could not ban {user.name}. Insufficient permissions.")

# Process unbans
async def process_unbans():

    # Globals
    global user_data



    # Loop forever
    while True:

        # Console print
        console_print("info", f"Processing unbans")

        # Try
        try:

            # Iterate through user in bans dictionary
            for user_id in user_data["bans"]:

                # Server ids to remove
                remove_ids = []

                # Iterate through servers user is banned in
                for server_id in user_data["bans"][str(user_id)]:

                    # Formulate date
                    ban_date = (datetime.datetime.strptime(user_data["bans"][str(user_id)][str(server_id)], "%Y-%m-%d %H:%M:%S.%f"))

                    # If date is passed
                    if ban_date < datetime.datetime.now():

                        # Get server
                        server = bot.get_guild(int(server_id))

                        # Try
                        try:

                            # Get user
                            user = await bot.fetch_user(int(user_id))

                            # Unban
                            await server.unban(user)

                            print("x")

                        except:

                            # Console print
                            console_print("error", f"Error unbanning user {user_id} in {server_id}")

                        # Add to remove queue
                        remove_ids.append(server_id)

                        print(remove_ids)

                # Iterate through ids to remove
                for server_id in remove_ids:

                    # Remove dict entry
                    user_data["bans"][str(user_id)].pop(str(server_id))

        except:

            pass

        # Console print
        console_print("success", f"Processed unbans")

        # Wait
        await asyncio.sleep(5)

# Save file wrapper for scheduling
async def save_file():

    # Wait
    await asyncio.sleep(11)

    # Loop
    while True and bot_ready:

        # Save
        export_savefile(SAVEFILE_NAME, user_data)

        # Wait
        await asyncio.sleep(5)

# Save to logging file
async def save_log():

    # Wait
    await asyncio.sleep(3)

    # Repeat forever
    while True:

        # Try
        try:

            # If there are items in list:
            queue_length = len(log_queue)
            if queue_length != 0:

                # Repeat for everything in queue
                for index in range(queue_length):

                    # Open file
                    log_file = open(LOG_FILE_NAME, "a")

                    # Write to file
                    log_file.write(log_queue.pop())

                    # Close file
                    log_file.close()

            # Wait

        except:

            pass

        await asyncio.sleep(5)



# BOT EVENTS
@bot.event
async def on_ready():

    # Globals
    global user_data, bot_ready, language_dict

    # Import user data
    user_data = import_savefile(SAVEFILE_NAME, error_file_name=ERROR_FILE_NAME)
    language_dict = import_savefile(LANGUAGEFILE_NAME)

    # Set bot is ready
    bot_ready = True

    # Print
    console_print("info", "Bot is ready")



# SLASH COMMANDS

# Wager command
@bot.slash_command(description="Gamble your life away.")
async def wager(ctx: discord.ApplicationContext,
                minutes: int = 15,
                chance: int = 1):

    # Console print
    console_print("info", f"")

    # If either var is out of range
    if minutes <= 0 or chance <= 0 or chance >= 6:

        # Check if minutes and chance are in range
        error_embed = discord.Embed(title=f"{get_random(language_dict, 'laugh')} u fucked up") #TODO color

        # If minutes out of range
        if minutes <= 0:

            # Add field
            error_embed.add_field(name="Minutes",
                                  value=f"You need to wager at least 1 minute, {get_random(language_dict, 'insult')}")

        # If chance out of range
        if chance <= 0 or chance >= 6:

            # Add field
            error_embed.add_field(name="Chance",
                                  value=f"Chance needs to be between 1 and 5, {get_random(language_dict, 'insult')}")

        # Respond with embed
        await ctx.respond(embed=error_embed)

        # Exit function
        return

    # Calculate points
    points_total = minutes * chance

    # Roll a number
    rolled_number = random.randint(1, 6)

    # If chosen number is within rolled number
    if chance >= rolled_number:

        # Mark user to be banned
        banned = True

    # If not
    else:

        # Mark user to not be banned
        banned = False

    # Process save data
    await process_ban_data(ctx.guild.id, ctx.author.id, minutes, chance, banned)

    # Process ban response
    await process_ban_response(ctx, ctx.author.name, minutes, chance, banned)

    # Process ban action
    await process_ban_action(ctx.author, banned)

# Leaderboard command
@bot.slash_command(description="Who is good and who is not?")
async def leaderboard(ctx: discord.ApplicationContext): # TODO page number

    # Get server
    server = ctx.guild

    # Temp dict
    leaderboard_dict = {}

    # Iterate through users in server
    for user in server.members:

        # If user is registered
        if str(user.id) in user_data["user_stats"]:

            # Add to temp dict
            leaderboard_dict[str(user.id)] = int(user_data["user_stats"][str(user.id)]["points"])

    # Sort dict
    leaderboard_dict = dict(sorted(leaderboard_dict.items(), key=lambda item: 1/item[1]))

    # Create embed
    leaderboard_embed = discord.Embed(title="Leaderboard")

    # Generate text
    rankings = ""
    usernames = ""
    points = ""
    for index in range(min(10, len(leaderboard_dict))):

        rankings += f"{str(index+1)}\n"
        usernames += f"{server.get_member(int(list(leaderboard_dict.keys())[index])).name}\n"
        points += f"{int(list(leaderboard_dict.values())[index])}\n"

    # Add embed fields
    leaderboard_embed.add_field(name="Rank",
                                value=rankings,
                                inline=True)
    leaderboard_embed.add_field(name="User",
                                value=usernames,
                                inline=True)
    leaderboard_embed.add_field(name="Points",
                                value=points,
                                inline=True)

    # Respond
    await ctx.respond(embed=leaderboard_embed)

# Profile command
@bot.slash_command(description="How bad are you?")
async def profile(ctx:discord.ApplicationContext):

    # Get server
    server = ctx.guild

    # Temp dict
    leaderboard_dict = {}

    # Iterate through users in server
    for user in server.members:

        # If user is registered
        if str(user.id) in user_data["user_stats"]:
            # Add to temp dict
            leaderboard_dict[str(user.id)] = int(user_data["user_stats"][str(user.id)]["points"])

    # Try
    try:

        # Sort dict
        leaderboard_dict = dict(sorted(leaderboard_dict.items(), key=lambda item: 1 / item[1]))

        # Get ranking
        ranking = str((list(leaderboard_dict.keys()).index(str(ctx.author.id)))+1)

        # Get minutes banned
        minutes_banned = user_data["user_stats"][str(ctx.author.id)]["banned_minutes"]

        # Get points
        points = int(user_data["user_stats"][str(ctx.author.id)]["points"])

        # Create embed
        profile_embed = discord.Embed(title="Profile")

        # Add embed fields
        profile_embed.add_field(name="Name",
                                value=ctx.author.name,
                                inline=False)
        profile_embed.add_field(name="Server ranking",
                                value=ranking,
                                inline=False)
        profile_embed.add_field(name="Points",
                                value=points,
                                inline=False)
        profile_embed.add_field(name="Minutes banned",
                                value=minutes_banned,
                                inline=False)

    except:

        # Create embed
        profile_embed = discord.Embed(title="Profile",
                                      description=f"You don't seem to have played before, {get_random(language_dict, 'insult')}!")



    # Respond
    await ctx.respond(embed=profile_embed)

# About command
@bot.slash_command(description="Stalk me")
async def about(ctx: discord.ApplicationContext):

    # Create embed
    about_embed = discord.Embed(title="About Ban Roulette")

    # Add embed fields
    about_embed.add_field(name="Author",
                          value="Authored by osteofelidae:\nhttps://osteofelidae.github.io/",
                          inline=False)
    about_embed.add_field(name="Help",
                          value="[IF YOU SEE THIS THE DEV IS LAZY AND HASNT ADDED A LINK HERE YET]",  # TODO this
                          inline=False)
    about_embed.add_field(name="Vote",
                          value="[IF YOU SEE THIS THE DEV IS LAZY AND HASNT ADDED A LINK HERE YET]", # TODO this
                          inline=False)
    about_embed.add_field(name="Donate",
                          value="I made this bot for fun and host it for free. If you would like to support me, please visit\nhttps://www.buymeacoffee.com/osteofelidae",
                          inline=False)

    # Respond
    await ctx.respond(embed=about_embed)



# REGISTER EVENTS

bot.loop.create_task(process_unbans())
bot.loop.create_task(save_file())
bot.loop.create_task(save_log())



# RUN BOT

bot.run(BOT_TOKEN)