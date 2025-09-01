from unidecode import unidecode
from helpers.format_helper import reformat_name
import re
import pycountry
from procyclingstats import Rider
import matplotlib.pyplot as plt
import io
import discord

def format_season_results_embeds(results, rider_name):
    """
    Format season results into one or more embeds with a clean readable layout.
    Groups by race, stages underneath.
    """
    if not results:
        return [discord.Embed(
            title=f"{rider_name} — Season Results",
            description="No results found.",
            color=discord.Color.red()
        )]

    embeds = []
    current_desc = ""
    max_len = 3500  # keep buffer under 4096
    current_race = None

    for r in results:
        date = r.get("date") or "-"
        result = r.get("result") or "-"
        race = r.get("stage_name") or "-"
        distance = f"{r.get('distance', '-')}" if r.get("distance") else "-"
        pcs = str(r.get("pcs_points") or "-")
        uci = str(r.get("uci_points") or "-")

        # Detect race group change
        if race != current_race:
            if current_desc:  # flush previous embed if too long
                embed = discord.Embed(
                    title=f"{rider_name} — Season Results",
                    description=current_desc,
                    color=discord.Color.green()
                )
                embeds.append(embed)
                current_desc = ""

            current_desc += f"\n**🏁 {race}**\n"
            current_race = race

        # Add stage line
        line = f"> {date} | {result} | {distance} km | {pcs} PCS | {uci} UCI\n"

        # Flush into new embed if needed
        if len(current_desc) + len(line) > max_len:
            embed = discord.Embed(
                title=f"{rider_name} — Season Results",
                description=current_desc,
                color=discord.Color.green()
            )
            embeds.append(embed)
            current_desc = f"\n**🏁 {race}**\n"

        current_desc += line

    # Final embed
    if current_desc:
        embed = discord.Embed(
            title=f"{rider_name} — Season Results",
            description=current_desc,
            color=discord.Color.green()
        )
        embeds.append(embed)

    return embeds

def plot_points_per_speciality_table(points_data: dict, rider_name="Rider"):
    SPECIALITY_COLORS = {
        "one_day_races": "limegreen",
        "gc": "red",
        "time_trial": "deepskyblue",
        "sprint": "orange",
        "climber": "mediumpurple",
        "hills": "hotpink"
    }

    SPECIALITY_LABELS = {
        "one_day_races": "Oneday race",
        "gc": "GC",
        "time_trial": "Time Trial",
        "sprint": "Sprint",
        "climber": "Climber",
        "hills": "Hill"
    }

    if not points_data:
        return None

    specialties = list(SPECIALITY_COLORS.keys())
    points = [points_data.get(s, 0) for s in specialties]
    max_points = max(points) if points else 1

    fig, ax = plt.subplots(figsize=(8, 6))
    y_positions = range(len(specialties))
    bar_height = 0.6

    # Draw horizontal separators BETWEEN bars
    for y in [-0.5 + i for i in range(len(specialties) + 1)]:
        ax.hlines(y=y, xmin=0, xmax=max_points*1.15, color='lightgrey', linewidth=0.8)

    # Draw bars, specialty labels, and points
    for y, s, p in zip(y_positions, specialties, points):
        # Base bar
        ax.barh(y, max_points, color='lightgrey', height=bar_height)
        # Colored proportional fill
        ax.barh(y, p, color=SPECIALITY_COLORS[s], height=bar_height)
        # Left: specialty label
        ax.text(-max_points*0.02, y, SPECIALITY_LABELS[s], va='center', ha='right', fontsize=10)
        # Right: points
        ax.text(max_points + max_points*0.01, y, str(p), va='center', fontsize=10)

    # Clean axes
    ax.set_yticks([])
    ax.set_xlim(0, max_points*1.15)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.invert_yaxis()  # Top specialty at top
    ax.set_title(f"{rider_name} — PCS Points per Speciality", pad=15)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return buffer

