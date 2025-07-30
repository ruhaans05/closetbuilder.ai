import streamlit as st
import openai
import json
import ast

# --- CONFIG ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")  # or hardcode: "sk-..."

shirt_sizes = ["", "XS", "S", "M", "L", "XL"]
genders = ["", "Male", "Female", "Unisex", "Kids"]
channels = ["", "Online", "In Person", "Both"]

countries = sorted([
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Australia", "Austria", "Bangladesh", "Belgium", "Brazil", "Canada",
    "China", "Colombia", "Denmark", "Egypt", "Finland", "France", "Germany", "Greece", "Hungary", "India", "Indonesia", "Iran",
    "Iraq", "Ireland", "Israel", "Italy", "Japan", "Kenya", "Malaysia", "Mexico", "Nepal", "Netherlands", "New Zealand", "Nigeria",
    "Norway", "Pakistan", "Philippines", "Poland", "Portugal", "Qatar", "Russia", "Saudi Arabia", "Singapore", "South Africa",
    "South Korea", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Thailand", "Turkey", "UAE", "UK", "USA", "Vietnam", "Zimbabwe"
])

# --- UI ---
st.title("🧠 AI Clothing Finder")

with st.form("search_form"):
    col1, col2 = st.columns(2)

    with col1:
        shirt_size = st.selectbox("Shirt Size", shirt_sizes)
        gender = st.selectbox("Gender", genders)
        min_price = st.slider("Min Price ($)", 0, 5000, 0, step=10)

    with col2:
        channel = st.selectbox("Shopping Preference", channels)
        country = st.selectbox("Country", countries)
        max_price = st.slider("Max Price ($)", 0, 5000, 5000, step=10)

    query = st.text_input("What are you looking for?", placeholder="e.g. black hoodie")

    submitted = st.form_submit_button("🔍 Find Clothes")

# --- BACKEND ---
if submitted:
    with st.spinner("Thinking..."):
        prompt = f"""
You're a fashion shopping assistant. Based on this user's preferences:

- Shirt Size: {shirt_size}
- Gender: {gender}
- Country: {country}
- Shopping Preference: {channel}
- Price Range: ${min_price} to ${max_price}
- Query: {query}

Find 20 clothing items available online that match these filters.
Each item must include:
- name
- size
- price
- link (real product link)

If fewer than 20 are found, fill in the rest with similar items. Return as JSON:
[{{"name": "...", "size": "...", "price": ..., "link": "..."}}...]
"""

        try:
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            raw = res.choices[0].message.content

            # --- Robust parsing ---
            try:
                results = json.loads(raw)
            except json.JSONDecodeError:
                try:
                    results = ast.literal_eval(raw)
                except Exception as e:
                    st.error("❌ Failed to parse AI response.")
                    st.code(raw)
                    st.stop()

            st.success("✅ Found results!")

            for item in results:
                st.markdown(
                    f"**[{item['name']}]({item['link']})**  \nSize: {item['size']} — ${item['price']}",
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")
