#!/usr/bin/env python3
"""
Moral Video Game Library — Catalog Builder
Created by Daniel Bates, BatesAI LLC

Builds a curated SQLite catalog of retro video games that meet the
Moral Video Game Library qualification criteria:

1. No longer supported by original developer/publisher
2. Not remastered, remade, or re-released on modern platforms
3. At least 10 years since last official publication
4. Priority given to titles from defunct/inactive studios

Data sourced from libretro-database (MIT License).
"""

import sqlite3
import os
import re
import subprocess
import sys
from datetime import datetime

# Known remastered/re-released game patterns to EXCLUDE
# These games are still commercially available or have been remade
REMASTERED_EXCLUSIONS = [
    # Nintendo first-party (available on Switch Online or remade)
    r"Super Mario Bros",
    r"Super Mario World",
    r"Super Mario 64",
    r"Super Mario Kart",
    r"Mario Kart 64",
    r"Legend of Zelda",
    r"Zelda II",
    r"Link to the Past",
    r"Ocarina of Time",
    r"Majora's Mask",
    r"Metroid",
    r"Super Metroid",
    r"Metroid Fusion",
    r"Metroid Zero Mission",
    r"Kirby's Adventure",
    r"Kirby Super Star",
    r"Kirby's Dream Land",
    r"Star Fox",
    r"Star Fox 64",
    r"F-Zero",
    r"Donkey Kong Country",
    r"Donkey Kong 64",
    r"Pokemon Red",
    r"Pokemon Blue",
    r"Pokemon Yellow",
    r"Pokemon Gold",
    r"Pokemon Silver",
    r"Pokemon Crystal",
    r"Pokemon Ruby",
    r"Pokemon Sapphire",
    r"Pokemon Emerald",
    r"Pokemon FireRed",
    r"Pokemon LeafGreen",
    r"EarthBound",
    r"Mother",
    r"Fire Emblem",
    r"Advance Wars",
    r"Animal Crossing",
    r"Super Smash Bros",
    r"Mario Party",
    r"Paper Mario",
    r"Punch-Out",
    r"Ice Climber",
    r"Kid Icarus",
    r"Excitebike",
    r"Pikmin",
    r"Wave Race",
    r"1080.*Snowboarding",
    r"Golden Sun",
    # Sega (available on modern platforms)
    r"Sonic the Hedgehog",
    r"Sonic 2",
    r"Sonic 3",
    r"Sonic & Knuckles",
    r"Streets of Rage",
    r"Phantasy Star",
    r"Shining Force",
    r"Ecco the Dolphin",
    r"Virtua Fighter",
    r"Crazy Taxi",
    r"Jet Set Radio",
    r"NiGHTS",
    r"Panzer Dragoon",
    r"Shenmue",
    r"Space Channel 5",
    r"Super Monkey Ball",
    # Capcom (re-released collections)
    r"Mega Man",
    r"Street Fighter",
    r"Resident Evil",
    r"Devil May Cry",
    r"Ghosts '?n",
    r"Final Fight",
    r"Breath of Fire",
    # Square Enix
    r"Final Fantasy",
    r"Chrono Trigger",
    r"Chrono Cross",
    r"Secret of Mana",
    r"Dragon Quest",
    r"Kingdom Hearts",
    r"Star Ocean",
    r"SaGa",
    r"Trials of Mana",
    r"Romancing SaGa",
    r"Valkyrie Profile",
    # Konami
    r"Castlevania",
    r"Metal Gear",
    r"Contra",
    r"Gradius",
    r"Teenage Mutant Ninja Turtles",
    r"Silent Hill",
    r"Suikoden",
    # Namco/Bandai
    r"Pac-Man",
    r"Tekken",
    r"Tales of",
    r"Dig Dug",
    r"Galaga",
    r"Ridge Racer",
    r"Ace Combat",
    r"Soul Calibur",
    r"SoulBlade",
    # SNK
    r"King of Fighters",
    r"Fatal Fury",
    r"Art of Fighting",
    r"Samurai Shodown",
    r"Metal Slug",
    # Atlus
    r"Shin Megami Tensei",
    r"Persona",
    r"Disgaea",
    # Other well-known re-releases
    r"Doom",
    r"Quake",
    r"Diablo",
    r"Baldur's Gate",
    r"Icewind Dale",
    r"Planescape",
    r"Myst",
    r"Spyro",
    r"Crash Bandicoot",
    r"Tony Hawk",
    r"Grand Theft Auto",
    r"Tomb Raider",
    r"Prince of Persia",
    r"Rayman",
    r"Oddworld",
    r"System Shock",
    r"Deus Ex",
    r"Thief",
    r"Warcraft",
    r"StarCraft",
    r"Age of Empires",
    r"Command & Conquer",
    r"SimCity",
    r"Civilization",
    r"Tetris",
    r"Bomberman",
    r"Harvest Moon",
    r"Mega Man X",
    r"Mega Man Battle Network",
    r"Mega Man Zero",
    r"Mega Man Legends",
    r"Klonoa",
    r"Wonder Boy",
    r"Alex Kidd",
    r"Ys ",
    r"Langrisser",
    r"R-Type",
    r"Darius",
    r"Cotton",
    r"Vampire",
    r"Darkstalkers",
    r"Marvel vs",
    r"Capcom vs",
    r"SNK vs",
    r"Bionic Commando",
    r"Strider",
    r"Ghosts 'n Goblins",
    r"Ghouls 'n Ghosts",
]

