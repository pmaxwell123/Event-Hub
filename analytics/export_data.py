import csv
import json
from pathlib import Path


BASE_DIR = Path("analytics/mock_firestore")
EXPORT_DIR = Path("analytics/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filename):
    with (BASE_DIR / filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_csv(filename, rows, fieldnames):
    path = EXPORT_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {path}")


def export_profiles(profiles):
    rows = []
    for device_id, profile in profiles.items():
        rows.append({
            "device_id": device_id,
            "name": profile.get("name", ""),
            "email": profile.get("email", ""),
            "phone": profile.get("phone", ""),
            "using_default_picture": profile.get("usingDefaultPicture", False),
            "admin_notifications": profile.get("adminNotifications", False),
            "admin": profile.get("admin", False),
        })

    write_csv(
        "profiles.csv",
        rows,
        [
            "device_id",
            "name",
            "email",
            "phone",
            "using_default_picture",
            "admin_notifications",
            "admin",
        ],
    )


def export_organizers(organizers):
    rows = []
    for device_id, organizer in organizers.items():
        events = organizer.get("events", [])
        rows.append({
            "device_id": device_id,
            "event_count": len(events),
        })

    write_csv(
        "organizers.csv",
        rows,
        ["device_id", "event_count"],
    )


def export_facilities(facilities):
    rows = []
    for facility_id, facility in facilities.items():
        rows.append({
            "facility_id": facility_id,
            "facility_name": facility.get("facilityName", ""),
            "street_address": facility.get("streetAddress", ""),
            "device_id": facility.get("deviceId", ""),
        })

    write_csv(
        "facilities.csv",
        rows,
        ["facility_id", "facility_name", "street_address", "device_id"],
    )


def export_entrants(entrants):
    rows = []
    for device_id, entrant in entrants.items():
        waitlisted = entrant.get("waitlistedEvents", [])
        finalist = entrant.get("finalistEvents", [])
        invited = entrant.get("invitedEvents", [])
        uninvited = entrant.get("uninvitedEvents", [])

        rows.append({
            "device_id": device_id,
            "waitlisted_event_count": len(waitlisted),
            "finalist_event_count": len(finalist),
            "invited_event_count": len(invited),
            "uninvited_event_count": len(uninvited),
            "total_event_interactions": len(waitlisted) + len(finalist) + len(invited) + len(uninvited),
        })

    write_csv(
        "entrants.csv",
        rows,
        [
            "device_id",
            "waitlisted_event_count",
            "finalist_event_count",
            "invited_event_count",
            "uninvited_event_count",
            "total_event_interactions",
        ],
    )


def export_events(events):
    rows = []
    for event_id, event in events.items():
        waitlisted = event.get("waitlisted", [])
        finalists = event.get("finalists", [])
        selected = event.get("selected", [])
        cancelled = event.get("cancelled", [])
        reselected = event.get("reselected", [])
        join_locations = event.get("joinLocations", [])

        event_slots = int(event.get("eventSlots", 0) or 0)
        waitlist_capacity = int(event.get("waitListCapacity", 0) or 0)

        rows.append({
            "event_id": event_id,
            "name": event.get("name", ""),
            "event_date": event.get("eventDate", ""),
            "time": event.get("time", ""),
            "location": event.get("location", ""),
            "price": event.get("price", ""),
            "event_slots": event_slots,
            "waitlist_capacity": waitlist_capacity,
            "device_id": event.get("deviceId", ""),
            "geo_location_enabled": event.get("geoLocation", False),
            "signup_deadline": event.get("signupDeadline", ""),
            "entrants_chosen": event.get("entrantsChosen", False),
            "disabled": event.get("disabled", False),
            "waitlisted_count": len(waitlisted),
            "finalist_count": len(finalists),
            "selected_count": len(selected),
            "cancelled_count": len(cancelled),
            "reselected_count": len(reselected),
            "join_location_count": len(join_locations),
            "demand_count": len(waitlisted) + len(finalists) + len(selected) + len(reselected),
            "fill_rate": round(len(finalists) / event_slots, 3) if event_slots else 0,
            "oversubscription_ratio": round((len(waitlisted) + len(finalists) + len(selected) + len(reselected)) / event_slots, 3) if event_slots else 0,
        })

    write_csv(
        "events.csv",
        rows,
        [
            "event_id",
            "name",
            "event_date",
            "time",
            "location",
            "price",
            "event_slots",
            "waitlist_capacity",
            "device_id",
            "geo_location_enabled",
            "signup_deadline",
            "entrants_chosen",
            "disabled",
            "waitlisted_count",
            "finalist_count",
            "selected_count",
            "cancelled_count",
            "reselected_count",
            "join_location_count",
            "demand_count",
            "fill_rate",
            "oversubscription_ratio",
        ],
    )


def export_event_participation(events):
    rows = []

    for event_id, event in events.items():
        stage_map = {
            "waitlisted": event.get("waitlisted", []),
            "finalist": event.get("finalists", []),
            "selected": event.get("selected", []),
            "cancelled": event.get("cancelled", []),
            "reselected": event.get("reselected", []),
        }

        for stage, entrants in stage_map.items():
            for device_id in entrants:
                rows.append({
                    "event_id": event_id,
                    "device_id": device_id,
                    "stage": stage,
                })

    write_csv(
        "event_participation.csv",
        rows,
        ["event_id", "device_id", "stage"],
    )


def run():
    profiles = load_json("profiles.json")
    organizers = load_json("organizers.json")
    facilities = load_json("facilities.json")
    entrants = load_json("entrants.json")
    events = load_json("events.json")

    export_profiles(profiles)
    export_organizers(organizers)
    export_facilities(facilities)
    export_entrants(entrants)
    export_events(events)
    export_event_participation(events)

    print("Done exporting Event Hub analytics data.")


run()