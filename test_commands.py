#!/usr/bin/env python3
"""
Test script to check if slash commands are being registered properly
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.tree.command(name="test", description="Test command")
async def test_command(interaction: discord.Interaction):
    """Test command"""
    await interaction.response.send_message("✅ Test command works!", ephemeral=True)

@bot.tree.command(name="test2", description="Test command 2")
async def test_command2(interaction: discord.Interaction):
    """Test command 2"""
    await interaction.response.send_message("✅ Test command 2 works!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    
    # List commands before sync
    commands = bot.tree.get_commands()
    print(f'Found {len(commands)} commands before sync:')
    for cmd in commands:
        print(f'  - {cmd.name}: {cmd.description}')
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
        for cmd in synced:
            print(f'  - Synced: {cmd.name}')
    except Exception as e:
        print(f'Error syncing commands: {e}')

if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("No DISCORD_BOT_TOKEN found in environment")
        exit(1)
    
    bot.run(token)