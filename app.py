import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Database connection
conn = sqlite3.connect('oldagehome.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS residents
             (name TEXT, age INTEGER, gender TEXT, admission_date TEXT, health TEXT, room TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS donors
             (name TEXT, contact TEXT, amount REAL, type TEXT, date TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (category TEXT, amount REAL, date TEXT, description TEXT)''')

conn.commit()

# Login
def login():
    st.title("Dharti no Chedo Vrudhashram - Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["Dashboard", "Add Resident", "Add Donor", "Add Expense"])

    if page == "Add Resident":
        st.header("Add Resident")
        name = st.text_input("Name")
        age = st.number_input("Age", 0, 120)
        gender = st.selectbox("Gender", ["Male", "Female"])
        admission_date = st.date_input("Admission Date")
        health = st.text_input("Health Condition")
        room = st.text_input("Room Number")

        if st.button("Save Resident"):
            c.execute("INSERT INTO residents VALUES (?,?,?,?,?,?)",
                      (name, age, gender, str(admission_date), health, room))
            conn.commit()
            st.success("Resident added successfully!")

    elif page == "Add Donor":
        st.header("Add Donor")
        name = st.text_input("Donor Name")
        contact = st.text_input("Contact")
        amount = st.number_input("Donation Amount", 0.0)
        dtype = st.selectbox("Donation Type", ["Cash", "Online", "Kind"])
        date = st.date_input("Date")

        if st.button("Save Donor"):
            c.execute("INSERT INTO donors VALUES (?,?,?,?,?)",
                      (name, contact, amount, dtype, str(date)))
            conn.commit()
            st.success("Donor added successfully!")

    elif page == "Add Expense":
        st.header("Add Expense")
        category = st.selectbox("Category", ["Food", "Furniture", "Medical", "Daily Needs", "Maintenance"])
        amount = st.number_input("Amount", 0.0)
        date = st.date_input("Date")
        description = st.text_input("Description")

        if st.button("Save Expense"):
            c.execute("INSERT INTO expenses VALUES (?,?,?,?)",
                      (category, amount, str(date), description))
            conn.commit()
            st.success("Expense added successfully!")

    elif page == "Dashboard":
        st.title("Dashboard Overview")

        donors_df = pd.read_sql_query("SELECT * FROM donors", conn)
        expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
        residents_df = pd.read_sql_query("SELECT * FROM residents", conn)

        total_donation = donors_df['amount'].sum() if not donors_df.empty else 0
        total_expense = expenses_df['amount'].sum() if not expenses_df.empty else 0
        balance = total_donation - total_expense

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Residents", len(residents_df))
        col2.metric("Total Donation", f"₹ {total_donation}")
        col3.metric("Balance", f"₹ {balance}")

        if not expenses_df.empty:
            st.subheader("Expense by Category")
            category_sum = expenses_df.groupby("category")["amount"].sum()
            fig, ax = plt.subplots()
            category_sum.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            st.pyplot(fig)
