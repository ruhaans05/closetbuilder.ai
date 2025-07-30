import streamlit as st
import openai
import json
import ast
import sqlite3
from datetime import datetime

# --- Setup OpenAI Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")  # Replace with your key during local dev

# --- Initialize SQLite ---
conn = sqlite3.connect("closetbuilder_users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS searches (
    username TEXT,
    timestamp TEXT,
    query TEXT,
    result_json TEXT
)
""")
conn.commit()

# --- Auth Logic ---
def login(username, password):
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row and row[0] == password:
        return True
    return False

def register(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def save_search(username, query, results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO searches VALUES (?, ?, ?, ?)", (username, timestamp, query, json.dumps(results)))
    conn.commit()

def get_history(username):
    cursor.execute("SELECT timestamp, query, result_json FROM searches WHERE username = ? ORDER BY timestamp DESC", (username,))
    return cursor.fetchall()

# --- Login UI ---
with st.sidebar:
    st.title("🧾 ClosetBuilder Login")
    login_tab = st.radio("Account", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if login_tab == "Login":
        if st.button("🔐 Login"):
            if login(username, password):
                st.session_state.username = username
                st.success("Logged in!")
            else:
                st.error("Invalid credentials.")
    else:
        if st.button("🆕 Register"):
            if register(username, password):
                st.success("Account created! You can log in now.")
            else:
                st.error("Username already exists.")

if "username" not in st.session_state:
    st.warning("Please login to use ClosetBuilder.AI.")
    st.stop()

# --- Dropdown Options ---
shirt_sizes = ["", "XS", "S", "M", "L", "XL"]
genders = ["", "Male", "Female", "Unisex", "Kids"]
channels = ["", "Online", "In Person", "Both"]
countries = sorted([
    "Afghanistan", "Albania", "Algeria", "Argentina", "Australia", "Austria", "Bangladesh", "Belgium", "Brazil", "Canada",
    "China", "Colombia", "Denmark", "Egypt", "Finland", "France", "Germany", "Greece", "Hungary", "India", "Indonesia", "Iran",
    "Iraq", "Ireland", "Israel", "Italy", "Japan", "Kenya", "Malaysia", "Mexico", "Nepal", "Netherlands", "New Zealand", "Nigeria",
    "Norway", "Pakistan", "Philippines", "Poland", "Portugal", "Qatar", "Russia", "Saudi Arabia", "Singapore", "South Africa",
    "South Korea", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Thailand", "Turkey", "UAE", "UK", "USA", "Vietnam", "Zimbabwe"
])

currency_options = {
    "USD": {"symbol": "$", "rate": 1.1},
    "EUR": {"symbol": "€", "rate": 1.0},
    "CAD": {"symbol": "C$", "rate": 1.47},
    "AUD": {"symbol": "A$", "rate": 1.63},
    "GBP": {"symbol": "£", "rate": 0.85},
    "INR": {"symbol": "₹", "rate": 90.0}
}

st.title("🎩 ClosetBuilder.AI -- Design your wardrobe in seconds!")

# --- Currency Selection ---
currency = st.selectbox("Currency", list(currency_options.keys()), index=0)
symbol = currency_options[currency]["symbol"]
rate = currency_options[currency]["rate"]
max_local_price = int(2000 * rate)

col3, col4 = st.columns(2)
with col3:
    min_price = st.slider(f"Min Price ({symbol})", 0, max_local_price, 0, step=10)
with col4:
    max_price = st.slider(f"Max Price ({symbol})", 0, max_local_price, max_local_price, step=10)

# --- Search Form ---
with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        shirt_size = st.selectbox("Shirt Size", shirt_sizes)
        gender = st.selectbox("Gender", genders)
    with col2:
        channel = st.selectbox("Shopping Preference", channels)
        country = st.selectbox("Country", countries)

    query = st.text_input("What are you looking for?", placeholder="e.g. black hoodie")
    submitted = st.form_submit_button("🔍 Find Clothes")

# --- Search Execution ---
if submitted:
    with st.spinner("Designing your wardrobe..."):
        prompt = f"""
You're a fashion shopping assistant. Based on this user's preferences:

- Shirt Size: {shirt_size}
- Gender: {gender}
- Country: {country}
- Shopping Preference: {channel}
- Currency: {currency}
- Price Range: {symbol}{min_price} to {symbol}{max_price}
- Query: {query}

Find 20 real clothing items available online that match these filters.
Each result must include:
- name
- size
- price (in {currency})
- link (real product link)

Return the result as strict valid JSON like:
[
  {{
    "name": "...",
    "size": "...",
    "price": ...,
    "link": "..."
  }},
  ...
]
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            raw = response.choices[0].message.content

            try:
                results = json.loads(raw)
            except json.JSONDecodeError:
                try:
                    results = ast.literal_eval(raw)
                except Exception:
                    st.error("❌ ClosetBuilder.AI is down right now. There are developers working on this behind the scenes. Please come back later.")
                    st.code(raw)
                    st.stop()

            st.success("✅ Found results!")
            save_search(st.session_state.username, query, results)

            for item in results:
                st.markdown(
                    f"**[{item['name']}]({item['link']})**  \nSize: {item['size']} — {symbol}{item['price']}",
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")

# --- History Tab ---
st.markdown("---")
with st.expander("🕓 View My Past Searches"):
    history = get_history(st.session_state.username)
    if not history:
        st.info("No search history yet.")
    else:
        for ts, q, res in history:
            st.markdown(f"**{ts} — Query:** _{q}_")
            try:
                items = json.loads(res)
                for item in items[:3]:
                    st.markdown(f"- [{item['name']}]({item['link']}) — {symbol}{item['price']}")
                st.markdown("...")
            except:
                st.text("(Could not display results)")
