import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class UnbanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='unban', description="Odbanuj użytkownika")
    @app_commands.describe(user_id='ID użytkownika, którego chcesz odbanować', reason='Powód odbanowania')
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "Nie podano powodu"):
        print(f'Komenda unban wywołana przez {interaction.user} dla użytkownika {user_id} z powodem: {reason}')
        
        try:
            # Sprawdzenie, czy użytkownik wywołujący komendę ma odpowiednie uprawnienia
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("Nie masz uprawnień do odbanowywania użytkowników.", ephemeral=True)
                return

            user = await self.bot.fetch_user(user_id)
            if user is None:
                await interaction.response.send_message("Nie znaleziono użytkownika o podanym ID.", ephemeral=True)
                return

            await interaction.guild.unban(user, reason=reason)
            await interaction.response.send_message(f"Użytkownik {user.mention} został odbanowany. Powód: {reason}")

            # Zapisz log do pliku
            self.log_unban(interaction.user, user, reason)

        except discord.NotFound:
            await interaction.response.send_message("Nie znaleziono użytkownika o podanym ID w banach.", ephemeral=True)
        except Exception as e:
            print(f'Błąd podczas wykonywania komendy unban: {e}')
            await interaction.response.send_message("Wystąpił błąd podczas wykonywania komendy.", ephemeral=True)

    def log_unban(self, moderator, user, reason):
        with open("bans.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Moderator unban: {moderator} ({moderator.id}), User: {user} ({user.id}), Reason: {reason}\n")

async def setup(bot):
    await bot.add_cog(UnbanCommand(bot))
