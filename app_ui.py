import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect("medicine_data.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        quantity INTEGER,
        expiry_date TEXT,
        category TEXT,
        description TEXT,
        donatable INTEGER DEFAULT 0
    )''')
    conn.commit()
    return conn

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(page_title="💊 MedShare Dashboard", layout="wide")
st.title("💊 MedShare - Medicine Expiry & Donation Tracker")
st.markdown("---")

menu = [
    "Add New Medicine",
    "View All Medicines",
    "Check Near-Expiry Medicines",
    "Mark Medicine as Donatable (QR Code)",
    "View Donatable Medicines",
    "Delete Medicine",
    "Export Data to CSV"
]
choice = st.sidebar.selectbox("📂 Select an Option", menu)

# -------------------------------
# 1️⃣ Add New Medicine
# -------------------------------
if choice == "Add New Medicine":
    st.subheader("➕ Add a New Medicine")

    name = st.text_input("Medicine Name")
    category = st.selectbox("Category", ["Tablet", "Syrup", "Capsule", "Injection", "Other"])
    description = st.text_area("Description (Optional)")
    qty = st.number_input("Quantity", min_value=1, step=1)
    expiry = st.date_input("Expiry Date")

    if st.button("Add Medicine"):
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO medicines (name, quantity, expiry_date, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (name, qty, expiry.strftime('%Y-%m-%d'), category, description))
        conn.commit()
        conn.close()
        st.success(f"✅ '{name}' added successfully!")


# -------------------------------
# 2️⃣ View All Medicines
# -------------------------------
elif choice == "View All Medicines":
    st.subheader("📋 All Medicines in Database")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM medicines", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No medicines found.")


# -------------------------------
# 3️⃣ Check Near-Expiry Medicines
# -------------------------------
elif choice == "Check Near-Expiry Medicines":
    st.subheader("⚠️ Medicines Near Expiry (Within 30 Days)")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM medicines", conn)
    conn.close()

    if not df.empty:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"])
        today = datetime.today()
        df["days_left"] = (df["expiry_date"] - today).dt.days
        near_expiry = df[df["days_left"] <= 30]

        if not near_expiry.empty:
            st.dataframe(near_expiry)
        else:
            st.info("🎉 No near-expiry medicines found.")
    else:
        st.warning("No medicines in database.")


# -------------------------------
# 4️⃣ Mark Medicine as Donatable (QR Code)
# -------------------------------
elif choice == "Mark Medicine as Donatable (QR Code)":
    st.subheader("🤝 Mark Medicine as Donatable & Generate QR Code")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM medicines WHERE donatable = 0", conn)

    if not df.empty:
        selected_med = st.selectbox("Select Medicine to Donate", df["name"].tolist())

        if st.button("Mark as Donatable & Generate QR Code"):
            med_row = df[df["name"] == selected_med].iloc[0]
            conn.execute("UPDATE medicines SET donatable = 1 WHERE name = ?", (selected_med,))
            conn.commit()

            # Generate QR Code with all details
            qr_data = (
                f"💊 Medicine: {med_row['name']}\n"
                f"📦 Quantity: {med_row['quantity']}\n"
                f"🗓 Expiry: {med_row['expiry_date']}\n"
                f"🏷 Category: {med_row['category']}\n"
                f"📝 Description: {med_row['description'] or 'N/A'}"
            )
            # Generate smaller QR Code (200x200)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5,  # smaller box size = smaller image
                border=2
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Convert to BytesIO for Streamlit display
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            st.image(buf.getvalue(), caption=f"QR Code for {selected_med}", width=200)

            st.success(f"✅ '{selected_med}' marked as donatable and QR generated!")

        conn.close()
    else:
        st.info("No medicines available to mark as donatable.")


# -------------------------------
# 5️⃣ View Donatable Medicines
# -------------------------------
elif choice == "View Donatable Medicines":
    st.subheader("🎁 Donatable Medicines")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM medicines WHERE donatable = 1", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No donatable medicines yet.")


# -------------------------------
# 6️⃣ 🗑 Delete Medicine
# -------------------------------
elif choice == "Delete Medicine":
    st.subheader("🗑 Delete Medicine")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM medicines", conn)

    if not df.empty:
        selected_med = st.selectbox("Select Medicine to Delete", df["name"].tolist())

        if st.button("Delete Selected Medicine"):
            conn.execute("DELETE FROM medicines WHERE name = ?", (selected_med,))
            conn.commit()
            conn.close()
            st.success(f"❌ '{selected_med}' deleted successfully!")
    else:
        st.info("No medicines to delete.")


# -------------------------------
# 7️⃣ Export Data to CSV
# -------------------------------
elif choice == "Export Data to CSV":
    st.subheader("⬇️ Export Medicine Data")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM medicines", conn)
    conn.close()

    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Medicines Data as CSV",
            data=csv,
            file_name="medicine_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available to export.")
