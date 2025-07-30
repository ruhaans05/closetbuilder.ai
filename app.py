import streamlit as st
import openai
import json
import ast
import sqlite3
from datetime import datetime

# --- OpenAI Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

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

# --- Currency Setup ---
currency_options = {
    "USD": {"symbol": "$", "rate": 1.1},
    "EUR": {"symbol": "€", "rate": 1.0},
    "CAD": {"symbol": "C$", "rate": 1.47},
    "AUD": {"symbol": "A$", "rate": 1.63},
    "GBP": {"symbol": "£", "rate": 0.85},
    "INR": {"symbol": "₹", "rate": 90.0}
}

# --- SQLite DB Setup ---
def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            username TEXT,
            timestamp TEXT,
            query TEXT,
            min_price INT,
            max_price INT,
            currency TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_history(username, query, min_price, max_price, currency):
    conn = sqlite3.connect("users.db")
    conn.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)", (
        username, datetime.now().isoformat(), query, min_price, max_price, currency
    ))
    conn.commit()
    conn.close()

def get_history(username):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT timestamp, query, min_price, max_price, currency FROM history WHERE username=? ORDER BY timestamp DESC", (username,))
    rows = cur.fetchall()
    conn.close()
    return rows

# --- Auth helpers ---
def login(username, password):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] == password

def register(username, password):
    conn = sqlite3.connect("users.db")
    try:
        conn.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# --- Init DB ---
init_db()

# --- Sidebar Auth (Optional) ---
st.sidebar.markdown("### 👤 Optional Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_status = False

if st.sidebar.button("Login"):
    if login(username, password):
        st.session_state.username = username
        st.sidebar.success("Logged in!")
    else:
        st.sidebar.error("Invalid credentials")

if st.sidebar.button("Register"):
    if register(username, password):
        st.session_state.username = username
        st.sidebar.success("Account created!")
    else:
        st.sidebar.error("Username already taken")

if 'username' in st.session_state:
    st.sidebar.markdown(f"✅ Logged in as `{st.session_state.username}`")
    with st.sidebar.expander("📜 Your History"):
        for ts, q, minp, maxp, cur in get_history(st.session_state.username):
            st.sidebar.markdown(f"**{ts.split('T')[0]}**: {q} ({cur}{minp}–{maxp})")

# --- Main Title ---
st.title("🎩 ClosetBuilder.AI — Design your wardrobe in seconds!")

# --- Currency Selection ---
currency = st.selectbox("Currency", list(currency_options.keys()), index=0)
symbol = currency_options[currency]["symbol"]
rate = currency_options[currency]["rate"]
max_local_price = int(2000 * rate)

# --- Price sliders ---
col3, col4 = st.columns(2)
with col3:
    min_price = st.slider(f"Min Price ({symbol})", 0, max_local_price, 0, step=10)
with col4:
    max_price = st.slider(f"Max Price ({symbol})", 0, max_local_price, max_local_price, step=10)

# --- Form inputs ---
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

# --- Submit to OpenAI ---
if submitted:
    if query.strip() == "":
        st.error("Please enter a valid search query.")
        st.stop()

    if 'username' in st.session_state:
        save_history(st.session_state.username, query, min_price, max_price, currency)

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
                    st.error("❌ ClosetBuilder.AI is down. Try again later.")
                    st.code(raw)
                    st.stop()

            st.success("✅ Found results!")

            for item in results:
                st.markdown(
                    f"**[{item['name']}]({item['link']})**  \nSize: {item['size']} — {symbol}{item['price']}",
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")
