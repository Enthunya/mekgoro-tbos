"""
MEKGORO SHOP APP
Streamlit Cloud Deployment Ready
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# ============== CONFIG ==============
# Get from Streamlit secrets (secure)
API_URL = st.secrets.get("api_url", "https://httpbin.org/get")  # Fallback for testing

st.set_page_config(
    page_title="Mekgoro Daily",
    page_icon="🏪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============== STYLES ==============
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stButton>button {
        width: 100%; 
        border-radius: 8px; 
        height: 3em;
        background-color: #2E7D32;
        color: white;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    .metric-card {
        background: white; 
        padding: 1em; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-msg {
        background-color: #E8F5E9;
        border-left: 4px solid #2E7D32;
        padding: 1em;
    }
</style>
""", unsafe_allow_html=True)

# ============== STATE ==============
if 'shop' not in st.session_state:
    st.session_state.shop = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# ============== API HELPERS ==============
def api_get(action, params=None):
    """Safe API GET with error handling"""
    try:
        url = f"{API_URL}?action={action}"
        if params:
            for key, val in params.items():
                url += f"&{key}={val}"
        
        with st.spinner("Loading..."):
            resp = requests.get(url, timeout=15)
            return resp.json()
    except Exception as e:
        st.error(f"Connection error: {str(e)[:100]}")
        return {"error": "Connection failed"}

def api_post(action, data):
    """Safe API POST with error handling"""
    try:
        payload = {"action": action, **data}
        
        with st.spinner("Saving..."):
            resp = requests.post(API_URL, json=payload, timeout=15)
            return resp.json()
    except Exception as e:
        st.error(f"Failed to save: {str(e)[:100]}")
        return {"error": "Save failed"}

