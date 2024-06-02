import discord
from discord.ext import commands
from discord import app_commands
import pymysql
import os
from datetime import datetime

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'HELLNAH',
    'database': 'HELLNAH'
}

required_role_id = 1242549323372167308  # ID roli, która ma mieć dostęp do komendy

def find_player(name):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT name, ip, source_file FROM players WHERE name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

class FindCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(app_commands.Command(
            name='find',
            description="Wyszukaj swojego przeciwnika!",
            callback=self.find
        ))

    async def find(self, interaction: discord.Interaction, name: str):
        # Dodaj logi do debugowania
        print(f"Received find command from user {interaction.user} with name {name}")
        log_to_file(f"Received find command from user {interaction.user} with name {name}")
        
        # Sprawdzenie ról użytkownika
        role_names = [role.name for role in interaction.user.roles if role.name != "@everyone"]
        print(f"User roles: {role_names}")
        log_to_file(f"User roles: {role_names}")
        
        if required_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Brak uprawnień", 
                description="Nie masz odpowiedniej roli, aby użyć tej komendy.", 
                color=0xff0000
            ))
            return

        # Wyszukiwanie w bazie danych
        results = find_player(name)
        print(f"Database results: {results}")
        log_to_file(f"Database results: {results}")
        
        if results:
            embed = discord.Embed(title="", color=0x1f1f1f)
            for result in results:
                player_name, ip, source_file = result
                source_file_name = os.path.splitext(source_file)[0]  # Usuń rozszerzenie .txt
                embed.add_field(name="***Nazwa***", value=f'**{player_name}**', inline=True)
                embed.add_field(name="***IP***", value=f'**{ip}**', inline=True)
                embed.add_field(name="***Wyciek***", value=f'**{source_file_name}**', inline=True)

            embed.set_image(url="https://i.imgur.com/ONAXW8w.gif")  # Bezpośredni link do obrazka

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=discord.Embed(
                title="O Jebany Nie Ma Go", 
                color=0xff0000
            ))

        log_to_file(f"Command find executed by {interaction.user} for name {name}")

async def setup(bot):
    await bot.add_cog(FindCommand(bot))

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="?", intents=intents)

def log_to_file(message):
    log_file_path = 'main.logs'
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{datetime.now()} - {message}\n')
