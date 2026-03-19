# Moral Video Game Library

A curated SQLite catalog of classic video games that meet specific ethical and legal criteria for personal archival and preservation.

## About

Created by **Daniel Bates** ([BatesAI LLC](https://github.com/danielalanbates)), this project catalogs retro video games that are no longer commercially supported, have not been remastered, and are at least 10 years past their last publication date. The goal is to preserve gaming history for personal use, education, and research.

## Qualification Criteria

A game is included in this library only if it meets ALL of the following conditions:

1. **No Longer Supported** — The original developer or publisher no longer actively sells, updates, or supports the title.
2. **Not Remastered or Re-Released** — The game has not been remastered, remade, ported to modern platforms, or re-released on any digital storefront (e.g., Nintendo Switch Online, PlayStation Store, Steam, GOG).
3. **At Least 10 Years Old** — A minimum of 10 years has passed since the game's last official publication or re-release date.
4. **From a Defunct or Inactive Studio** — Priority is given to titles from studios that have closed or ceased game development entirely.

## Ethical Position

These games represent abandoned cultural works. They cannot be purchased through any legitimate channel. No developer or publisher profits from their sale. This library exists purely for preservation, personal use, education, and historical research — not for commercial redistribution.

This project does NOT include:
- Games currently sold on any platform
- Games that have received remasters, remakes, or HD re-releases
- Games from active studios that may re-release them
- Any commercially available ROMs or ISOs

## Database Schema

The SQLite database (`moral_video_game_library.db`) contains:

- **platforms** — Console and system definitions
- **games** — Full ROM catalog with hashes (CRC, MD5, SHA1) for verification
- **qualification** — Filtering metadata: support status, remaster status, last publication year, studio status
- **guidebooks** — Links to game guides, manuals, and walkthroughs from public sources
- **exclusions** — Games explicitly excluded with reasons (remastered, still sold, etc.)

## Platforms Covered

NES, SNES, Sega Genesis, Sega Master System, Game Boy, Game Boy Color, Game Boy Advance, Nintendo 64, Nintendo DS, PlayStation, PlayStation 2, Sega Saturn, Sega Dreamcast, Atari 2600, Atari 7800, TurboGrafx-16, Neo Geo, and more.

## Usage

```bash
# Browse qualified games
sqlite3 moral_video_game_library.db "SELECT g.name, p.name as platform FROM games g JOIN platforms p ON g.platform_id = p.id JOIN qualification q ON q.game_id = g.id WHERE q.qualified = 1 ORDER BY p.name, g.name;"

# Count qualified games by platform
sqlite3 moral_video_game_library.db "SELECT p.name, COUNT(*) FROM games g JOIN platforms p ON g.platform_id = p.id JOIN qualification q ON q.game_id = g.id WHERE q.qualified = 1 GROUP BY p.name ORDER BY COUNT(*) DESC;"

# Search for a specific game
sqlite3 moral_video_game_library.db "SELECT g.name, p.name, q.qualified, q.exclusion_reason FROM games g JOIN platforms p ON g.platform_id = p.id LEFT JOIN qualification q ON q.game_id = g.id WHERE g.name LIKE '%mario%';"
```

## Building from Source

```bash
pip install -r requirements.txt
python build_catalog.py
```

This clones the [libretro-database](https://github.com/libretro/libretro-database) and converts DAT files into the SQLite catalog, then applies qualification filtering.

## Contributing

Contributions welcome! You can help by:
- Identifying games that have been remastered (should be excluded)
- Adding last-known publication dates
- Flagging active studios whose games should be removed
- Adding guidebook sources

Please open an issue or PR with evidence (links to storefronts, remaster announcements, etc.).

## License

MIT License — see [LICENSE](LICENSE).

## Attribution

Created by Daniel Bates, BatesAI LLC. Catalog data sourced from the [libretro-database](https://github.com/libretro/libretro-database) project (MIT License).

A full fork of libretro-database is maintained at [danielalanbates/libretro-database](https://github.com/danielalanbates/libretro-database) for source data preservation.
