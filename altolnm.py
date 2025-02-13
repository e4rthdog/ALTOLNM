import os
import sqlite3
import csv

def check_csv_file(file_path):
    if not os.path.isfile(file_path):
        return False, f"CSV file does not exist at: {file_path}"
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(1024)
            if not sample.strip():
                return False, "CSV file is empty."
            dialect = csv.Sniffer().sniff(sample)
            if dialect.delimiter != ';':
                return False, f"CSV file does not use ';' as the separator. Detected delimiter: '{dialect.delimiter}'"
            f.seek(0)
            reader = csv.reader(f, dialect)
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
        # Reset is_addon and clear scenery_local_path
        cursor.execute("UPDATE airport SET is_addon = 0, scenery_local_path = '';")
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
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(1024)
            dialect = csv.Sniffer().sniff(sample)
            if dialect.delimiter != ';':
                print(f"CSV file delimiter is not ';' but '{dialect.delimiter}'.")
                return []
            f.seek(0)
            reader = csv.reader(f, dialect)
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
    """
    if not airport_info:
        print("No airport info found in the CSV file to update.")
        return

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        updated_count = 0
        for ident, scenery_path in airport_info:
            cursor.execute(
                "UPDATE airport SET is_addon = 1, scenery_local_path = ? WHERE UPPER(ident) = ?",
                (scenery_path, ident.upper())
            )
            updated_count += cursor.rowcount
        conn.commit()
        print(f"Update complete. Airports Updated: {updated_count}")
    except Exception as e:
        print(f"Error updating the airport table with info: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    default_csv_dir = r"C:\ProgramData\MSFS Addons Linker 2024\Data"
    default_csv_name = "Addons_ICAO.bin"
    default_csv_path = os.path.join(default_csv_dir, default_csv_name)

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
    print("(c) 2025 - Elias Stassinos - v1.1\n\n")

    print("Detected default paths:")
    print(f"MSFS Addons Linker CSV file:      {default_csv_path}")
    print(f"Little NavMap SQLite DB:     {default_sqlite_path}\n")

    use_defaults = input("Do you want to use the default paths? (Y/n): ").strip().lower()
    if use_defaults == "n":
        default_csv_path = input("Enter the full path for the MSFS Addons Linker CSV file: ").strip()
        default_sqlite_path = input("Enter the full path for the Little NavMap database file: ").strip()

    print("\n--- Checking Files ---")
    csv_valid, csv_message = check_csv_file(default_csv_path)
    print(f"MSFS Addons Linker CSV file check: {csv_message}")
    sqlite_valid, sqlite_message = check_sqlite_db(default_sqlite_path)
    print(f"Little NavMap SQLite database check: {sqlite_message}")

    if not (csv_valid and sqlite_valid):
        print("One or more file checks failed. Exiting.")
        return
    
    reset_airport_table(default_sqlite_path)
    
    airport_info = get_airport_info_from_csv(default_csv_path)
    if not airport_info:
        print("No valid airport info found in the MSFS Addons Linker CSV file. Exiting.")
        return
    else:
        print(f"Found {len(airport_info)} airport entries in the MSFS Addons Linker CSV file.")
    
    update_airport_with_info(default_sqlite_path, airport_info)

if __name__ == "__main__":
    main()
    input("\n\nPress Enter to exit...")
