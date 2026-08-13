# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ALTOLNM is a single-file Python CLI utility that flags MSFS Addons Linker airports as "addon" airports in the Little NavMap MSFS 2024 database. Little NavMap can no longer detect addons automatically because the MSFS 2024 database build procedure changed; this tool bridges that gap by reading the Addons Linker export and writing the addon flag into Little NavMap's SQLite DB.

All logic lives in `altolnm.py`. There are no external modules, tests, or packages — it is intentionally a one-file program.

A parallel `.github/copilot-instructions.md` covers the same project for GitHub Copilot; keep the two in sync when conventions change.

## Commands

Run from source (interactive; prompts on stdin):
```bash
python altolnm.py
```

Install the only third-party dependency:
```bash
pip install colorama
```

Build the distributable Windows executable:
```bash
pyinstaller --onefile altolnm.py --icon=icon.ico
```
This is the canonical build command (README + copilot instructions). Output lands in `dist/altolnm.exe`. Note: `.gitignore` excludes `build/`, `dist/`, and `*.spec`, so the `altolnm.spec` file present in a working tree is **not** version-controlled and won't exist in a fresh clone — don't rely on it. If regenerating a spec, the shipped build uses `console=True`, UPX on, and `icon.ico`.

## Data flow / architecture

The program is a straight pipeline in `main()`:

1. **Resolve paths** — CSV default `C:\ProgramData\MSFS Addons Linker 2024\Data\Addons_ICAO.bin`; SQLite default `%APPDATA%\ABarthel\little_navmap_db\little_navmap_msfs24.sqlite`. User can override interactively.
2. **Validate** — `check_csv_file` (encoding-sniffs, must be non-empty, `;`-delimited) and `check_sqlite_db` (must contain an `airport` table).
3. **Reset** — `reset_airport_table` clears prior runs by matching `bgl_filename = 'ALTOLNM'` and setting `is_addon = 0`, `scenery_local_path = ''`.
4. **Read** — `get_airport_info_from_csv` returns `(ident, scenery_local_path)` tuples. Optional `Addons_ICAO_Custom.bin` (same dir, fixed name) is appended if present.
5. **Write** — `update_airport_with_info` sets `is_addon = 1`, `scenery_local_path`, and `bgl_filename = 'ALTOLNM'` for each matching `ident`.

### Load-bearing conventions

- **`bgl_filename = 'ALTOLNM'` is the ownership marker.** It is how the tool distinguishes rows it touched from real MSFS data. The reset step relies on it to avoid clobbering unrelated airports. Do not repurpose this sentinel.
- **The tool only UPDATEs — never INSERT or DELETE.** This is a hard product guarantee stated in the README and disclaimer. Preserve it.
- **The "CSV" is a `.bin` file** but is plain text, `;`-delimited: field 0 = scenery local path, field 1 = airport ICAO ident.
- **Encoding is auto-detected** via `detect_encoding` (tries utf-8, cp1252, latin-1, iso-8859-x, windows-1250). Reuse it for any new file reads rather than hardcoding an encoding.
- **Progress output uses `\r\033[K`** (carriage return + ANSI clear-line) with `colorama.init()` for cross-platform ANSI. Keep colorama initialized if adding colored output.

## PyInstaller / stdin caveat

`main()` uses `input()` for interactive prompts and there is a trailing `input("Press Enter to exit...")` at the bottom of the file. When the exe is launched without an attached stdin (e.g. built windowed, or launched by another process), `input()` raises `EOFError`. The spec ships with `console=True`, so double-clicking works. The exit prompt is already guarded with `try/except EOFError`, so a stdin-less launch exits cleanly. The interactive path prompts inside `main()` are **not** yet guarded — guard them the same way if a windowed/stdin-less build is ever shipped.

## Version string

The user-facing version is a hardcoded print in `main()` (currently `v1.50`). Bump it there when releasing.
