import matplotlib.pyplot as plt
import io

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