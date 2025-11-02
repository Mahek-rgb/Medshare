from datetime import datetime, timedelta
from db import get_connection


def add_test_medicine():
    conn = get_connection()
    cursor = conn.cursor()
    test_name = "TestMedicine"
    test_quantity = 1
    test_expiry = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM medicines WHERE name=?", (test_name,))
    if cursor.fetchone():
        print("Test medicine already exists.\n")
        conn.close()
        return

    cursor.execute("INSERT INTO medicines (name, quantity, expiry_date) VALUES (?, ?, ?)",
                   (test_name, test_quantity, test_expiry))
    conn.commit()
    conn.close()
    print(f"✅ Test medicine added: {test_name}, expires on {test_expiry}\n")
