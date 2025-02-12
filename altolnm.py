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
        cursor.execute("UPDATE airport SET is_addon = 0;")
        conn.commit()
        print("All airports are cleared from the addon airport status.")
    except Exception as e:
        print(f"Error resetting the airport table: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def get_airport_idents_from_csv(csv_path):
    idents = []
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
                ident = row[1].strip()
                if ident: 
                    idents.append(ident)
    except Exception as e:
        print(f"Error reading MSFS Addons Linker CSV file for airport idents: {e}")
    return idents

def update_airport_with_idents(sqlite_path, idents):
    if not idents:
        print("No airport idents found in the MSFS Addons Linker CSV file to update.")
        return

    upper_idents = [ident.upper() for ident in idents]
    
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' for _ in upper_idents)
        query = f"UPDATE airport SET is_addon = 1 WHERE UPPER(ident) IN ({placeholders});"
        
        cursor.execute(query, upper_idents)
        conn.commit()
        print(f"Update complete. Airports Added: {cursor.rowcount}")
    except Exception as e:
        print(f"Error updating the airport table with idents: {e}")
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
    print("***Disclaimer:*** I am not responsible for any harm to the files that the utility accesses (the CSV file Of MSFS Addons Linker and the Little NavMap SQLite database for MSFS2024).\n")
    print("NOTE: Little NavMap database must ALREADY be populated with the airports from MSFS 2024!\n")
    print("(c) 2025 - Elias Stassinos\n\n")

    
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
    
    idents = get_airport_idents_from_csv(default_csv_path)
    if not idents:
        print("No valid airport idents found in the MSFS Addons Linker CSV file. Exiting.")
        return
    else:
        print(f"Found {len(idents)} airport idents in the MSFS Addons Linker CSV file.")
    
    update_airport_with_idents(default_sqlite_path, idents)

if __name__ == "__main__":
    main()
    input("\n\nPress Enter to exit...")