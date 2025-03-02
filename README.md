# ALTOLNM

Little NavMap is not able to mark the airport as an addon because the procedure of building the database of MSFS 2024 changed.

Therefore there is no indication in Little NavMap if an airport is an addon or not.

I am using this feature a lot since i need to plan my next flight between airports that are addons and not default and also i need LNM for all other planning tasks.

The uitility uses the database of popular MSFS Addons Linker 2024 edition to read the airports and then mark them as addons in Little NavMap.

NOTE: Both developers of Little NavMap and MSFS Addons Linker gave their permission for this utility to be distributed.

Installation & Details:

The utility is a simple console .exe file. Just unzip somewhere and run it.

MSFS Addons Linker database usual location is:

`C:\ProgramData\MSFS Addons Linker 2024\Data`

And the file name is:

`Addons_ICAO.bin`

**IMPORTANT!!! If you can't find the file in the AL folder above, run the duplicate check from the Tools -> Scan ICAO / Check for duplicates, and the file will be created.**

This file although a database is a simple CSV text file with 2 fields. The first is the local file path of the scenery and the second one is the ICAO of the airport.

This means that any file that meets this format can be used to flag the airports as addon in LNM.

The Little NavMap database is an sqlite one and the location is usually at:

`%APPDATA%\ABarthel`

The database file is named:

`little_navmap_msfs24.sqlite`

The utility reads the CSV file and updates the airport table in the sqlite database. It updates 2 fields, the ident and the local file path field. Before doing so , it clears these 2 fields.

**_IMPORTANT_** The utility DOES NOT insert or delete any record from either databases, only the operations described above.

## Build executable

Issue the command: `pyinstaller.exe --onefile .\altolnm.py --icon=icon.ico`
