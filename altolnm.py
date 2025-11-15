import os
import sys
import sqlite3
import csv
import subprocess
import colorama
from colorama import Fore, Style

# Initialize Colorama for consistent ANSI support across platforms
colorama.init()

def detect_encoding(file_path, encodings=["utf-8", "cp1252", "latin-1", "iso-8859-1", "iso-8859-2", "windows-1250"]):
    """
    Attempts to read the entire file using each encoding in the list.
    Returns the first encoding that successfully decodes the whole file.
    Raises an Exception if none work.
    """
    for enc in encodings:
        try:
            with open(file_path, 'r', newline='', encoding=enc) as f:
                f.read()  # Read the entire file to ensure full decoding
            return enc
        except Exception:
            continue
    raise Exception("Unable to decode file with provided encodings.")

def check_csv_file(file_path):
    if not os.path.isfile(file_path):
        return False, f"CSV file does not exist at: {file_path}"
    
    try:
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', newline='', encoding=encoding) as f:
            content = f.read()
            if not content.strip():
                return False, "CSV file is empty."
            f.seek(0)
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                pass
        return True, "MSFS Addons Linker CSV file is valid"
    except Exception as e:
        return False, f"Error processing CSV file: {e}"

def check_sqlite_db(file_path):
    if not os.path.isfile(file_path):
        return False, f"Little NavMap SQLite database does not exist at: {file_path}"
    
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='airport'")
        result = cursor.fetchone()
        if result is None:
            return False, "Little NavMap SQLite database does not contain a table named 'airport'."
        return True, "Little NavMap SQLite database is valid and contains the 'airport' table."
    except Exception as e:
        return False, f"Error accessing Little NavMap SQLite database: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass

