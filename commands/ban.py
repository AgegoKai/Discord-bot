import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class BanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ban', description="Zbanuj użytkownika")
    @app_commands.describe(member='Użytkownik, którego chcesz zbanować', reason='Powód zbanowania')
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Nie podano powodu"):
        print(f'Komenda ban wywołana przez {interaction.user} dla użytkownika {member} z powodem: {reason}')
        
        try:

            # Sprawdzenie, czy użytkownik wywołujący komendę ma odpowiednie uprawnienia
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("Nie masz uprawnień do banowania użytkowników.", ephemeral=True)
                return

            # Sprawdzenie, czy użytkownik wywołujący komendę może zbanować danego użytkownika (jego najwyższa rola musi być wyższa niż rola użytkownika, którego chce zbanować)
            if member.top_role.position >= interaction.user.top_role.position:
                await interaction.response.send_message("Nie możesz zbanować użytkownika z wyższą lub równą rangą.", ephemeral=True)
                return

            # Sprawdzenie, czy bot ma uprawnienia do banowania użytkownika
            if member.top_role.position >= interaction.guild.me.top_role.position:
                await interaction.response.send_message("Nie mogę zbanować tego użytkownika, ponieważ jego rola jest wyższa niż moja najwyższa rola.", ephemeral=True)
                return

            await member.ban(reason=reason)
            await interaction.response.send_message(f"Użytkownik {member.mention} został zbanowany. Powód: {reason}")

            # Zapisz log do pliku
            self.log_ban(interaction.user, member, reason)

        except Exception as e:
            print(f'Błąd podczas wykonywania komendy ban: {e}')
            await interaction.response.send_message("Wystąpił błąd podczas wykonywania komendy.", ephemeral=True)

    def log_ban(self, moderator, member, reason):
        with open("bans.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Moderator ban: {moderator} ({moderator.id}), User: {member} ({member.id}), Reason: {reason}\n")

async def setup(bot):
    await bot.add_cog(BanCommand(bot))
