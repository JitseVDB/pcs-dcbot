from pcs_scraper.rider_info_scraper import get_rider_age, get_rider_nationality, get_rider_weight, get_rider_height, get_rider_birthdate, get_rider_place_of_birth, get_rider_image_url
from pcs_scraper.rider_points_scraper import get_points_per_speciality, get_points_per_season
from pcs_scraper.rider_season_scraper import get_season_results, get_rider_program
from pcs_scraper.rider_team_history_scraper import get_rider_team_history
from pcs_scraper.race_result_scraper import get_rider_result_in_race
from pcs_scraper.race_info_scraper import get_race_flag
from helpers.plotter import plot_points_table_style, plot_points_per_speciality_table
from helpers.format_helper import split_text_preserving_lines, ordinal
from helpers.country_helper import country_to_emoji
from services.program_comparison import compare_programs
from services.result_comparison import compare_results
from services.past_results import get_past_results
from constants import MAX_FIELD_LENGTH, MAX_EMBED_DESCRIPTION_LENGTH
from discord import app_commands
from dotenv import load_dotenv
import discord
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
        points_per_season_history = get_points_per_season(name)
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
        points_data = get_points_per_speciality(name)
        if not points_data:
            await interaction.response.send_message(f"No points per speciality found for '{name}'")
            return

        image_buffer = plot_points_per_speciality_table(points_data, rider_name=name)
        file = discord.File(fp=image_buffer, filename="speciality_points.png")
        embed = discord.Embed(
            title=f"{name} - PCS Points per Speciality",
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
@app_commands.describe(
    name="Full name of the rider",
    season="The year of the season"
)
async def season_results_cmd(interaction: discord.Interaction, name: str, season: int):
    await interaction.response.defer()  # defer in case scraping takes time

    try:
        races = get_season_results(name, season)
    except Exception as e:
        await interaction.followup.send(f"Failed to fetch season results for '{name}': {e}")
        return

    if not races:
        await interaction.followup.send(f"No season results found for '{name}'.")
        return

    embeds = []
    current_embed = discord.Embed(
        title=f"{name} - {season} Season Results",
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

# rider program command
@client.tree.command(
    name="rider-program",
    description="Get upcoming program of a rider",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(name="Full name of the rider")
async def rider_program(interaction: discord.Interaction, name: str):
    await interaction.response.defer()

    races = get_rider_program(name)
    if not races:
        await interaction.followup.send(f"No race program found for {name}.")
        return

    # Create a white embed
    embed = discord.Embed(
        title=f"{name} - Race Program",
        color=(255 << 16) + (255 << 8) + 255  # white
    )

    # Build the description: "date - flag title"
    description = ""
    for race in races:
        description += f"{race['date']} - {race['flag']} {race['title']}\n"

    embed.description = description.strip()

    await interaction.followup.send(embed=embed)

# rider program comparison command
@client.tree.command(
    name="compare-rider-programs",
    description="Compare the upcoming program of 2 riders",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    name1="Full name of the first rider",
    name2="Full name of the second rider"
)
async def rider_program(interaction: discord.Interaction, name1: str, name2: str):
    await interaction.response.defer()

    comparison = compare_programs(name1, name2)
    if not comparison:
        await interaction.followup.send(f"Comparison between program of {name1} and program of {name2} failed.")
        return

    # Create a white embed
    embed = discord.Embed(
        title=f"{name1} vs {name2} - Race Program Comparison",
        color=(255 << 16) + (255 << 8) + 255
    )

    description = ""
    for race in comparison:
        # Race line: date - flag - title
        description += f"**{race['date']} - {race['flag']} {race['title']}**\n"

        # Participation line using monospaced text for alignment
        r1 = "✅" if race["name1_participating"] else "❌"
        r2 = "✅" if race["name2_participating"] else "❌"
        description += f"`{r1:<2} {name1:<20}`  `{r2:<2} {name2:<20}`\n\n"

    embed.description = description.strip()

    await interaction.followup.send(embed=embed)

# rider season results comparison command
@client.tree.command(
    name="compare-rider-season-results",
    description="Compare the season results of 2 riders",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    name1="Full name of the first rider",
    name2="Full name of the second rider",
    season="The year of the season"
)
async def compare_results(interaction: discord.Interaction, name1: str, name2: str, season: int):
    await interaction.response.defer()

    comparison = compare_results(name1, name2, season)
    if not comparison:
        await interaction.followup.send(f"Comparison between season results of {name1} and {name2} failed.")
        return

    # Count wins
    wins_name1 = sum(1 for entry in comparison if entry['winner'] == 'name1')
    wins_name2 = sum(1 for entry in comparison if entry['winner'] == 'name2')

    # Start description with head-to-head summary
    description = f"🏆 **Head-to-Head:** {name1} {wins_name1} - {wins_name2} {name2}\n\n"

    for entry in comparison:
        race_line = f"**{entry['date']} - {entry['flag']} {entry['race']}**"
        stage = f" - {entry['stage_or_class']}" if entry['stage_or_class'] else ""
        description += f"{race_line}{stage}\n"

        n1_res = entry['name1_result']
        n2_res = entry['name2_result']

        if entry['winner'] == 'name1':
            n1_res = f"{n1_res} 🏆"
        elif entry['winner'] == 'name2':
            n2_res = f"{n2_res} 🏆"

        description += f"`{name1:<15}: {n1_res:<5}`  `{name2:<15}: {n2_res:<5}`\n\n"

    # Split description if too long
    description_chunks = split_text_preserving_lines(description, MAX_EMBED_DESCRIPTION_LENGTH)

    embeds = []
    for i, chunk in enumerate(description_chunks):
        embed = discord.Embed(
            title=f"{name1} vs {name2} - {season} Season Results Comparison",
            description=chunk,
            color=0xFFFFFF
        )
        embeds.append(embed)

    # Send all embeds
    for embed in embeds:
        await interaction.followup.send(embed=embed)

# Rider past results command
@client.tree.command(
    name="rider-past-results",
    description="Show the past results of a rider in a given race across seasons",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    name="Full name of the rider",
    race="Race name (e.g. 'Ronde Van Vlaanderen')"
)
async def rider_past_results(interaction: discord.Interaction, name: str, race: str):
    await interaction.response.defer()

    results = get_past_results(name, race)
    race_flag = get_race_flag(race)
    rider_nationality = get_rider_nationality(name)
    rider_flag = country_to_emoji(rider_nationality)

    if not results:
        await interaction.followup.send(f"Could not retrieve past results for {name} in {race}.")
        return

    # Embed title with flags
    title = f"{rider_flag} {name} – {race_flag} {race} Past Results"

    description_lines = []
    for season in sorted(results.keys(), reverse=True):
        res = results[season]
        if res:  # Only include seasons where rider had a result
            # Add medal for top 3
            medal = ""
            if res == "1":
                medal = " 🥇"
            elif res == "2":
                medal = " 🥈"
            elif res == "3":
                medal = " 🥉"

            description_lines.append(f"**{season}:** {res}{medal}")

    if not description_lines:
        await interaction.followup.send(f"No past results available for {name} in {race}.")
        return

    description = "\n".join(description_lines)

    # Split description if too long
    description_chunks = split_text_preserving_lines(description, MAX_EMBED_DESCRIPTION_LENGTH)

    embeds = []
    for chunk in description_chunks:
        embed = discord.Embed(
            title=title,
            description=chunk,
            color=0xFFFFFF
        )
        embeds.append(embed)

    for embed in embeds:
        await interaction.followup.send(embed=embed)

# Rider single race result command
@client.tree.command(
    name="rider-race-result",
    description="Show the result of a rider in a specific race and season",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    name="Full name of the rider",
    race="Race name (e.g., 'Ronde Van Vlaanderen')",
    season="Season year"
)
async def rider_race_result(interaction: discord.Interaction, name: str, race: str, season: int):
    await interaction.response.defer()

    result = get_rider_result_in_race(name, race, season)
    if not result:
        await interaction.followup.send(f"{name} did not participate in {race} during {season}.")
        return

    try:
        result_int = int(result)
        result_str = ordinal(result_int)
    except ValueError:
        result_str = result  # fallback if rank is not a number

    # Add medal emoji for podium
    medal = ""
    if result_str.startswith("1"):
        medal = " 🥇"
    elif result_str.startswith("2"):
        medal = " 🥈"
    elif result_str.startswith("3"):
        medal = " 🥉"

    await interaction.followup.send(f"{name} got **{result_str}{medal}** place in {race} ({season})")

# Race flag command
@client.tree.command(
    name="race-flag",
    description="Get the flag emoji of a race",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    race="Race name (e.g., 'Ronde Van Vlaanderen')"
)
async def race_flag_command(interaction: discord.Interaction, race: str):
    await interaction.response.defer()

    try:
        emoji = get_race_flag(race)
        if not emoji:
            await interaction.followup.send(f"Could not find the flag for {race}.")
            return

        await interaction.followup.send(f"The flag for **{race}** is {emoji}")
    except Exception as e:
        await interaction.followup.send(f"An error occurred while fetching the flag for {race}: {e}")

client.run(token)
