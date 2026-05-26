#!/usr/bin/env python3
"""
mark_defunct_publishers.py

Research pass: marks games from known-defunct publishers in the licensing table.
Sets publisher_status='defunct' and copyright_status='abandonware_claimed' 
for titles whose names match known defunct publisher/developer prefixes.

This is a research heuristic — a human should review before flipping download_allowed.
"""

import sqlite3
import re
from datetime import datetime

DB_PATH = "moral_video_game_library.db"

# Known defunct publishers/developers → their common title prefixes or name fragments
# Sources: MobyGames, Wikipedia "defunct video game companies"
DEFUNCT_PUBLISHERS = {
    # Atari Corp / Atari Games (dissolved 1996-1999)
    "Atari": ["Atari"],
    # 3DO Company (bankrupt 2003)
    "3DO": ["3DO", "Army Men", "Heroes of Might and Magic"],
    # Acclaim Entertainment (bankrupt 2004)
    "Acclaim": ["Acclaim", "NBA Jam", "NFL Quarterback Club", "Turok", "Shadowman", "Burnout"],
    # 3dfx (bankrupt 2000)
    "3dfx": ["3dfx"],
    # Broderbund (dissolved into The Learning Company ~1998)
    "Broderbund": ["Broderbund", "Myst", "Where in the World is Carmen Sandiego", "Print Shop"],
    # Midway Games (bankrupt 2009)
    "Midway": ["Midway", "Mortal Kombat", "Rampage", "Spy Hunter", "Gauntlet", "Joust", "Defender"],
    # Interplay (effectively defunct ~2004, skeleton corp after)
    "Interplay": ["Interplay", "Descent", "Fallout", "Baldur's Gate", "Earthworm Jim", "MDK"],
    # GT Interactive / Infogrames (GT bankrupt 1999)
    "GT Interactive": ["GT Interactive", "Duke Nukem 3D", "Unreal"],
    # 3D Realms (closed 2009, revived shell)
    "3D Realms": ["3D Realms", "Duke Nukem", "Max Payne", "Prey"],
    # Virgin Interactive (dissolved 1998)
    "Virgin": ["Virgin Interactive", "Virgin Games", "Cool Spot", "Global Gladiators"],
    # Ocean Software (dissolved 1996)
    "Ocean": ["Ocean Software", "Ocean"],
    # Psygnosis (dissolved 2012, dormant well before)
    "Psygnosis": ["Psygnosis", "Lemmings", "Wipeout", "Colony Wars"],
    # Hudson Soft (dissolved 2012)
    "Hudson Soft": ["Hudson", "Bomberman", "Bonk", "Adventure Island", "Neutopia"],
    # Sega (not defunct but many dormant IP)
    # Skipping — Sega still active
    # Irem (left game market 2010)
    "Irem": ["Irem", "R-Type", "Moon Patrol"],
    # Data East (bankrupt 2003)
    "Data East": ["Data East", "BurgerTime", "Bad Dudes", "Karate Champ"],
    # Jaleco (left market 2014)
    "Jaleco": ["Jaleco", "Bases Loaded", "Ninja Jajamaru"],
    # Kemco (largely dormant classic lineup)
    "Kemco": ["Kemco"],
    # Taito (absorbed by Square Enix 2005, classic IPs dormant)
    "Taito": ["Taito", "Space Invaders", "Bubble Bobble", "Rainbow Islands", "Arkanoid", "Breakout"],
    # SNK (bankrupt 2001, revived 2003 as Playmore; classic arcade era is effectively abandoned)
    "SNK": ["SNK", "Neo Geo", "King of Fighters", "Metal Slug", "Samurai Shodown"],
    # Atari Lynx / Jaguar homebrew/official
    "Atari Jaguar": ["Jaguar"],
}

def build_pattern(fragments):
    escaped = [re.escape(f) for f in fragments]
    return re.compile("|".join(escaped), re.IGNORECASE)

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.utcnow().isoformat()
    total_marked = 0

    for publisher, fragments in DEFUNCT_PUBLISHERS.items():
        pattern = build_pattern(fragments)
        
        # Find matching game IDs not already marked defunct
        c.execute("SELECT id, name FROM games")
        matches = []
        for row in c.fetchall():
            gid, name = row
            if pattern.search(name):
                matches.append(gid)

        if not matches:
            continue

        for gid in matches:
            # Upsert into licensing
            c.execute("""
                INSERT INTO licensing (game_id, copyright_status, publisher_status, notes, updated_at)
                VALUES (?, 'abandonware_claimed', 'defunct', ?, ?)
                ON CONFLICT(game_id) DO UPDATE SET
                    publisher_status='defunct',
                    copyright_status=CASE WHEN copyright_status='unknown' THEN 'abandonware_claimed' ELSE copyright_status END,
                    notes=excluded.notes,
                    updated_at=excluded.updated_at
            """, (gid, f"Auto-tagged: publisher '{publisher}' known defunct", now))

        total_marked += len(matches)
        print(f"  {publisher}: {len(matches)} titles tagged")

    conn.commit()
    
    # Summary
    c.execute("SELECT COUNT(*) FROM licensing WHERE publisher_status='defunct'")
    defunct_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM licensing WHERE download_allowed=1")
    allowed_count = c.fetchone()[0]
    
    print(f"\nDone. {total_marked} titles tagged this run.")
    print(f"Total defunct-publisher entries in licensing: {defunct_count}")
    print(f"Total download_allowed=1: {allowed_count} (unchanged — manual review required before enabling)")
    
    conn.close()

if __name__ == "__main__":
    main()
