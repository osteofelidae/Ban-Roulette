# TODO console logging, leaderboard command, profile command

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
ERROR_FILE_NAME = "dump.json"



# VARIABLES

# User data
user_data = {"user_stats":{},
             "bans":{}}
user_data_default = {"user_stats":{"example_user":{"points": 0,
                                                   "banned_minutes": 0}},
                     "bans": {"example_user":{"(server_id)":{"(UNIX date)"}}}
                     }

# Discord bot object
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)



# FUNCTIONS

# Console print
def console_print(msgType: str, msgText: str):

    # Print
    print(f"[{msgType.upper()}] {msgText}")

# Import savefile
def import_savefile(file_name: str,
                    error_file_name = "dump.json"):

    # TODO: console print in this function

    # Temp var
    temp_dict = {}

    # Try open file
    try:

        # Open file
        file_object = open(file_name, "r")

    # If file not found
    except FileNotFoundError:

        # Create file
        file_object = open(file_name, "w")

        # Write brackets to file
        file_object.write(str(user_data_default))

        # Open file for read
        file_object.close()
        file_object = open(file_name, "r")

    # Try import from file
    try:

        # Import dict from file
        temp_dict = json.loads(file_object.read())

    # If formatting is incorrect
    except json.decoder.JSONDecodeError:

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

    # Open file for write
    file_object = open(file_name, "w")

    # Try dumping data
    try:

        # Dump to file
        json.dump(dict_in, file_object)

    # On error
    except:

        # Return error
        console_print("error", "Critical error writing to savefile.")

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

    # See if dict entry exists
    try:

        # Access required stuff
        user_data["user_stats"][str(user_id)]
        user_data["bans"][str(user_id)]

    except:

        # Initialize profile
        user_data["user_stats"][str(user_id)] = {"points": 0,
                                            "banned_minutes": 0}
        user_data["bans"][str(user_id)] = {}

    # Increment user points
    user_data["user_stats"][str(user_id)]["points"] += minutes * chance

    # If user is banned:
    if banned:

        # Increment minutes
        user_data["user_stats"][str(user_id)]["banned_minutes"] += minutes

        # Calculate ban end time
        ban_end_time = datetime.datetime.now() + datetime.timedelta(0, minutes * 60)

        # Add to time
        user_data["bans"][str(user_id)][str(server_id)] = str(ban_end_time)

    # Save
    export_savefile(SAVEFILE_NAME, user_data)

# Process ban response
async def process_ban_response(ctx,
                         user_name: str,
                         minutes: int,
                         chance: int,
                         banned: bool):

    # Set variables
    if banned:

        # Set embed fields
        embed_title = "L" # TODO random laugh
        embed_description = f"LOL {user_name} got banned"
        # TODO color

    # If not banned:
    else:

        # Set embed fields
        embed_title = "WOW"  # TODO random exclamation
        embed_description = f"LOL {user_name} dodged the ban!"
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
        embed_title = "L"  # TODO random laugh
        embed_description = f"LOL you got banned from {ctx.guild.name}\nClick the title of this embed to rejoin when the ban expires"
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



# Process ban action
async def process_ban_action(user: discord.Member,
                       banned: bool):

    # If user is banned
    if banned:

        # Try
        try:

            # Ban user
            await user.ban()

        # if failed
        except discord.errors.Forbidden:

            console_print("error", f"Could not ban {user.name}. Insufficient permissions.")

# Process unbans
async def process_unbans(): # TODO exception handling

    # Globals
    global user_data

    # Loop forever
    while True:

    # Try
        try:

            # Iterate through user in bans dictionary
            for user_id in user_data["bans"]:

                # TODO temp
                print(user_id)

                # Server ids to remove
                remove_ids = []

                # Iterate through servers user is banned in
                for server_id in user_data["bans"][str(user_id)]:

                    # Formulate date
                    ban_date = (datetime.datetime.strptime(user_data["bans"][str(user_id)][str(server_id)], "%Y-%m-%d %H:%M:%S.%f"))

                    # TODO temp
                    print(str(ban_date) + "    " + str(datetime.datetime.now()))
                    print(ban_date < datetime.datetime.now())

                    # If date is passed
                    if ban_date < datetime.datetime.now():

                        # TODo temp
                        print("YES")

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

                            pass

                        # Add to remove queue
                        remove_ids.append(server_id)

                        print(remove_ids)

                # Iterate through ids to remove
                for server_id in remove_ids:

                    # Remove dict entry
                    user_data["bans"][str(user_id)].pop(str(server_id))

                    # Save file
                    export_savefile(SAVEFILE_NAME, user_data)


        except:

            pass

        # Wait
        await asyncio.sleep(1)




# BOT EVENTS
@bot.event
async def on_ready():

    # Globals
    global user_data

    # Import user data
    user_data = import_savefile(SAVEFILE_NAME, error_file_name=ERROR_FILE_NAME)

    # Print
    console_print("info", "Bot is ready")



# SLASH COMMANDS

# Wager command
@bot.slash_command(description="Gamble your life away.")
async def wager(ctx: discord.ApplicationContext,
                minutes: int = 15,
                chance: int = 1):

    # If either var is out of range
    if minutes <= 0 or chance <= 0 or chance >= 6:

        # Check if minutes and chance are in range
        error_embed = discord.Embed(title="U fucked up") # TODO random fuckup text, color

        # If minutes out of range
        if minutes <= 0:

            # Add field
            error_embed.add_field(name="Minutes",
                                  value="You need to wager at least 1 minute, idiot") # TODO random insult

        # If chance out of range
        if chance <= 0 or chance >= 6:

            # Add field
            error_embed.add_field(name="Chance",
                                  value="Chance needs to be between 1 and 5, idiot")  # TODO random insult

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



# REGISTER EVENTS

bot.loop.create_task(process_unbans())



# RUN BOT

bot.run(BOT_TOKEN)