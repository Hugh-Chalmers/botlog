import discord
import datetime
import asyncio
import os
import pytz

token = "NzkyODk4NTg1NTUyNjE3NDgz.GlcoXL.Uoynu4W1ugOdNlHuIkKG-sy4a-XiP7fZlnmr1I"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Define the time zone for the UK
uk_timezone = pytz.timezone('Europe/London')

# Define the transition times between BST and GMT
bst_to_gmt_transition = datetime.datetime(2024, 10, 27, 2, 0, 0, tzinfo=pytz.utc)
gmt_to_bst_transition = datetime.datetime(2025, 3, 30, 1, 0, 0, tzinfo=pytz.utc)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    channel = str(message.channel.id)
    log_channel = client.get_channel(1242883124392628319)
    botcmd_channel = client.get_channel(1242891038423650324)

    if msg == "!ping":
        await message.channel.send("Pong!")

    elif msg == "!help":
        help_message = (
            "Here are the available commands:\n"
            "!ping - Responds with 'Pong!'\n"
            "!help - Shows this help message\n"
            "!download M1 - Downloads the M1 log\n"
            "!download M15 - Downloads the M15 log\n"
            "!download M30 - Downloads the M30 log\n"
            "!fetch_messages <channel_id> [filename] - Fetches all messages from the specified channel and saves them to a file with the specified name (defaults to channel_id_messages.txt)\n"
        )
        await message.channel.send(help_message)

    now = datetime.datetime.now(uk_timezone)

    # Adjust for BST/GMT transition
    if now >= bst_to_gmt_transition and now < gmt_to_bst_transition:
        now -= datetime.timedelta(hours=1)

    current_time = str(now.strftime("%Y-%m-%d %H:%M"))

    if channel == "1242153468790050856":  # M15
        tofile = current_time + " : " + str(msg) + "\n"
        with open("M15_log.txt", "a") as f:
            f.write(tofile)
        await log_channel.send(f"[{current_time}] M15 Candle Logged")

    elif channel == "1242257146503106704":  # M1
        tofile = current_time + " : " + str(msg) + "\n"
        with open("M1_log.txt", "a") as f:
            f.write(tofile)
        await log_channel.send(f"[{current_time}] M1 Candle Logged")

    elif channel == "1242288710007914539":  # M30
        tofile = current_time + " : " + str(msg) + "\n"
        with open("M30_log.txt", "a") as f:
            f.write(tofile)
        await log_channel.send(f"[{current_time}] M30 Candle Logged")

    elif channel == "1242891038423650324":  # Bot Commands
        if str(msg) == "!download M1":
            with open("M1_log.txt", "rb") as f:
                await botcmd_channel.send(file=discord.File(f))
        if str(msg) == "!download M15":
            with open("M15_log.txt", "rb") as f:
                await botcmd_channel.send(file=discord.File(f))
        if str(msg) == "!download M30":
            with open("M30_log.txt", "rb") as f:
                await botcmd_channel.send(file=discord.File(f))
        if str(msg).startswith("!fetch_messages"):
            parts = msg.split()
            if len(parts) < 2 or len(parts) > 3:
                await botcmd_channel.send("Usage: !fetch_messages <channel_id> [filename]")
                return

            channel_id = int(parts[1])
            target_channel = client.get_channel(channel_id)
            if not target_channel:
                await botcmd_channel.send(f"Channel with ID {channel_id} not found.")
                return

            filename = f"{channel_id}_messages.txt"
            if len(parts) == 3:
                filename = parts[2]

            # Ensure directory exists
            os.makedirs("./Log_Files", exist_ok=True)

            # Append ".txt" extension if not provided
            if not filename.endswith(".txt"):
                filename += ".txt"

            # Construct file path
            file_path = os.path.join("./Log_Files", filename)

            messages = []
            async for msg in target_channel.history(limit=None):
                message_time = msg.created_at.replace(tzinfo=pytz.utc).astimezone(uk_timezone)
                # Subtract one hour
                message_time -= datetime.timedelta(hours=1)
                formatted_time = message_time.strftime("%Y-%m-%d %H:%M")
                messages.append(f'{formatted_time} : {msg.content}\n')

            # Reverse the list of messages to ensure latest messages are appended at the bottom
            messages.reverse()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(messages)

            await botcmd_channel.send(f"Messages from channel {channel_id} have been written to {file_path}")
            with open(file_path, 'rb') as file:
                await botcmd_channel.send(file=discord.File(file))

client.run(token)