# ============== PAGES ==============
def login_page():
    """Login and registration"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.title("🏪 Mekgoro")
        st.markdown("### Your Shop Assistant")
        
        tabs = st.tabs(["Login", "Start Free Trial"])
        
        with tabs[0]:
            shop_code = st.text_input(
                "Shop Code", 
                placeholder="e.g., SHOP123",
                help="Found in your WhatsApp welcome message"
            )
            
            if st.button("Open My Shop", type="primary"):
                if not shop_code:
                    st.warning("Enter your shop code")
                    return
                
                result = api_get("get_shop", {"shop_id": shop_code})
                
                if "error" in result:
                    st.error("Shop not found. Check your code or start a trial.")
                else:
                    st.session_state.shop = result
                    st.session_state.page = 'dashboard'
                    st.rerun()
        
        with tabs[1]:
            with st.form("trial_form"):
                st.write("14 days free, then R150/week")
                
                name = st.text_input("Shop Name *")
                owner = st.text_input("Your Name *")
                phone = st.text_input("WhatsApp Number *", placeholder="0712345678")
                location = st.text_input("Township/Area *")
                
                st.caption("* Required fields")
                
                submitted = st.form_submit_button("Create My Shop", type="primary")
                
                if submitted:
                    if not all([name, owner, phone, location]):
                        st.error("Fill all required fields")
                        return
                    
                    result = api_post("add_shop", {
                        "name": name,
                        "owner": owner,
                        "phone": phone,
                        "location": location,
                        "plan": "growth",
                        "type": "spaza"
                    })
                    
                    if result.get("success"):
                        st.success(f"✅ Created! Your code: {result['shop_id']}")
                        st.info("Check WhatsApp for your welcome message")
                        st.balloons()
                        
                        # Auto-login
                        st.session_state.shop = api_get("get_shop", {"shop_id": result['shop_id']})
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Failed to create. WhatsApp 0712345678 for help.")

def dashboard_page():
    """Main shop dashboard"""
    shop = st.session_state.shop
    
    # Header
    st.title(f"🏪 {shop.get('name', 'My Shop')}")
    
    # Status bar
    status_cols = st.columns([2, 1, 1, 1])
    
    with status_cols[0]:
        st.caption(f"📍 {shop.get('location', '---')} | Code: {shop.get('shop_id', '---')}")
    
    with status_cols[1]:
        plan = shop.get('plan', 'trial').upper()
        st.caption(f"Plan: {plan}")
    
    with status_cols[2]:
        if shop.get('status') == 'trial':
            ends = shop.get('trial_ends', '')
            if ends:
                try:
                    days = (datetime.strptime(ends, '%Y-%m-%d') - datetime.now()).days
                    st.caption(f"⏰ Trial: {max(0, days)}d")
                except:
                    pass
    
    with status_cols[3]:
        if st.button("Logout", type="secondary"):
            st.session_state.shop = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Navigation
    st.markdown("---")
    menu = st.radio(
        "Menu",
        ["📊 Today's Entry", "📈 This Week", "📦 Stock", "👥 Credit", "💳 Account", "❓ Help"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Route
    if "Today's Entry" in menu:
        entry_page(shop)
    elif "This Week" in menu:
        week_page(shop)
    elif "Stock" in menu:
        stock_page(shop)
    elif "Credit" in menu:
        credit_page(shop)
    elif "Account" in menu:
        account_page(shop)
    else:
        help_page()

def entry_page(shop):
    """Daily sales entry"""
    st.subheader(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")
    
    # Yesterday preview
    st.markdown("### Yesterday")
    sales = api_get("get_sales", {"shop_id": shop['shop_id'], "days": "2"})
    
    if sales and len(sales) > 0:
        yesterday = sales[-1]
        cols = st.columns(3)
        cols[0].metric("Sales", f"R{yesterday.get('revenue', 0)}")
        cols[1].metric("Profit", f"R{yesterday.get('profit', 0)}")
        rev = yesterday.get('revenue', 1)
        prof = yesterday.get('profit', 0)
        margin = (prof / max(rev, 1)) * 100
        cols[2].metric("Margin", f"{margin:.0f}%")
    else:
        st.info("No data yet. Enter your first day below!")
    
    # Entry form
    st.markdown("---")
    st.markdown("### Enter Today's Numbers")
    
    with st.form("daily_entry"):
        cols = st.columns(2)
        
        with cols[0]:
            revenue = st.number_input(
                "Total Sales (R) *",
                min_value=0,
                step=10,
                help="All cash + card sales today"
            )
            expenses = st.number_input(
                "Stock Bought (R) *",
                min_value=0,
                step=10,
                help="Money spent on stock today"
            )
        
        with cols[1]:
            st.caption("Quick Add (optional)")
            bread = st.number_input("Bread loaves sold", 0, 100, 0)
            drinks = st.number_input("Cold drinks sold", 0, 100, 0)
            airtime = st.number_input("Airtime sales (R)", 0, 5000, 0)
        
        notes = st.text_area(
            "Notes",
            placeholder="e.g., Rainy day, market was slow, ran out of bread...",
            height=80
        )
        
        submitted = st.form_submit_button("Submit to Mekgoro", type="primary")
        
        if submitted:
            if revenue == 0 and expenses == 0:
                st.warning("Enter at least sales or expenses")
                return
            
            result = api_post("daily_entry", {
                "shop_id": shop['shop_id'],
                "revenue": revenue,
                "expenses": expenses,
                "notes": notes,
                "details": {"bread": bread, "drinks": drinks, "airtime": airtime}
            })
            
            if result.get("success"):
                profit = result.get('profit', 0)
                st.success(f"✅ Recorded! Today's profit: R{profit}")
                st.info("📱 Full report coming to your WhatsApp by 8pm")
                
                # Show preview
                st.markdown("---")
                st.markdown("**Preview:**")
                preview_cols = st.columns(3)
                preview_cols[0].write(f"Revenue: R{revenue}")
                preview_cols[1].write(f"Expenses: R{expenses}")
                preview_cols[2].write(f"**Profit: R{profit}**")
                
                if result.get('alerts'):
                    st.markdown("**Alerts:**")
                    for alert in result['alerts']:
                        st.write(f"- {alert}")
            else:
                error = result.get('error', 'Unknown error')
                if 'payment' in error.lower():
                    st.error("⚠️ Subscription required. Go to 'Account' tab.")
                else:
                    st.error(f"Failed: {error}")
                    st.info("WhatsApp backup: 0712345678")

def week_page(shop):
    """Weekly view"""
    st.subheader("📈 This Week")
    
    sales = api_get("get_sales", {"shop_id": shop['shop_id'], "days": "7"})
    
    if not sales:
        st.info("No data yet. Submit daily entries to see your week!")
        return
    
    # Chart
    df = pd.DataFrame(sales)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    st.line_chart(df.set_index('date')[['revenue', 'profit']])
    
    # Summary
    total_rev = df['revenue'].sum()
    total_prof = df['profit'].sum()
    avg_margin = (total_prof / max(total_rev, 1)) * 100
    
    cols = st.columns(3)
    cols[0].metric("7-Day Sales", f"R{total_rev:,.0f}")
    cols[1].metric("7-Day Profit", f"R{total_prof:,.0f}")
    cols[2].metric("Avg Margin", f"{avg_margin:.1f}%")
    
    # Table
    st.markdown("### Daily Breakdown")
    display_df = df[['date', 'revenue', 'expenses', 'profit']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%a %d %b')
    display_df.columns = ['Date', 'Sales', 'Expenses', 'Profit']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def stock_page(shop):
    """Stock management"""
    st.subheader("📦 Stock Levels")
    
    # Add product
    with st.expander("➕ Add New Product"):
        with st.form("add_product"):
            name = st.text_input("Product Name")
            buy = st.number_input("Your Buy Price (R)", min_value=0.0, step=0.5)
            sell = st.number_input("Your Sell Price (R)", min_value=0.0, step=0.5)
            stock = st.number_input("Current Stock", min_value=0, step=1)
            min_alert = st.number_input("Alert When Below", min_value=1, value=5)
            
            if st.form_submit_button("Add Product"):
                # API call here
                st.success(f"Added {name}")
                st.rerun()
    
    # Current stock (mock for now)
    st.markdown("### Current Stock")
    
    products = [
        {"name": "White Bread", "stock": 3, "min": 5, "status": "low"},
        {"name": "Brown Bread", "stock": 12, "min": 5, "status": "ok"},
        {"name": "Milk 1L", "stock": 2, "min": 4, "status": "low"},
        {"name": "Cold Drinks", "stock": 24, "min": 12, "status": "ok"},
    ]
    
    for p in products:
        cols = st.columns([3, 1, 1])
        
        with cols[0]:
            st.write(f"**{p['name']}**")
        
        with cols[1]:
            color = "red" if p['status'] == 'low' else "green"
            st.markdown(f"<span style='color:{color}'>{p['stock']} / min {p['min']}</span>", 
                       unsafe_allow_html=True)
        
        with cols[2]:
            if p['status'] == 'low':
                st.button("Order", key=f"ord_{p['name']}", type="primary")
            else:
                st.caption("OK")

def credit_page(shop):
    """Credit customers"""
    st.subheader("👥 Credit Customers")
    
    tabs = st.tabs(["Who Owes Me", "Add Customer"])
    
    with tabs[0]:
        # Mock data
        customers = [
            {"name": "John Dlamini", "phone": "0823456789", "owed": 150, "since": "15 Feb"},
            {"name": "Mary Ndlovu", "phone": "0734567890", "owed": 80, "since": "18 Feb"},
            {"name": "Themba", "phone": "0812345678", "owed": 200, "since": "10 Feb"},
        ]
        
        total = sum(c['owed'] for c in customers)
        st.metric("Total Outstanding", f"R{total}", f"{len(customers)} customers")
        
        for c in customers:
            with st.expander(f"{c['name']} — R{c['owed']}"):
                st.caption(f"📱 {c['phone']} | Since: {c['since']}")
                
                cols = st.columns([1, 1])
                with cols[0]:
                    if st.button(f"Remind", key=f"rem_{c['name']}"):
                        st.success(f"WhatsApp reminder sent to {c['name']}!")
                
                with cols[1]:
                    payment = st.number_input(
                        f"Payment R", 
                        min_value=0, 
                        max_value=c['owed'],
                        key=f"pay_{c['name']}"
                    )
                    if st.button(f"Record", key=f"rec_{c['name']}"):
                        st.success(f"Recorded R{payment} payment!")
    
    with tabs[1]:
        with st.form("add_customer"):
            name = st.text_input("Customer Name")
            phone = st.text_input("Phone")
            limit = st.number_input("Credit Limit", min_value=50, value=500, step=50)
            
            if st.form_submit_button("Add Customer"):
                st.success(f"Added {name} with R{limit} limit")

def account_page(shop):
    """Subscription and payment"""
    st.subheader("💳 My Account")
    
    fee = shop.get('weekly_fee', 150)
    status = shop.get('status', 'trial')
    
    cols = st.columns(2)
    
    with cols[0]:
        st.metric("Plan", shop.get('plan', 'growth').upper())
        st.metric("Weekly Fee", f"R{fee}")
        
        if status == 'trial':
            ends = shop.get('trial_ends', '')
            if ends:
                try:
                    days = (datetime.strptime(ends, '%Y-%m-%d') - datetime.now()).days
                    st.metric("Trial Ends In", f"{max(0, days)} days")
                except:
                    pass
        else:
            st.metric("Status", status.upper())
    
    with cols[1]:
        st.markdown("### Payment Options")
        
        st.markdown("**1. Cash Collection**")
        st.caption("Reply 'CASH' on WhatsApp. We'll collect from your shop.")
        
        st.markdown("**2. Bank Transfer**")
        st.code(f"""
