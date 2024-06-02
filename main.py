import discord
from discord.ext import commands
import os
import importlib
import asyncio
import pymysql
from datetime import datetime

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'HELLNAH',
    'database': 'HELLNAH'
}

log_file_path = 'main.logs'

def log_to_file(message):
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{datetime.now()} - {message}\n')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)
required_role_id = '1242549323372167308'

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Tylu wycieków to ja na oczy nie widziałem zamówcie hydraulika bo się z was leje"))
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

async def load_commands():
    print("Loading commands...")
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'commands')):
        if filename.endswith('.py'):
            command_name = filename[:-3]  # Usuń rozszerzenie .py
            print(f'Command: {command_name}')
            try:
                extension = f'commands.{command_name}'
                await bot.load_extension(extension)
                print(f'Successfully loaded extension: {extension}')
            except Exception as e:
                print(f'Failed to load extension {extension}: {e}')
    print("Commands loaded.")

@bot.command(name='update')
@commands.is_owner()
async def update(ctx):
    log_to_file(f'Command update invoked by {ctx.author}')
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'commands')):
        if filename.endswith('.py'):
            try:
                extension = f'commands.{filename[:-3]}'
                await bot.unload_extension(extension)
                importlib.reload(importlib.import_module(extension))
                await bot.load_extension(extension)
                await ctx.send(f'Pomyślnie zaktualizowano {extension}!')
            except Exception as e:
                await ctx.send(f'Błąd przy aktualizacji rozszerzenia {extension}: {e}')

@bot.command(name='stop')
@commands.is_owner()  
async def reset(ctx):
    log_to_file(f'Command stop invoked by {ctx.author}')
    await ctx.send("Wyłączanie bota...")
    await bot.close()

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        role_id = 1064074137355681834
        if any(role.id == role_id for role in message.author.roles):
            response_embed = discord.Embed(color=0x00FFFF)
            response_embed.add_field(name='\u200b', value="Hej kochanie!", inline=False)
        else:
            response_embed = discord.Embed(color=0x00FFFF)
            combined_value = f"Na chuj mnie idioto oznaczasz?"
            response_embed.add_field(name='\u200b', value=combined_value, inline=False)
        await message.channel.send(embed=response_embed)
    await bot.process_commands(message)



async def main():
    async with bot:
        await load_commands()
        await bot.start('HELLNAH')

if __name__ == '__main__':
    asyncio.run(main())
