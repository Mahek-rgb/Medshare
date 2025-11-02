import csv
from datetime import datetime
from db import get_connection
import qrcode


def generate_donatable_qr(name, quantity, expiry_date):

    data = f"Medicine Name: {name}\nQuantity: {quantity}\nExpiry Date: {expiry_date}\nDonatable: Yes"

    img = qrcode.make(data)
    filename = f"{name}_donatable_qr.png"
    img.save(filename)
    print(f"✅ QR code generated: {filename}\n")


def add_medicine():
    conn = get_connection()
    cursor = conn.cursor()

    name = input("Enter medicine name: ")
    quantity = int(input("Enter quantity: "))
    expiry_date = input("Enter expiry date (YYYY-MM-DD): ")

    cursor.execute(
        "INSERT INTO medicines (name, quantity, expiry_date) VALUES (?, ?, ?)",
        (name, quantity, expiry_date)
    )

    conn.commit()
    conn.close()
    print("✅ Medicine added successfully!\n")


def view_all_medicines():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, quantity, expiry_date, donatable FROM medicines")
    rows = cursor.fetchall()

    if not rows:
        print("No medicines found.\n")
    else:
        print("\nAll Medicines:")
        for row in rows:
            donatable = "Yes" if row[4] else "No"
            print(f"{row[0]}. {row[1]} - Qty: {row[2]} - Expiry: {row[3]} - Donatable: {donatable}")
    print()

    conn.close()


def check_near_expiry():
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.today().date()
    cursor.execute("SELECT name, expiry_date FROM medicines")
    rows = cursor.fetchall()

    print("\nMedicines expiring soon (within 30 days):")
    found = False
    for name, expiry_date in rows:
        exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        if 0 <= (exp_date - today).days <= 30:
            print(f"⚠️ {name} expires on {expiry_date}")
            found = True
    if not found:
        print("No medicines are near expiry.\n")
    print()

    conn.close()


def mark_donatable():
    view_all_medicines()
    medicine_id = int(input("Enter the medicine ID to mark as donatable: "))

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("UPDATE medicines SET donatable=1 WHERE id=?", (medicine_id,))


    cursor.execute("SELECT name, quantity, expiry_date FROM medicines WHERE id=?", (medicine_id,))
    med = cursor.fetchone()

    conn.commit()
    conn.close()

    print("✅ Medicine marked as donatable.\n")


    if med:
        name, quantity, expiry_date = med
        generate_donatable_qr(name, quantity, expiry_date)


def view_donatable_medicines():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, quantity, expiry_date FROM medicines WHERE donatable=1")
    rows = cursor.fetchall()

    print("\nDonatable Medicines:")
    if not rows:
        print("No donatable medicines found.\n")
    else:
        for row in rows:
            print(f"- {row[0]} (Qty: {row[1]}) - Expiry: {row[2]}")
    print()

    conn.close()


def search_medicine():
    query = input("Enter medicine name to search (partial names allowed): ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, expiry_date, donatable FROM medicines WHERE name LIKE ?", (f"%{query}%",))
    rows = cursor.fetchall()
    if not rows:
        print("\nNo medicines found matching that name.\n")
    else:
        print("\nSearch Results:")
        for r in rows:
            donatable = "Yes" if r[4] else "No"
            print(f"{r[0]}. {r[1]} - Qty: {r[2]} - Expiry: {r[3]} - Donatable: {donatable}")
        print()
    conn.close()


def generate_report():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("SELECT COUNT(*) FROM medicines")
    total = cursor.fetchone()[0]


    cursor.execute("SELECT COUNT(*) FROM medicines WHERE donatable=1")
    donatable = cursor.fetchone()[0]

    today = datetime.today().date()
    cursor.execute("SELECT expiry_date FROM medicines")
    rows = cursor.fetchall()
    expired = 0
    near_expiry = 0
    for (expiry_date,) in rows:
        try:
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            if days_left < 0:
                expired += 1
            elif days_left <= 30:
                near_expiry += 1
        except Exception:
            pass

    print("\n========= Inventory Report =========")
    print(f"Total medicines      : {total}")
    print(f"Donatable medicines  : {donatable}")
    print(f"Expired medicines    : {expired}")
    print(f"Near-expiry (<=30d)  : {near_expiry}")
    print("====================================\n")

    conn.close()



def export_to_csv(filename="medicines_backup.csv"):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, expiry_date, donatable FROM medicines")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No data to export.\n")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Quantity", "Expiry Date", "Donatable"])
        for r in rows:
            donatable = "Yes" if r[4] else "No"
            writer.writerow([r[0], r[1], r[2], r[3], donatable])

    print(f"✅ Data exported to {filename}\n")