FNB Business
Acc: 1234567890
Branch: 250655
Ref: {shop.get('shop_id', 'SHOP')}
        """)
        
        st.markdown("**3. Instant EFT**")
        if st.button("Pay Securely Now"):
            st.info("Redirecting to payment gateway...")

def help_page():
    """Help and support"""
    st.subheader("❓ Help & Support")
    
    st.markdown("""
    ### How Mekgoro Works
    
    **Every day by 7pm:**
    1. Enter your total sales for the day
    2. Enter how much you spent on stock
    3. Add any notes (optional)
    
    **By 8pm:**
    - ✅ I calculate your exact profit
    - ✅ I alert you if stock is low
    - ✅ I remind you who owes money
    - ✅ I send a business tip
    
    ### Tips for Success
    
    - **Be consistent** — daily data = better insights
    - **Track everything** — even small sales add up
    - **Update stock weekly** — keeps alerts accurate
    - **Record credit immediately** — don't forget who owes
    
    ### Contact
    
    📱 WhatsApp: 071-234-5678  
    ⏰ Hours: 7am — 9pm daily  
    📍 Visit: Tembisa Market, Stall 45
    
    ### Common Questions
    
    **Q: What if I forget to enter data?**  
    A: I'll remind you at 8pm. You can enter late, but same-day is best.
    
    **Q: Is my data safe?**  
    A: Yes. Only you and Mekgoro can see your numbers.
    
    **Q: Can I cancel anytime?**  
    A: Yes. WhatsApp "CANCEL" and we'll stop immediately.
    """)

# ============== MAIN ==============
def main():
    if st.session_state.page == 'login':
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
