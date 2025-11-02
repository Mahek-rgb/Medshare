import sqlite3
from datetime import datetime, timedelta
import qrcode
import pandas as pd


def init_db():
    conn = sqlite3.connect("medicine_tracker.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_date TEXT NOT NULL,
            donatable INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()



def add_medicine(name, quantity, expiry_date):
    conn = sqlite3.connect("medicine_tracker.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicines (name, quantity, expiry_date)
        VALUES (?, ?, ?)
    """, (name, quantity, expiry_date))
    conn.commit()
    conn.close()
    print(f"✅ {name} added successfully!")


def fetch_all_medicines():
    conn = sqlite3.connect("medicine_tracker.db")
    df = pd.read_sql_query("SELECT * FROM medicines", conn)
    conn.close()
    return df



def check_near_expiry(days=30):
    conn = sqlite3.connect("medicine_tracker.db")
    cursor = conn.cursor()
    today = datetime.now().date()
    limit = today + timedelta(days=days)

    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    conn.close()

    near_expiry = []
    for med in medicines:
        med_id, name, qty, expiry, donatable = med
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        if today <= expiry_date <= limit:
            near_expiry.append(med)

    return near_expiry



def mark_as_donatable(medicine_id):
    conn = sqlite3.connect("medicine_tracker.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE medicines SET donatable = 1 WHERE id = ?", (medicine_id,))
    conn.commit()

    cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
    med = cursor.fetchone()
    conn.close()

    if med:
        qr_data = f"Medicine: {med[1]}\nQuantity: {med[2]}\nExpiry: {med[3]}"
        qr_img = qrcode.make(qr_data)
        qr_filename = f"QR_{med[1]}_{med[0]}.png"
        qr_img.save(qr_filename)
        print(f"✅ QR code saved as {qr_filename}")



def fetch_donatable_medicines():
    conn = sqlite3.connect("medicine_tracker.db")
    df = pd.read_sql_query("SELECT * FROM medicines WHERE donatable = 1", conn)
    conn.close()
    return df



def export_to_csv():
    df = fetch_all_medicines()
    df.to_csv("medicines_export.csv", index=False)
    print("📦 Data exported to medicines_export.csv successfully!")



if __name__ == "__main__":
    while True:
        print("\n====== Medicine Expiry & Donation Tracker ======")
        print("1. Add new medicine")
        print("2. View all medicines")
        print("3. Check near-expiry medicines")
        print("4. Mark medicine as donatable (and generate QR)")
        print("5. View donatable medicines")
        print("6. Export to CSV")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter medicine name: ")
            quantity = int(input("Enter quantity: "))
            expiry_date = input("Enter expiry date (YYYY-MM-DD): ")
            add_medicine(name, quantity, expiry_date)

        elif choice == "2":
            print(fetch_all_medicines())

        elif choice == "3":
            meds = check_near_expiry()
            if meds:
                print("\nNear-expiry medicines (within 30 days):")
                for med in meds:
                    print(f"➡️  {med[1]} (Expires: {med[3]})")
            else:
                print("No near-expiry medicines found.")

        elif choice == "4":
            med_id = int(input("Enter medicine ID to mark as donatable: "))
            mark_as_donatable(med_id)

        elif choice == "5":
            print(fetch_donatable_medicines())

        elif choice == "6":
            export_to_csv()

        elif choice == "7":
            print("Goodbye 👋")
            break

        else:
            print("Invalid choice. Please try again.")
