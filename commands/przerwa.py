import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta, datetime
import aiohttp

class PrzerwaCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='przerwa', description="Nałóż przerwę (timeout) na użytkownika")
    async def przerwa(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "Nie podano powodu"):
        print(f'Komenda przerwa wywołana przez {interaction.user} dla użytkownika {member} na {duration} minut z powodem: {reason}')
        
        try:
            # Sprawdzenie, czy użytkownik wywołujący komendę ma odpowiednie uprawnienia
            if not interaction.user.guild_permissions.moderate_members:
                await interaction.response.send_message("Nie masz uprawnień do nakładania przerwy.", ephemeral=True)
                return

            # Sprawdzenie, czy użytkownik wywołujący komendę może nałożyć przerwę na danego użytkownika (jego najwyższa rola musi być wyższa niż rola użytkownika, którego chce nałożyć przerwę)
            if member.top_role.position >= interaction.user.top_role.position:
                await interaction.response.send_message("Nie możesz nałożyć przerwy na użytkownika z wyższą lub równą rangą.", ephemeral=True)
                return

            # Sprawdzenie, czy bot ma uprawnienia do nakładania przerwy na użytkownika
            if member.top_role.position >= interaction.guild.me.top_role.position:
                await interaction.response.send_message("Nie mogę nałożyć przerwy na tego użytkownika, ponieważ jego rola jest wyższa niż moja najwyższa rola.", ephemeral=True)
                return

            # Nałóż przerwę na użytkownika za pomocą bezpośredniego zapytania API
            timeout_duration = timedelta(minutes=duration)
            timeout_until = (datetime.utcnow() + timeout_duration).isoformat()
            headers = {
                "Authorization": f"Bot {interaction.client.http.token}",
                "Content-Type": "application/json"
            }
            payload = {
                "communication_disabled_until": timeout_until,
                "reason": reason
            }

            async with aiohttp.ClientSession() as session:
                async with session.patch(f"https://discord.com/api/v9/guilds/{interaction.guild.id}/members/{member.id}", json=payload, headers=headers) as response:
                    if response.status == 200:
                        await interaction.response.send_message(f"Użytkownik {member.mention} został wyciszony na {duration} minut. Powód: {reason}")
                        # Zapisz log do pliku
                        self.log_timeout(interaction.user, member, duration, reason)
                    else:
                        await interaction.response.send_message("Wystąpił błąd podczas nakładania przerwy.", ephemeral=True)
                        print(f'Błąd API: {response.status} - {await response.text()}')

        except Exception as e:
            print(f'Błąd podczas wykonywania komendy przerwa: {e}')
            await interaction.response.send_message("Wystąpił błąd podczas wykonywania komendy.", ephemeral=True)

    def log_timeout(self, moderator, member, duration, reason):
        with open("przerwa.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Moderator: {moderator} ({moderator.id}), User: {member} ({member.id}), Duration: {duration} minutes, Reason: {reason}\n")

async def setup(bot):
    await bot.add_cog(PrzerwaCommand(bot))