def format_season_results(results: list[dict]) -> str:
    lines = []
    for r in results:
        date = r.get("date", "-")
        stage_name = r.get("stage_name", "-")
        result = r.get("result", "-")
        gc_position = r.get("gc_position", "-")
        pcs_points = r.get("pcs_points", 0)
        uci_points = r.get("uci_points", 0)
        lines.append(f"{date} | {stage_name} | Result: {result} | GC: {gc_position} | PCS: {pcs_points} | UCI: {uci_points}")
    return "\n".join(lines) if lines else "No results available."

def plot_points_table_style(points_data, rider_name="Rider"):
    seasons = [str(d["season"]) for d in points_data]
    points = [d["points"] for d in points_data]
    ranks = [d["rank"] for d in points_data]

    fig, ax = plt.subplots(figsize=(8, 6))

    y_positions = range(len(seasons))

    # Create horizontal bars
    bars = ax.barh(y_positions, points, color='limegreen', height=0.6)

    # Hide default y-axis
    ax.set_yticks([])

    # Add horizontal separator lines BETWEEN bars
    for y in [-0.5 + i for i in range(len(seasons) + 1)]:
        ax.hlines(y=y, xmin=0, xmax=max(points) * 1.15, color='lightgrey', linewidth=0.8)

    # Add season labels on the left
    for y, season in zip(y_positions, seasons):
        ax.text(-max(points) * 0.02, y, season, va='center', ha='right', fontsize=10)

    # Add rank on the right of each bar
    for bar, rank in zip(bars, ranks):
        width = bar.get_width()
        ax.text(width + max(points) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"#{rank}", va='center', fontsize=10)

    # Clean up axes
    ax.set_xlim(0, max(points) * 1.15)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])  # optional: remove x-axis ticks

    ax.invert_yaxis()  # newest season at top
    ax.set_title(f"{rider_name} — PCS Points per Season", pad=15)
    plt.tight_layout()

    # Save to BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return buffer

def split_text(text, limit=2000):
    lines = text.splitlines()
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line + "\n"
        else:
            current += line + "\n"
    if current:
        chunks.append(current)
    return chunks

# Convert team history dicts into lines of text
def format_team_history(team_history_list):
    lines = []
    for entry in team_history_list:
        # Example: {'season': 2025, 'team_name': 'Team Visma', 'class': 'WT', 'since': '01-01', 'until': '12-31'}
        season = entry.get('season', '')
        team_name = entry.get('team_name', '')
        team_class = entry.get('class', '')
        since = entry.get('since', '')
        until = entry.get('until', '')

        if since and until:
            lines.append(f"{season} {team_name} ({team_class}) from {since} to {until}")
        else:
            lines.append(f"{season} {team_name} ({team_class})")
    return lines

def country_full_name(code: str) -> str:
    try:
        country = pycountry.countries.get(alpha_2=code.upper())
        return country.name if country else code
    except:
        return code

def country_flag_emoji(code: str) -> str:
    OFFSET = 127397  # Unicode offset for regional indicator symbols
    return "".join([chr(ord(char.upper()) + OFFSET) for char in code])

def country_with_flag(code: str) -> str:
    full_name = country_full_name(code)
    flag = country_flag_emoji(code)
    return f"{full_name} {flag}"


def get_rider_team_history(name: str):
    pcs_name = reformat_name(name)
    try:
        rider = Rider(f"rider/{pcs_name}")
        return rider.teams_history()
    except Exception:
        return None

def get_rider_points_per_season_history(name: str):
    pcs_name = reformat_name(name)
    try:
        rider = Rider(f"rider/{pcs_name}")
        return rider.points_per_season_history()
    except Exception:
        return None

def get_rider_points_per_speciality(name: str):
    pcs_name = reformat_name(name)
    try:
        rider = Rider(f"rider/{pcs_name}")
        return rider.points_per_speciality()
    except Exception:
        return None