# ALTOLNM

## Overview

Little NavMap is not able to mark airports as addons because the procedure for building the database of MSFS 2024 has changed. As a result, there is no indication in Little NavMap if an airport is an addon or not.

This utility addresses this issue by using the database of the popular MSFS Addons Linker 2024 edition to read the airports and mark them as addons in Little NavMap. This is particularly useful for planning flights between addon airports and for other planning tasks in Little NavMap.

**Note**: Both developers of Little NavMap and MSFS Addons Linker have given their permission for this utility to be distributed.

---

## Features

- Reads the MSFS Addons Linker database to identify addon airports.
- Updates the Little NavMap SQLite database to flag airports as addons.
- Does not insert or delete any records from the databases—only updates specific fields.

---

## Installation

1. Download the utility and unzip it to a desired location.
2. Run the executable file from the console.

### MSFS Addons Linker Database
- **Default Location**: `C:\ProgramData\MSFS Addons Linker 2024\Data`
- **File Name**: `Addons_ICAO.bin`

**Important**: If the file is not found in the above folder, run the duplicate check from the MSFS Addons Linker menu: `Tools -> Scan ICAO / Check for duplicates`. This will create the file.

The file is a simple CSV text file with two fields:
1. The local file path of the scenery.
2. The ICAO code of the airport.

Any file that meets this format can be used to flag airports as addons in Little NavMap.

### Little NavMap Database
- **Default Location**: `%APPDATA%\ABarthel`
- **File Name**: `little_navmap_msfs24.sqlite`

The utility reads the CSV file and updates the `airport` table in the SQLite database. It updates two fields:
1. `ident`
2. `scenery_local_path`

Before updating, it clears these fields to ensure consistency.

**_IMPORTANT_**: The utility does not insert or delete any records from either database. It only performs the operations described above.

---

## Usage

1. Ensure the MSFS Addons Linker database (`Addons_ICAO.bin`) and the Little NavMap database (`little_navmap_msfs24.sqlite`) are accessible.
2. Run the utility from the console.
3. Follow the on-screen instructions to confirm or override default file paths.

---

## Build Executable

To build the executable from the source code, use the following command:

```bash
pyinstaller.exe --onefile .\altolnm.py --icon=icon.ico
```

---

## Troubleshooting

- **File Not Found**: Ensure the database files are in their default locations or provide the correct paths when prompted.
- **Permission Issues**: Run the utility with administrative privileges if you encounter access issues.

---

## License

This utility is distributed under the terms specified in the `LICENSE` file. Please refer to it for more details.
