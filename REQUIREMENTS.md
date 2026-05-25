# Emulator & Software Requirements

To run the titles cataloged in the Moral Video Game Library, the following
emulators are required. All are free and open-source. On macOS they install via
[Homebrew](https://brew.sh):

```bash
brew install --cask retroarch openemu dolphin pcsx2 flycast mgba-app
```

## Platform → Emulator Mapping

| Platform(s) | Recommended Emulator | RetroArch Core |
|---|---|---|
| NES, SNES, Game Boy / Color / Advance, Virtual Boy, Satellaview | RetroArch / OpenEmu | `mesen`, `snes9x`, `mgba` |
| Nintendo 64 / 64DD | RetroArch | `mupen64plus_next`, `parallel_n64` |
| Nintendo DS / DSi | RetroArch | `melonds`, `desmume` |
| GameCube, Wii | **Dolphin** | — |
| Sega Master System, Genesis/Mega Drive, Game Gear, SG-1000, 32X, Sega CD | RetroArch / OpenEmu | `genesis_plus_gx`, `picodrive` |
| Sega Saturn | RetroArch | `mednafen_saturn`, `yabause` |
| Sega Dreamcast | **Flycast** | `flycast` |
| Sony PlayStation (PS1) | RetroArch / DuckStation | `swanstation`, `beetle_psx` |
| Sony PlayStation 2 | **PCSX2** | — |
| Sony PSP | RetroArch / PPSSPP | `ppsspp` |
| Atari 2600 / 5200 / 7800 / Lynx / Jaguar / ST | RetroArch | `stella`, `a5200`, `prosystem`, `handy` |
| NEC PC Engine / TurboGrafx-16 / SuperGrafx / CD / PC-FX | RetroArch | `mednafen_pce`, `mednafen_pcfx` |
| SNK Neo Geo / Pocket / CD | RetroArch | `fbneo`, `mednafen_ngp` |
| Bandai WonderSwan / Color | RetroArch | `mednafen_wswan` |
| ColecoVision, Intellivision, Odyssey2, Vectrex, Videopac+ | RetroArch | `bluemsx`, `freeintv`, `o2em`, `vecx` |
| Commodore 64 / Amiga, Amstrad CPC, ZX Spectrum, MSX/MSX2 | RetroArch | `vice`, `puae`, `cap32`, `fuse`, `bluemsx` |
| DOS | RetroArch (DOSBox-Pure) / DOSBox-X | `dosbox_pure` |
| 3DO | RetroArch | `opera` |

## Installation Status (Daniel's Mac, verified 2026-05-25)

Already installed via Homebrew cask:
`retroarch`, `openemu`, `dolphin`, `pcsx2`, `flycast`, `mgba-app`. ✅

After installing RetroArch, download cores from within the app:
**Online Updater → Core Downloader**, or install the full set:
RetroArch menu → *Online Updater → Update Installed Cores*.

## BIOS Files

Some systems require original BIOS files (not distributed here): PS1/PS2 (`scph*`),
Saturn, Dreamcast (`dc_boot.bin`), Neo Geo (`neogeo.zip`), PC-FX, Sega CD.
Provide your own legally-obtained BIOS dumps. Place them in RetroArch's `system/`
folder.

## Building the Catalog Manifest

The catalog database (`moral_video_game_library.db`, ~150k qualified titles) is
built from the [libretro-database](https://github.com/libretro/libretro-database)
DAT files:

```bash
# 1. clone the source DAT data
git clone --depth 1 https://github.com/libretro/libretro-database.git
# 2. build the base catalog (names + CRC/MD5/SHA1 hashes)
python3 build_base_catalog.py
# 3. apply Moral Library qualification filtering
python3 build_catalog.py
```
