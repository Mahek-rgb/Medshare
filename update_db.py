import sqlite3

conn = sqlite3.connect("medicine_data.db")
cursor = conn.cursor()

# Add new columns if they don’t exist
try:
    cursor.execute("ALTER TABLE medicines ADD COLUMN category TEXT;")
    print("✅ 'category' column added successfully!")
except:
    print("ℹ️ 'category' column already exists.")

try:
    cursor.execute("ALTER TABLE medicines ADD COLUMN description TEXT;")
    print("✅ 'description' column added successfully!")
except:
    print("ℹ️ 'description' column already exists.")

conn.commit()
conn.close()
