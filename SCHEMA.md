# Database Schema Reference

## Tables

### `platforms`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| name | TEXT UNIQUE | e.g. `"Nintendo - NES"` |

### `games`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| name | TEXT | Full game title |
| platform_id | INTEGER FK | → `platforms.id` |
| crc | TEXT | CRC32 hash of ROM file |
| md5 | TEXT | MD5 hash |
| sha1 | TEXT | SHA1 hash |

### `qualification`
Tracks whether a game passes the moral-library filter.

| Column | Type | Notes |
|--------|------|-------|
| game_id | INTEGER PK FK | → `games.id` |
| qualified | INTEGER | `1` = passes filter, `0` = excluded |
| exclusion_reason | TEXT | Populated when `qualified = 0` |

### `exclusions`
Pattern-based exclusion rules applied during qualification pass.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| pattern | TEXT | Substring/regex pattern to match against game name |
| reason | TEXT | Human-readable exclusion reason |
| category | TEXT | Broad category (e.g. `"violence"`, `"occult"`) |

### `licensing` *(added 2026-05-26)*
Per-game copyright and download-rights metadata. Drives the abandonware crawler — only titles with `download_allowed = 1` are eligible for automated download.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| game_id | INTEGER PK FK | — | → `games.id` |
| copyright_status | TEXT | `'unknown'` | One of: `commercial`, `public_domain`, `freeware`, `open_source`, `abandonware_claimed`, `unknown` |
| license_name | TEXT | NULL | e.g. `'CC0'`, `'GPL-2.0'`, `'Copyright Nintendo'` |
| publisher_status | TEXT | `'unknown'` | One of: `active`, `defunct`, `acquired`, `unknown` |
| source_url | TEXT | NULL | URL of a known legal/authorized download |
| download_allowed | INTEGER | `0` | `1` = crawler may download; `0` = off-limits |
| copyrighted | INTEGER | `1` | Derived yes/no: `0` = verified copyright-free (public_domain / freeware / open_source); `1` = copyrighted **or not yet verified** (conservative default) |
| notes | TEXT | NULL | Freeform research notes |
| updated_at | TEXT | `datetime('now')` | Last updated timestamp |

#### `copyrighted` derivation (added 2026-09-20)
`copyrighted` is a convenience column maintained by two SQLite triggers
(`licensing_copyrighted_on_insert`, `licensing_copyrighted_on_status_change`),
so any writer gets a consistent value:

```sql
copyrighted = CASE
    WHEN copyright_status IN ('public_domain', 'freeware', 'open_source') THEN 0
    ELSE 1 END
```

Every new row defaults to `copyrighted = 1` until a researcher verifies
otherwise. `unknown` and `abandonware_claimed` both map to `1` — abandonment
is not a legal defense, and unverified is not a green light.

Quick "what is safe to look at" query:

```sql
SELECT g.name, p.name AS platform, l.copyright_status
FROM games g
JOIN platforms p ON p.id = g.platform_id
JOIN licensing l ON l.game_id = g.id
WHERE l.copyrighted = 0;
```

> Note: `copyrighted = 0` only means no copyright barrier was found. The
> separate `download_allowed` flag (human-verified) still gates the crawler.

#### Migration
Tables created before 2026-09-20 lack `copyrighted` (and possibly `notes` /
`updated_at`). `build_licensing_table()` in `build_catalog.py` migrates them
in place without dropping research data:

```sql
ALTER TABLE licensing ADD COLUMN copyrighted INTEGER DEFAULT 1;
UPDATE licensing SET copyrighted = CASE
    WHEN copyright_status IN ('public_domain', 'freeware', 'open_source') THEN 0
    ELSE 1 END;
```

#### `copyright_status` values
| Value | Meaning |
|-------|---------|
| `commercial` | Active commercial copyright; **do not download** |
| `public_domain` | Copyright expired or explicitly released to PD |
| `freeware` | Released as freeware by rights-holder; may download |
| `open_source` | Source + binary released under open license (GPL, MIT, CC0, etc.) |
| `abandonware_claimed` | Publisher defunct and no successor has asserted rights — legally grey, not PD; requires human review before enabling downloads |
| `unknown` | Not yet researched — default for all entries |

#### `publisher_status` values
| Value | Meaning |
|-------|---------|
| `active` | Publisher/rights-holder still operating |
| `defunct` | Company dissolved with no successor identified |
| `acquired` | Company acquired; rights transferred to acquirer |
| `unknown` | Not yet researched |

#### Crawler gate
The automated downloader checks:
```sql
SELECT g.*, l.source_url
FROM games g
JOIN licensing l ON l.game_id = g.id
WHERE l.download_allowed = 1
  AND l.source_url IS NOT NULL;
```
`download_allowed` is only set to `1` by a human or a verified-research script — never auto-set.

### `library_metadata`
Key-value store for library-level metadata (version, build date, etc.).

| Column | Type |
|--------|------|
| key | TEXT PK |
| value | TEXT |
