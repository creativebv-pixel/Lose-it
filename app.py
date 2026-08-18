import datetime
import pandas as pd
import streamlit as st
import google.generativeai as genai

# Configure AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def estimate_calories(food_desc):
    prompt = f"Estimate the calories in: {food_desc}. Provide only the integer number."
    response = model.generate_content(prompt)
    return int(response.text.strip())

st.set_page_config(page_title="AI Calorie Tracker", page_icon="🥗", layout="centered")

# --- Log Entry Sidebar ---
st.sidebar.header("📝 Smart Log")
item_name = st.sidebar.text_input("What did you eat?", placeholder="e.g., 2 eggs and a banana")
entry_type = "Food (+)"

if st.sidebar.button("Calculate & Add"):
    if item_name:
        with st.spinner("AI is calculating..."):
            cals = estimate_calories(item_name)
            # Add to session state
            new_row = pd.DataFrame({"Date": [datetime.date.today()], "Type": [entry_type], "Item": [item_name], "Calories": [cals]})
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_row], ignore_index=True)
            st.sidebar.success(f"Added {cals} kcal!")
    else:
        st.sidebar.error("Please enter a food item.")

# ... (Include your existing Dashboard code from the previous step here
    
