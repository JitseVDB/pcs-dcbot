from helpers.country_helper import country_to_emoji
from pcs_scraper.rider_info_scraper import get_rider_age, get_rider_nationality, get_rider_weight, get_rider_height, get_rider_birthdate, get_rider_place_of_birth, get_rider_image_url
from pcs_scraper.season_results_scraper import get_season_results
from discord import app_commands
from constants import MAX_FIELD_LENGTH
from pcs_utils.rider_utils import *
from dotenv import load_dotenv
import os

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

def split_text_preserving_lines(text, max_len=MAX_FIELD_LENGTH):
    """
    Split a text into chunks <= max_len without splitting lines.
    Returns a list of strings.
    """
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks

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

# age command
@client.tree.command(
    name="age",
    description="Get the age of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def birthdate(interaction: discord.Interaction, name: str):
    rider_age = get_rider_age(name)
    if rider_age is None:
        await interaction.response.send_message(f"No age found for '{name}'")
    else:
        await interaction.response.send_message(f"**{name}** is {rider_age} years old")

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
        await interaction.response.send_message(f"**{name}** weighs {rider_weight}")

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
        await interaction.response.send_message(f"**{name}** is {rider_height} tall")

# nationality command
@client.tree.command(
    name="nationality",
    description="Get the nationality of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def nationality(interaction: discord.Interaction, name: str):
    rider_nationality = get_rider_nationality(name)
    flag_nationality = country_to_emoji(rider_nationality)
    if rider_nationality is None:
        await interaction.response.send_message(f"No nationality found for '{name}'")
    else:
        await interaction.response.send_message(f"**{name}**'s nationality is {rider_nationality} {flag_nationality}")

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
            title=f"{name} - Rider Image",
            color=(255 << 16) + (255 << 8) + 255
        )
        # Set the image
        embed.set_image(url=image_url)

        # Add a footer or description
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
        title=f"{name} - Team History",
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
            title=f"{name} - PCS Points per Season",
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

# season results command
@client.tree.command(
    name="season-results",
    description="Get season results of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def season_results_cmd(interaction: discord.Interaction, name: str):
    await interaction.response.defer()  # defer in case scraping takes time

    try:
        races = get_season_results(name)
    except Exception as e:
        await interaction.followup.send(f"Failed to fetch season results for '{name}': {e}")
        return

    if not races:
        await interaction.followup.send(f"No season results found for '{name}'.")
        return

    embeds = []
    current_embed = discord.Embed(
        title=f"{name} - Season Results",
        color=discord.Color.from_rgb(255, 255, 255)
    )

    for race, info in races.items():
        if "stages" in info:  # Stage race
            race_line = f"**{race} {info['flag']}**\n{info['date_range']}"
            stage_lines = []
            classification_lines = []

            # Handle stages
            for stage in reversed(info.get("stages", [])):
                stage_desc = stage.get("description", "")
                stage_line = (
                    f"{stage_desc}\n"
                    f"• {stage['date']} - {stage['result']} - {stage['distance']} km - "
                    f"{stage['pcs_points']} PCS - {stage['uci_points']} UCI"
                )
                stage_lines.append(stage_line)

            # Handle classifications (no date/distance)
            seen_classes = set()
            for c in info.get("classifications", []):
                cname = c['name']
                if cname.lower() in seen_classes:
                    continue
                seen_classes.add(cname.lower())

                class_line = (
                    f"{cname}\n"
                    f"• {c['result']} - {c['pcs_points']} PCS - {c['uci_points']} UCI"
                )
                classification_lines.append(class_line)

            # Combine into one block
            value_parts = [race_line]
            if stage_lines:
                value_parts.extend(stage_lines)
            if classification_lines:
                value_parts.append("\n**Classifications:**")  # Visual header for clarity
                value_parts.extend(classification_lines)

            value = "\n".join(value_parts)

            # Split into chunks if needed
            for chunk in split_text_preserving_lines(value):
                current_embed.add_field(name="\u200b", value=chunk, inline=False)

        else:  # One-day race
            value = (
                f"**{race} {info['flag']}**\n"
                f"{info['date']} - {info['result']} - {info['distance']} km - "
                f"{info['pcs_points']} PCS - {info['uci_points']} UCI"
            )

            if len(value) > MAX_FIELD_LENGTH:
                for chunk in split_text_preserving_lines(value):
                    current_embed.add_field(name="\u200b", value=chunk, inline=False)
            else:
                current_embed.add_field(name="\u200b", value=value, inline=False)

        # If embed is full, push and start new
        if sum(len(f.value) for f in current_embed.fields) >= 6000:  # embed total limit
            embeds.append(current_embed)
            current_embed = discord.Embed(
                title=f"{name} - Season Results",
                color=discord.Color.from_rgb(255, 255, 255)
            )

    embeds.append(current_embed)

    # Send all embeds
    for embed in embeds:
        await interaction.followup.send(embed=embed)

client.run(token)
