from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


EXPORT_DIR = Path("analytics/exports")
PLOT_DIR = Path("analytics/plots")
PLOT_DIR.mkdir(parents=True, exist_ok=True)


profiles = pd.read_csv(EXPORT_DIR / "profiles.csv")
organizers = pd.read_csv(EXPORT_DIR / "organizers.csv")
facilities = pd.read_csv(EXPORT_DIR / "facilities.csv")
entrants = pd.read_csv(EXPORT_DIR / "entrants.csv")
events = pd.read_csv(EXPORT_DIR / "events.csv")
event_participation = pd.read_csv(EXPORT_DIR / "event_participation.csv")


def save_plot(filename):
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename)
    plt.close()


# 1. Top organizers by number of events
top_organizers = organizers.sort_values("event_count", ascending=False).head(10)
top_organizers.plot(x="device_id", y="event_count", kind="bar")
plt.title("Top Organizers by Number of Events")
plt.xlabel("Organizer Device ID")
plt.ylabel("Event Count")
plt.xticks(rotation=45, ha="right")
save_plot("top_organizers.png")


# 2. Average demand by event
top_demand = events.sort_values("demand_count", ascending=False).head(10)
top_demand.plot(x="name", y="demand_count", kind="bar")
plt.title("Top Events by Demand")
plt.xlabel("Event")
plt.ylabel("Demand Count")
plt.xticks(rotation=45, ha="right")
save_plot("top_events_by_demand.png")


# 3. Geo-enabled vs non-geo-enabled events
events["geo_location_enabled"].map({True: "Geo-enabled", False: "Not geo-enabled"}).value_counts().plot(kind="bar")
plt.title("Geo-enabled vs Non-Geo-enabled Events")
plt.xlabel("Event Type")
plt.ylabel("Number of Events")
save_plot("geo_enabled_distribution.png")


# 4. Average fill rate by geo setting
fill_by_geo = (
    events.groupby("geo_location_enabled")["fill_rate"]
    .mean()
    .rename(index={True: "Geo-enabled", False: "Not geo-enabled"})
)
fill_by_geo.plot(kind="bar")
plt.title("Average Fill Rate by Geo Setting")
plt.xlabel("Event Type")
plt.ylabel("Average Fill Rate")
save_plot("fill_rate_by_geo.png")


# 5. Entrant funnel stage distribution
event_participation["stage"].value_counts().plot(kind="bar")
plt.title("Entrant Funnel Stage Distribution")
plt.xlabel("Stage")
plt.ylabel("Number of Records")
save_plot("entrant_stage_distribution.png")


# 6. Entrant activity distribution
top_entrants = entrants.sort_values("total_event_interactions", ascending=False).head(10)
top_entrants.plot(x="device_id", y="total_event_interactions", kind="bar")
plt.title("Top Entrants by Total Event Interactions")
plt.xlabel("Entrant Device ID")
plt.ylabel("Total Event Interactions")
plt.xticks(rotation=45, ha="right")
save_plot("top_entrants.png")


# 7. Demand vs event capacity
events.plot(x="event_slots", y="demand_count", kind="scatter")
plt.title("Event Demand vs Event Capacity")
plt.xlabel("Event Slots")
plt.ylabel("Demand Count")
save_plot("demand_vs_capacity.png")


# Summary table
summary = {
    "total_profiles": len(profiles),
    "total_organizers": len(organizers),
    "total_facilities": len(facilities),
    "total_entrants": len(entrants),
    "total_events": len(events),
    "avg_event_slots": round(events["event_slots"].mean(), 2),
    "avg_demand_per_event": round(events["demand_count"].mean(), 2),
    "avg_fill_rate": round(events["fill_rate"].mean(), 3),
    "geo_enabled_event_share": round(events["geo_location_enabled"].mean(), 3),
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv(EXPORT_DIR / "analytics_summary.csv", index=False)

print("Analytics complete.")
print(summary_df.to_string(index=False))
print(f"Plots saved to {PLOT_DIR}")