import json
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

BASE_DIR = Path("analytics/mock_firestore")
BASE_DIR.mkdir(parents=True, exist_ok=True)


def save_json(filename, data):
    path = BASE_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {path}")


def make_device_id(i):
    return f"device_{i:03d}"


def make_event_id(i):
    return f"event_{i:03d}"


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def random_time():
    hour = random.randint(9, 20)
    minute = random.choice([0, 15, 30, 45])
    return f"{hour:02d}:{minute:02d}"


def random_future_date(days_ahead_min=5, days_ahead_max=120):
    date = datetime.now() + timedelta(days=random.randint(days_ahead_min, days_ahead_max))
    return date.strftime("%m/%d/%Y")


def random_signup_deadline(event_date_str):
    event_date = datetime.strptime(event_date_str, "%m/%d/%Y")
    deadline = event_date - timedelta(days=random.randint(3, 21))
    return deadline.strftime("%m/%d/%Y")


def random_price():
    if random.random() < 0.25:
        return "0"
    return random.choice(["5", "10", "15", "20", "25", "30", "40", "50"])


def random_lat_lon():
    # Roughly around Edmonton for demo purposes
    lat = round(random.uniform(53.45, 53.62), 6)
    lon = round(random.uniform(-113.62, -113.35), 6)
    return [lat, lon]


def build_profiles(num_profiles=24, num_admins=5):
    first_names = [
        "Alex", "Jordan", "Taylor", "Morgan", "Avery", "Sam", "Riley", "Jamie",
        "Cameron", "Casey", "Drew", "Parker", "Quinn", "Skyler", "Emerson",
        "Hayden", "Rowan", "Blake", "Finley", "Logan", "Elliot", "Kendall",
        "Reese", "Charlie"
    ]
    last_names = [
        "Lee", "Patel", "Wong", "Kim", "Brown", "Nguyen", "Garcia", "Smith",
        "Miller", "Johnson", "Wilson", "Clark", "Ahmed", "Singh", "Lopez",
        "Martin", "Baker", "Hall", "Scott", "Turner", "Young", "Evans", "Hill", "Moore"
    ]

    profiles = {}
    admin_ids = set(random.sample([make_device_id(i) for i in range(1, num_profiles + 1)], num_admins))

    for i in range(1, num_profiles + 1):
        device_id = make_device_id(i)
        name = f"{first_names[i - 1]} {last_names[i - 1]}"
        profiles[device_id] = {
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@example.com",
            "phone": f"780555{1000 + i}",
            "deviceId": device_id,
            "profilePicturePath": f"/mock/profiles/{device_id}.png",
            "usingDefaultPicture": random.random() < 0.7,
            "adminNotifications": random.random() < 0.8,
            "admin": device_id in admin_ids,
        }

    return profiles


def build_organizers_and_facilities(profiles, num_organizers=8):
    organizer_ids = sorted(random.sample(list(profiles.keys()), num_organizers))
    street_names = [
        "Whyte Ave", "Jasper Ave", "82 Ave", "Gateway Blvd", "109 St",
        "104 St", "97 St", "Kingsway", "118 Ave", "111 Ave"
    ]
    facility_prefixes = [
        "Student Centre", "Innovation Hub", "Conference Hall", "Community Centre",
        "Arts Building", "Sports Complex", "Library Room", "Tech Lab"
    ]

    organizers = {}
    facilities = {}

    for i, device_id in enumerate(organizer_ids, start=1):
        organizers[device_id] = {
            "deviceId": device_id,
            "events": [],
        }

        facilities[f"facility_{i:03d}"] = {
            "facilityName": f"{random.choice(facility_prefixes)} {i}",
            "streetAddress": f"{random.randint(1000, 9999)} {random.choice(street_names)}, Edmonton, AB",
            "deviceId": device_id,
        }

    return organizers, facilities


def initialize_entrants(profiles):
    entrants = {}
    for device_id, profile in profiles.items():
        if not profile["admin"]:
            entrants[device_id] = {
                "waitlistedEvents": [],
                "finalistEvents": [],
                "invitedEvents": [],
                "uninvitedEvents": [],
            }
    return entrants