# Platforms that qualify (retro, 10+ years since last game published)
QUALIFYING_PLATFORMS = [
    "Nintendo - Nintendo Entertainment System",
    "Nintendo - Super Nintendo Entertainment System",
    "Nintendo - Game Boy",
    "Nintendo - Game Boy Color",
    "Nintendo - Game Boy Advance",
    "Nintendo - Nintendo 64",
    "Nintendo - Nintendo DS",
    "Nintendo - Virtual Boy",
    "Sega - Master System - Mark III",
    "Sega - Mega Drive - Genesis",
    "Sega - Game Gear",
    "Sega - Saturn",
    "Sega - Dreamcast",
    "Sega - 32X",
    "Sega - Mega-CD - Sega CD",
    "Sega - SG-1000",
    "Sony - PlayStation",
    "Sony - PlayStation 2",
    "Sony - PlayStation Portable",
    "Atari - 2600",
    "Atari - 5200",
    "Atari - 7800",
    "Atari - Jaguar",
    "Atari - Lynx",
    "Atari - ST",
    "NEC - PC Engine - TurboGrafx-16",
    "NEC - PC Engine SuperGrafx",
    "NEC - PC Engine CD - TurboGrafx-CD",
    "NEC - PC-FX",
    "SNK - Neo Geo Pocket",
    "SNK - Neo Geo Pocket Color",
    "SNK - Neo Geo CD",
    "Bandai - WonderSwan",
    "Bandai - WonderSwan Color",
    "Coleco - ColecoVision",
    "GCE - Vectrex",
    "Magnavox - Odyssey2",
    "Mattel - Intellivision",
    "Commodore - 64",
    "Commodore - Amiga",
    "Sinclair - ZX Spectrum",
    "Amstrad - CPC",
    "MSX",
    "MSX2",
    "DOS",
    "3DO Interactive Multiplayer",
    "Philips - Videopac+",
]

DB_PATH = os.path.join(os.path.dirname(__file__), "moral_video_game_library.db")
SOURCE_DB = os.path.expanduser("~/X10/Games & ROMs/retro_catalog.db")


