import discord
from discord.ext import commands
from discord import app_commands
import subprocess
import mysql.connector


required_role_id = 1242549323372167308

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '09yPig+l7v}XFFe',
            'database': 'wyciekstore'
        }

    def check_ip_in_database(self, address):
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            query = "SELECT EXISTS(SELECT 1 FROM players WHERE ip = %s)"
            cursor.execute(query, (address,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result[0] == 1
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    @app_commands.command(name='ping', description="Sprawdź czy jego internet działa!")
    @commands.cooldown(1, 60, commands.BucketType.user)  # Cooldown: 1 use per 60 seconds per user
    async def ping(self, interaction: discord.Interaction, address: str):
        print(f"Received ping command for address: {address}")

        if required_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Brak uprawnień", 
                description="Nie masz odpowiedniej roli, aby użyć tej komendy.", 
                color=0xff0000
            ))
            return

        if not self.check_ip_in_database(address):
            print(f"IP address {address} not found in database")
            await interaction.response.send_message(f'Adres IP {address} nie znajduje się w bazie danych.')
            return

        await interaction.response.defer(thinking=True)

        try:
            print(f"Pinging IP address: {address}")
            output = subprocess.run(['ping', '-n', '5', address], capture_output=True, text=True)
            result = output.stdout

            embed = discord.Embed(title=f'Ping results for {address}', description=f'```{result}```', color=discord.Color.blue())
            await interaction.followup.send(embed=embed)
            print(f"Ping results sent for IP address: {address}")
        except Exception as e:
            print(f"Error during ping: {e}")
            await interaction.followup.send(f'Błąd podczas pingowania: {e}')

    @ping.error
    async def ping_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.followup.send(f'Musisz poczekać jeszcze {int(error.retry_after)} sekund przed ponownym użyciem tej komendy.')
        else:
            print(f"Error in ping command: {error}")
            await interaction.followup.send(f'Wystąpił błąd: {error}')

async def setup(bot):
    await bot.add_cog(Ping(bot))
