#!/usr/bin/env python3
"""Build retro_catalog.db (platforms + games + hashes) from libretro DAT files."""
import sqlite3, os, re, glob

BASE = "/Volumes/x10/Video Games/Games & ROMs/libretro-database"
DAT_DIRS = [
    os.path.join(BASE, "dat"),
    os.path.join(BASE, "metadat", "no-intro"),
    os.path.join(BASE, "metadat", "redump"),
]
OUT_DB  = "/Volumes/x10/Video Games/Games & ROMs/retro_catalog.db"

game_re = re.compile(r'game\s*\(\s*name\s+"((?:[^"\\]|\\.)*)"', re.MULTILINE)
rom_re  = re.compile(r'rom\s*\(([^)]*)\)')

def field(blob, key):
    m = re.search(rf'\b{key}\s+([0-9a-fA-F]+)', blob)
    return m.group(1).lower() if m else None

def main():
    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)
    conn = sqlite3.connect(OUT_DB)
    c = conn.cursor()
    c.execute("CREATE TABLE platforms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    c.execute("""CREATE TABLE games (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,
                 platform_id INTEGER, crc TEXT, md5 TEXT, sha1 TEXT,
                 FOREIGN KEY(platform_id) REFERENCES platforms(id))""")
    total = 0
    dats = []
    for d in DAT_DIRS:
        dats += sorted(glob.glob(os.path.join(d, "*.dat")))
    for dat in dats:
        plat = os.path.splitext(os.path.basename(dat))[0]
        try:
            text = open(dat, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        c.execute("INSERT OR IGNORE INTO platforms (name) VALUES (?)", (plat,))
        pid = c.execute("SELECT id FROM platforms WHERE name=?", (plat,)).fetchone()[0]
        # split into game blocks
        blocks = re.split(r'\ngame\s*\(', text)
        n = 0
        for blk in blocks[1:]:
            nm = re.search(r'^\s*name\s+"((?:[^"\\]|\\.)*)"', blk, re.MULTILINE)
            if not nm:
                continue
            name = nm.group(1)
            rm = rom_re.search(blk)
            crc = md5 = sha1 = None
            if rm:
                r = rm.group(1)
                crc, md5, sha1 = field(r,'crc'), field(r,'md5'), field(r,'sha1')
            c.execute("INSERT INTO games (name, platform_id, crc, md5, sha1) VALUES (?,?,?,?,?)",
                      (name, pid, crc, md5, sha1))
            n += 1
        total += n
    conn.commit()
    print(f"Platforms: {c.execute('SELECT COUNT(*) FROM platforms').fetchone()[0]}")
    print(f"Total games: {total}")
    conn.close()

if __name__ == "__main__":
    main()