def build_qualification_table(db_path):
    """Add qualification filtering to the database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create qualification table
    c.execute("DROP TABLE IF EXISTS qualification")
    c.execute("""
        CREATE TABLE qualification (
            game_id INTEGER PRIMARY KEY,
            qualified INTEGER DEFAULT 0,
            exclusion_reason TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    """)

    # Create exclusions table for transparency
    c.execute("DROP TABLE IF EXISTS exclusions")
    c.execute("""
        CREATE TABLE exclusions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            reason TEXT NOT NULL,
            category TEXT
        )
    """)

    # Log all exclusion patterns
    for pattern in REMASTERED_EXCLUSIONS:
        c.execute(
            "INSERT INTO exclusions (pattern, reason, category) VALUES (?, ?, ?)",
            (pattern, "Remastered, remade, or re-released on modern platforms", "remaster"),
        )

    # Create metadata table with qualification criteria
    c.execute("DROP TABLE IF EXISTS library_metadata")
    c.execute("""
        CREATE TABLE library_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    metadata = {
        "name": "Moral Video Game Library",
        "creator": "Daniel Bates",
        "organization": "BatesAI LLC",
        "created_date": datetime.now().isoformat(),
        "criteria_1": "No longer supported by original developer/publisher",
        "criteria_2": "Not remastered, remade, or re-released on modern platforms",
        "criteria_3": "At least 10 years since last official publication (before 2016)",
        "criteria_4": "Priority given to titles from defunct or inactive studios",
        "ethical_position": "These games represent abandoned cultural works that cannot be purchased through any legitimate channel. This library exists for preservation, personal use, education, and historical research.",
        "source": "libretro-database (MIT License)",
        "license": "MIT",
    }

    for key, value in metadata.items():
        c.execute("INSERT INTO library_metadata (key, value) VALUES (?, ?)", (key, value))

    # Get qualifying platform IDs
    placeholders = ",".join(["?" for _ in QUALIFYING_PLATFORMS])
    c.execute(f"SELECT id, name FROM platforms WHERE name IN ({placeholders})", QUALIFYING_PLATFORMS)
    qualifying_platform_ids = {row[0]: row[1] for row in c.fetchall()}

    if not qualifying_platform_ids:
        # Try partial matching
        for plat in QUALIFYING_PLATFORMS:
            c.execute("SELECT id, name FROM platforms WHERE name LIKE ?", (f"%{plat}%",))
            for row in c.fetchall():
                qualifying_platform_ids[row[0]] = row[1]

    print(f"Found {len(qualifying_platform_ids)} qualifying platforms")

    # Get all games from qualifying platforms
    plat_ids = list(qualifying_platform_ids.keys())
    if not plat_ids:
        print("No qualifying platforms found. Check platform names.")
        conn.close()
        return

    placeholders = ",".join(["?" for _ in plat_ids])
    c.execute(f"SELECT id, name, platform_id FROM games WHERE platform_id IN ({placeholders})", plat_ids)
    all_games = c.fetchall()
    print(f"Total games on qualifying platforms: {len(all_games)}")

    # Build exclusion regex
    exclusion_pattern = re.compile("|".join(REMASTERED_EXCLUSIONS), re.IGNORECASE)

    qualified_count = 0
    excluded_count = 0

    for game_id, game_name, platform_id in all_games:
        if exclusion_pattern.search(game_name or ""):
            c.execute(
                "INSERT INTO qualification (game_id, qualified, exclusion_reason) VALUES (?, 0, ?)",
                (game_id, "Matches remaster/re-release exclusion list"),
            )
            excluded_count += 1
        else:
            c.execute(
                "INSERT INTO qualification (game_id, qualified) VALUES (?, 1)",
                (game_id,),
            )
            qualified_count += 1

    conn.commit()
    print(f"Qualified: {qualified_count}")
    print(f"Excluded: {excluded_count}")

    # Print summary by platform
    print("\nQualified games by platform:")
    c.execute("""
        SELECT p.name, COUNT(*)
        FROM qualification q
        JOIN games g ON q.game_id = g.id
        JOIN platforms p ON g.platform_id = p.id
        WHERE q.qualified = 1
        GROUP BY p.name
        ORDER BY COUNT(*) DESC
    """)
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()


if __name__ == "__main__":
    import shutil

    if os.path.exists(SOURCE_DB):
        print(f"Copying source database from {SOURCE_DB}...")
        shutil.copy2(SOURCE_DB, DB_PATH)
    elif not os.path.exists(DB_PATH):
        print(f"Error: No source database found at {SOURCE_DB}")
        sys.exit(1)

    print("Building qualification table...")
    build_qualification_table(DB_PATH)
    print("\nDone! Database saved to:", DB_PATH)
