"""
MEKGORO SHOP APP - NO PANDAS VERSION
"""

import streamlit as st
import requests
from datetime import datetime, timedelta

API_URL = st.secrets.get("api_url", "https://httpbin.org/get")

st.set_page_config(page_title="Mekgoro", page_icon="🏪", layout="centered")

if 'shop' not in st.session_state:
    st.session_state.shop = None

def login_page():
    st.title("🏪 Mekgoro")
    
    shop_code = st.text_input("Shop Code")
    if st.button("Open My Shop") and shop_code:
        st.session_state.shop = {"id": shop_code, "name": "My Shop"}
        st.rerun()

def dashboard():
    shop = st.session_state.shop
    st.title(f"🏪 {shop['name']}")
    
    menu = st.radio("Menu", ["📊 Today's Entry", "📈 This Week", "💳 Account"])
    
    if "Today's Entry" in menu:
        with st.form("entry"):
            revenue = st.number_input("Sales (R)", min_value=0)
            expenses = st.number_input("Expenses (R)", min_value=0)
            
            if st.form_submit_button("Submit"):
                profit = revenue - expenses
                st.success(f"Profit: R{profit}")
    
    elif "This Week" in menu:
        st.write("Week view - no pandas needed")
        # Simple list instead of pandas dataframe
    
    else:
        st.write("Account settings")

def main():
    if not st.session_state.shop:
        login_page()
    else:
        dashboard()

if __name__ == "__main__":
    main()