def choose_attendees(candidate_ids, event_slots, waitlist_capacity, entrants_chosen):
    interested_count = random.randint(
        max(0, event_slots // 2),
        max(event_slots, waitlist_capacity + max(2, event_slots // 2)),
    )
    interested = random.sample(candidate_ids, min(interested_count, len(candidate_ids)))
    random.shuffle(interested)

    if not interested:
        return [], [], [], [], []

    finalist_count = min(
        random.randint(max(0, event_slots // 3), max(1, event_slots)),
        len(interested),
        event_slots,
    )
    finalists = interested[:finalist_count]

    remaining = interested[finalist_count:]
    selected_count = 0
    if entrants_chosen and remaining:
        selected_count = min(
            random.randint(0, max(1, min(event_slots, len(remaining)))),
            len(remaining),
        )
    selected = remaining[:selected_count]

    remaining = remaining[selected_count:]
    reselected_count = 0
    if entrants_chosen and remaining and random.random() < 0.45:
        reselected_count = min(random.randint(0, min(3, len(remaining))), len(remaining))
    reselected = remaining[:reselected_count]

    remaining = remaining[reselected_count:]
    waitlisted = remaining[: min(len(remaining), waitlist_capacity)]
    cancelled = remaining[min(len(remaining), waitlist_capacity):]

    return waitlisted, finalists, selected, cancelled, reselected


def build_events(profiles, organizers, facilities, entrants, num_events=40):
    event_names = [
        "Hack Night", "Startup Mixer", "AI Workshop", "Campus Concert", "Career Fair",
        "Board Game Evening", "Resume Clinic", "Networking Lunch", "Case Competition",
        "Photography Walk", "Data Science Meetup", "Design Sprint", "Tech Talk",
        "Volunteer Orientation", "Entrepreneurship Panel", "Wellness Session",
        "Open Mic Night", "Research Showcase", "Coding Bootcamp", "Leadership Seminar"
    ]

    descriptions = [
        "A student-focused event with networking and collaboration opportunities.",
        "An interactive event designed to connect participants with organizers and peers.",
        "A hands-on session featuring practical activities and group participation.",
        "An event that blends learning, community, and engagement in one setting.",
        "A campus event aimed at helping students discover new opportunities."
    ]

    facility_by_device = {f["deviceId"]: f for f in facilities.values()}
    non_admin_entrant_ids = list(entrants.keys())
    events = {}

    for i in range(1, num_events + 1):
        event_id = make_event_id(i)
        organizer_id = random.choice(list(organizers.keys()))
        facility = facility_by_device[organizer_id]

        event_date = random_future_date()
        signup_deadline = random_signup_deadline(event_date)
        event_slots = random.randint(15, 80)
        waitlist_capacity = random.randint(event_slots, event_slots + random.randint(10, 60))
        geo_enabled = random.random() < 0.45
        entrants_chosen = random.random() < 0.65

        waitlisted, finalists, selected, cancelled, reselected = choose_attendees(
            [d for d in non_admin_entrant_ids if d != organizer_id],
            event_slots,
            waitlist_capacity,
            entrants_chosen,
        )

        join_locations = []
        if geo_enabled:
            for entrant_id in finalists:
                join_locations.append({entrant_id: random_lat_lon()})

        qr_data = f"QR::{event_id}"
        qr_hash = hash_text(qr_data)

        event = {
            "name": f"{random.choice(event_names)} {i}",
            "eventDate": event_date,
            "time": random_time(),
            "description": random.choice(descriptions),
            "price": random_price(),
            "waitListCapacity": waitlist_capacity,
            "eventSlots": event_slots,
            "waitlisted": waitlisted,
            "finalists": finalists,
            "cancelled": cancelled,
            "selected": selected,
            "reselected": reselected,
            "qrCodeData": qr_data,
            "qrHash": qr_hash,
            "eventID": event_id,
            "geoLocation": geo_enabled,
            "waitlistedNotificationsList": waitlisted.copy(),
            "selectedNotificationsList": (selected + reselected).copy(),
            "joinedNotificationsList": finalists.copy(),
            "cancelledNotificationsList": cancelled.copy(),
            "joinLocations": join_locations,
            "location": facility["streetAddress"],
            "deviceId": organizer_id,
            "signupDeadline": signup_deadline,
            "entrantsChosen": entrants_chosen,
            "eventPosterURL": f"https://example.com/posters/{event_id}.jpg",
            "disabled": random.random() < 0.08,
        }

        events[event_id] = event
        organizers[organizer_id]["events"].append(event_id)

        for entrant_id in waitlisted:
            entrants[entrant_id]["waitlistedEvents"].append(event_id)

        for entrant_id in finalists:
            entrants[entrant_id]["finalistEvents"].append(event_id)

        for entrant_id in selected + reselected:
            entrants[entrant_id]["invitedEvents"].append(event_id)

        for entrant_id in cancelled:
            entrants[entrant_id]["uninvitedEvents"].append(event_id)

    return events


def run():
    profiles = build_profiles()
    organizers, facilities = build_organizers_and_facilities(profiles)
    entrants = initialize_entrants(profiles)
    events = build_events(profiles, organizers, facilities, entrants)

    save_json("profiles.json", profiles)
    save_json("organizers.json", organizers)
    save_json("facilities.json", facilities)
    save_json("entrants.json", entrants)
    save_json("events.json", events)

    print("\nDemo dataset created.")
    print(f"Profiles: {len(profiles)}")
    print(f"Organizers: {len(organizers)}")
    print(f"Facilities: {len(facilities)}")
    print(f"Entrants: {len(entrants)}")
    print(f"Events: {len(events)}")


run()