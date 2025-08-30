import discord
from discord import app_commands
from pcs_utils.rider_utils import *
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import io

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
GUILD_ID = 709429944354341007  # replace with your server ID

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = MyClient()

# birthdate command
@client.tree.command(
    name="birthdate",
    description="Get the birthdate of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def birthdate(interaction: discord.Interaction, name: str):
    rider_birthdate = get_rider_birthdate(name)
    if rider_birthdate is None:
        await interaction.response.send_message(f"No birthdate found for '{name}'")
    else:
        await interaction.response.send_message(f"The birthdate of **{name}** is {rider_birthdate}")

# place of birth command
@client.tree.command(
    name="place-of-birth",
    description="Get the place of birth of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def place_of_birth(interaction: discord.Interaction, name: str):
    rider_place_of_birth = get_rider_place_of_birth(name)
    if rider_place_of_birth is None:
        await interaction.response.send_message(f"No birth place found for '{name}'")
    else:
        await interaction.response.send_message(f"**{name}** was born in {rider_place_of_birth}")

# weight command
@client.tree.command(
    name="weight",
    description="Get the weight of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def weight(interaction: discord.Interaction, name: str):
    rider_weight = get_rider_weight(name)
    if rider_weight is None:
        await interaction.response.send_message(f"No weight found for '{name}'")
    else:
        await interaction.response.send_message(f"**{name}** weighs {rider_weight} kg")

# height command
@client.tree.command(
    name="height",
    description="Get the height of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def height(interaction: discord.Interaction, name: str):
    rider_height = get_rider_height(name)
    if rider_height is None:
        await interaction.response.send_message(f"No height found for '{name}'")
    else:
        await interaction.response.send_message(f"**{name}** is {rider_height} m tall")

# nationality command
@client.tree.command(
    name="nationality",
    description="Get the nationality of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def nationality(interaction: discord.Interaction, name: str):
    rider_nationality = get_rider_nationality(name)
    if rider_nationality is None:
        await interaction.response.send_message(f"No nationality found for '{name}'")
    else:
        await interaction.response.send_message(f"**{name}**'s nationality is {rider_nationality}")

# rider image command
@client.tree.command(
    name="rider-image",
    description="Get the image of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def rider_image_command(interaction: discord.Interaction, name: str):
    image_url = get_rider_image_url(name)

    if image_url is None:
        await interaction.response.send_message(f"No image found for '{name}'")
    else:
        # Create an embed
        embed = discord.Embed(
            title=f"{name} — Rider Image",
            color=(255 << 16) + (255 << 8) + 255
        )
        # Set the image
        embed.set_image(url=image_url)

        # Optionally, add a footer or description
        embed.set_footer(text="Image from ProCyclingStats")

        await interaction.response.send_message(embed=embed)

# team history command
@client.tree.command(
    name="team-history",
    description="Get the team history of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def team_history_command(interaction: discord.Interaction, name: str):
    team_history_list = get_rider_team_history(name)  # list of dicts
    if not team_history_list:
        await interaction.response.send_message(f"No team history found for '{name}'")
        return

    # Create an embed
    embed = discord.Embed(
        title=f"{name} — Team History",
        color=(255 << 16) + (255 << 8) + 255
    )

    # Add each season as a field
    for entry in team_history_list:
        season = entry.get('season', '')
        team_name = entry.get('team_name', '')
        team_class = entry.get('class', '')
        since = entry.get('since', '')
        until = entry.get('until', '')

        # Format the value nicely
        period = f"{since} → {until}" if since and until else "-"
        embed.add_field(
            name=f"{season} - {team_name} ({team_class})",
            value=period,
            inline=False
        )

    # Send the embed
    await interaction.response.send_message(embed=embed)

# points per season command
@client.tree.command(
    name="points-per-season",
    description="Get the PCS points scored per season of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def points_per_season_command(interaction: discord.Interaction, name: str):
    try:
        points_per_season_history = get_rider_points_per_season_history(name)
        if not points_per_season_history:
            await interaction.response.send_message(f"No points history found for '{name}'")
            return

        image_buffer = plot_points_table_style(points_per_season_history, rider_name=name)
        file = discord.File(fp=image_buffer, filename="points.png")
        embed = discord.Embed(
            title=f"{name} — PCS Points per Season",
            color=(255 << 16) + (255 << 8) + 255
        )
        embed.set_image(url="attachment://points.png")
        await interaction.response.send_message(embed=embed, file=file)

    except Exception as e:
        print(f"Error in points_per_season_command for {name}: {e}")
        await interaction.response.send_message("An unexpected error occurred while fetching points per season.")

# points per speciality command
@client.tree.command(
    name="points-per-speciality",
    description="Get the PCS points per speciality of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def points_per_speciality_command(interaction: discord.Interaction, name: str):
    try:
        points_data = get_rider_points_per_speciality(name)
        if not points_data:
            await interaction.response.send_message(f"No points per speciality found for '{name}'")
            return

        image_buffer = plot_points_per_speciality_table(points_data, rider_name=name)
        file = discord.File(fp=image_buffer, filename="speciality_points.png")
        embed = discord.Embed(
            title=f"{name} — PCS Points per Speciality",
            color=(255 << 16) + (255 << 8) + 255
        )
        embed.set_image(url="attachment://speciality_points.png")
        await interaction.response.send_message(embed=embed, file=file)

    except Exception as e:
        print(f"Error in points_per_speciality_command for {name}: {e}")
        await interaction.response.send_message("An unexpected error occurred while fetching points per speciality.")

# season result command
@client.tree.command(
    name="season-results",
    description="Get season results of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def season_results_cmd(interaction: discord.Interaction, name: str):
    results = get_season_results(name)
    embeds = format_season_results_embeds(results, name)

    # Send first embed as initial response
    await interaction.response.send_message(embed=embeds[0])

    # Send the rest as followups
    for embed in embeds[1:]:
        await interaction.followup.send(embed=embed)

client.run(token)
