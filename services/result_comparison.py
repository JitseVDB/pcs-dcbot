from pcs_scraper.rider_season_scraper import get_season_results
import re

def compare_results(name1: str, name2: str, season: int):
    results1 = get_season_results(name1, season)
    results2 = get_season_results(name2, season)

    comparison = []

    for race_name, data1 in results1.items():
        data2 = results2.get(race_name)
        if not data2:
            continue

        flag = data1.get("flag", "")
        date = data1.get("date_range") or data1.get("date", "")

        # Stage race
        if "stages" in data1 or "stages" in data2:
            stages1 = {s["description"]: s for s in data1.get("stages", [])} if "stages" in data1 else {}
            stages2 = {s["description"]: s for s in data2.get("stages", [])} if "stages" in data2 else {}
            classes1 = {c["name"]: c for c in data1.get("classifications", [])} if "classifications" in data1 else {}
            classes2 = {c["name"]: c for c in data2.get("classifications", [])} if "classifications" in data2 else {}

            all_subresults = set(stages1.keys()) | set(stages2.keys()) | set(classes1.keys()) | set(classes2.keys())

            # Sort stages numerically by stage number if present
            def stage_sort_key(name):
                m = re.search(r"Stage (\d+)", name)
                return int(m.group(1)) if m else 9999

            for sub in sorted(all_subresults, key=stage_sort_key):
                s1 = stages1.get(sub) or classes1.get(sub)
                s2 = stages2.get(sub) or classes2.get(sub)
                if s1 is None or s2 is None:
                    continue

                # Use stage-specific date if available
                stage_date = s1.get("date") or s2.get("date") or date  # fallback to race date_range

                r1 = s1.get("result")
                r2 = s2.get("result")
                if r1 is None or r2 is None:
                    continue

                # Determine winner
                winner = None
                try:
                    n1 = int(r1) if r1.isdigit() else None
                    n2 = int(r2) if r2.isdigit() else None
                    if n1 is not None and n2 is not None:
                        if n1 < n2:
                            winner = "name1"
                        elif n2 < n1:
                            winner = "name2"
                        else:
                            winner = "tie"
                except ValueError:
                    winner = None

                comparison.append({
                    "race": race_name,
                    "flag": flag,
                    "date": stage_date,
                    "stage_or_class": sub,
                    "name1_result": r1,
                    "name2_result": r2,
                    "winner": winner
                })

        else:  # One-day race
            r1 = data1.get("result")
            r2 = data2.get("result")
            if r1 is None or r2 is None:
                continue

            winner = None
            try:
                n1 = int(r1) if r1.isdigit() else None
                n2 = int(r2) if r2.isdigit() else None
                if n1 is not None and n2 is not None:
                    if n1 < n2:
                        winner = "name1"
                    elif n2 < n1:
                        winner = "name2"
                    else:
                        winner = "tie"
            except ValueError:
                winner = None

            comparison.append({
                "race": race_name,
                "flag": flag,
                "date": date,
                "stage_or_class": None,
                "name1_result": r1,
                "name2_result": r2,
                "winner": winner
            })

    return comparison