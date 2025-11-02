import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Medicine Database Viewer", layout="wide")


DB_PATH = "medicines.db"

def fetch_data(query):

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


st.title("💊 Medicine Database Dashboard")
st.write("View all medicine records stored in your database")

st.subheader("📦 All Medicines")
all_data = fetch_data("SELECT * FROM medicines")

if not all_data.empty:
    st.dataframe(all_data, use_container_width=True)
else:
    st.info("No medicines found in the database.")

st.subheader("⏳ Medicines Near Expiry")
near_expiry = fetch_data("SELECT * FROM medicines WHERE julianday(expiry_date) - julianday('now') <= 30")

if not near_expiry.empty:
    st.dataframe(near_expiry, use_container_width=True)
else:
    st.info("No medicines expiring within 30 days.")

st.subheader("🤝 Donatable Medicines")
donatable = fetch_data("SELECT * FROM medicines WHERE donatable = 'Yes'")

if not donatable.empty:
    st.dataframe(donatable, use_container_width=True)
else:
    st.info("No donatable medicines currently available.")


st.subheader("📥 Download Data")
if not all_data.empty:
    csv = all_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download All Medicines as CSV",
        data=csv,
        file_name="all_medicines.csv",
        mime="text/csv"
    )
