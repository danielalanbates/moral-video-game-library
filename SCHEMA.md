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
| notes | TEXT | NULL | Freeform research notes |
| updated_at | TEXT | `datetime('now')` | Last updated timestamp |

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
