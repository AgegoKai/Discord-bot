import discord
from discord.ext import commands
from discord import app_commands
import datetime

log_file_path = 'main.logs'

def log_to_file(message):
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{datetime.datetime.now()} - {message}\n')

class RoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='role', description="Nadaj lub odbierz rolę użytkownikowi")
    @app_commands.describe(action='Działanie, które chcesz wykonać (nadaj/zabierz)', member='Użytkownik, któremu chcesz nadać/zabrać rolę', role='Rola, którą chcesz nadać/zabrać')
    async def role(self, interaction: discord.Interaction, action: str, member: discord.Member, role: discord.Role):
        # Sprawdzenie, czy użytkownik wywołujący komendę jest właścicielem bota
        is_owner = await self.bot.is_owner(interaction.user)
        
        # Sprawdzenie, czy rola nie jest wyższa niż najwyższa rola użytkownika wywołującego komendę (z wyjątkiem właściciela bota)
        if not is_owner and role.position >= interaction.user.top_role.position:
            await interaction.response.send_message("Nie możesz zarządzać rolą, która jest wyższa lub równa Twojej najwyższej roli.", ephemeral=True)
            return

        # Sprawdzenie, czy bot ma uprawnienia do zarządzania tą rola
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message("Nie mogę zarządzać tą rolą, ponieważ jest wyższa niż moja najwyższa rola.", ephemeral=True)
            return

        if action.lower() == 'nadaj':
            await member.add_roles(role)
            await interaction.response.send_message(f"Nadano rolę {role.name} użytkownikowi {member.mention}.")
            log_to_file(f'{interaction.user} nadał rolę {role.name} użytkownikowi {member}.')
        elif action.lower() == 'zabierz':
            await member.remove_roles(role)
            await interaction.response.send_message(f"Zabrano rolę {role.name} użytkownikowi {member.mention}.")
            log_to_file(f'{interaction.user} zabrał rolę {role.name} użytkownikowi {member}.')
        else:
            await interaction.response.send_message("Nieznane działanie. Użyj 'nadaj' lub 'zabierz'.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleCommand(bot))