def reset_airport_table(sqlite_path):
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE airport SET is_addon = 0, scenery_local_path = '' WHERE bgl_filename = 'ALTOLNM';")
        conn.commit()
        print("All airports are cleared from the addon airport status and scenery paths have been reset.")
    except Exception as e:
        print(f"Error resetting the airport table: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def get_airport_info_from_csv(csv_path):
    """
    Reads the CSV file and returns a list of tuples:
    (airport ident, scenery_local_path)
    """
    airport_info = []
    try:
        encoding = detect_encoding(csv_path)
        with open(csv_path, 'r', newline='', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) < 2:
                    continue
                scenery_local_path = row[0].strip()  # First field (scenery path)
                ident = row[1].strip()               # Second field (airport ident)
                if ident:
                    airport_info.append((ident, scenery_local_path))
    except Exception as e:
        print(f"Error reading CSV file for airport info: {e}")
    return airport_info

def update_airport_with_info(sqlite_path, airport_info):
    """
    Updates the airport table setting is_addon = 1 and storing
    the scenery_local_path from the CSV for each airport matching the ident.
    This update process prints its status on one line (overwriting previous output)
    and clears the entire line before printing. Colorama is used for coloring the output.
    """
    if not airport_info:
        print("No airport info found in the CSV file to update.")
        return

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        updated_count = 0
        not_updated = []
        total_records = len(airport_info)
        print(f"Starting update process for {total_records} airport records...", end="")
        
        for index, (ident, scenery_path) in enumerate(airport_info, start=1):
            cursor.execute(
                "UPDATE airport SET is_addon = 1, scenery_local_path = ? , bgl_filename = 'ALTOLNM' WHERE UPPER(ident) = ? ",
                (scenery_path, ident.upper())
            )
            if cursor.rowcount == 0:
                not_updated.append(ident)
                status = f"[{index}/{total_records}] '{ident}': {Fore.RED}not found{Style.RESET_ALL}."
            else:
                updated_count += cursor.rowcount
                status = f"[{index}/{total_records}] '{ident}': {Fore.GREEN}updated ({cursor.rowcount}){Style.RESET_ALL}."
            
            # Clear the entire line and print the status.
            sys.stdout.write("\r\033[K" + status)
            sys.stdout.flush()
        
        conn.commit()
        # Final newline and summary.
        print("\n\nUpdate complete.")
        print(f"Total airports updated: {updated_count}.")
        if not_updated:
            print("Airports not updated (no matching ident found): " + ", ".join(not_updated))
        else:
            print("All airports from CSV have been updated successfully.")
    except Exception as e:
        print(f"\nError updating the airport table with info: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    default_csv_dir = r"C:\ProgramData\MSFS Addons Linker 2024\Data"
    default_csv_name = "Addons_ICAO.bin"
    default_csv_path = os.path.join(default_csv_dir, default_csv_name)
    
    # Optional custom CSV file that should be treated as part of the same dataset
    custom_csv_name = "Addons_ICAO_Custom.bin"
    custom_csv_path = os.path.join(default_csv_dir, custom_csv_name)

    appdata = os.environ.get('APPDATA')
    if appdata:
        default_sqlite_dir = os.path.join(appdata, "ABarthel", "little_navmap_db")
    else:
        default_sqlite_dir = ""
    default_sqlite_name = "little_navmap_msfs24.sqlite"
    default_sqlite_path = os.path.join(default_sqlite_dir, default_sqlite_name)

    print("ALTOLNM - A free utility to flag your MSFS Addons Linker airports as addon airports to Little NavMap MSFS 2024 database.\n")
    print("***Disclaimer:*** I am not responsible for any harm to the files that the utility accesses (the CSV file of MSFS Addons Linker and the Little NavMap SQLite database for MSFS2024).\n")
    print("NOTE: Little NavMap database must ALREADY be populated with the airports from MSFS 2024!\n")
    print("(c) 2025 - Elias Stassinos - v1.40\n\n")

    print("Detected default paths:")
    print(f"MSFS Addons Linker CSV file:           {default_csv_path}")
    print(f"Little NavMap SQLite DB:               {default_sqlite_path}\n")

    use_defaults = input("Do you want to use the default paths? (Y/n): ").strip().lower()
    if use_defaults == "n":
        user_csv = input(f"Enter the full path for the MSFS Addons Linker CSV file (default: {default_csv_path}): ").strip()
        if user_csv:
            default_csv_path = user_csv

        # Custom CSV always resides in the same directory as the main CSV;
        # its name is fixed and it is treated as optional.
        custom_csv_path = os.path.join(os.path.dirname(default_csv_path), custom_csv_name)

        user_sqlite = input(f"Enter the full path for the Little NavMap database file (default: {default_sqlite_path}): ").strip()
        if user_sqlite:
            default_sqlite_path = user_sqlite

    print("\n--- Checking Files ---")
    csv_valid, csv_message = check_csv_file(default_csv_path)
    print(f"MSFS Addons Linker CSV file check: {csv_message}")

    # Optional custom CSV: only check if the file exists
    custom_csv_valid = False
    if os.path.isfile(custom_csv_path):
        custom_csv_valid, _ = check_csv_file(custom_csv_path)
        print("Optional Custom CSV file: found and will be included.")
    else:
        print("Optional Custom CSV file: not found.")

    sqlite_valid, sqlite_message = check_sqlite_db(default_sqlite_path)
    print(f"Little NavMap SQLite database check: {sqlite_message}")

    if not (csv_valid and sqlite_valid):
        print("One or more required file checks failed. Exiting.")
        return
    
    reset_airport_table(default_sqlite_path)
    
    # Read main CSV (required)
    airport_info = get_airport_info_from_csv(default_csv_path)

    # If custom CSV is valid, read and append its entries
    if custom_csv_valid:
        custom_airport_info = get_airport_info_from_csv(custom_csv_path)
        airport_info.extend(custom_airport_info)
        print(f"Loaded {len(custom_airport_info)} additional entries from custom CSV file.")

    if not airport_info:
        print("No valid airport info found in the MSFS Addons Linker CSV files. Exiting.")
        return
    else:
        print(f"Total airport entries found (default + custom): {len(airport_info)}.\n")
    
    update_airport_with_info(default_sqlite_path, airport_info)

if __name__ == "__main__":
    main()
    input("\n\nPress Enter to exit...")
