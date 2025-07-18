import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from supabase import create_client, Client
import json

# Page configuration
st.set_page_config(
    page_title="Food Anxiety Tracker",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("❌ Supabase credentials not configured. Please set up secrets in Streamlit Cloud.")
        st.stop()

supabase: Client = init_supabase()

def check_authentication():
    """Handle user authentication"""
    
    # Check if user is already logged in
    if "user" in st.session_state and st.session_state.user:
        return True
    
    # Authentication UI
    st.markdown("# 🍽️ Food Anxiety Tracker")
    st.markdown("Please sign in to access your personal tracking data.")
    
    # Create tabs for Sign In and Sign Up
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Sign In")
        with st.form("signin_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            signin_submitted = st.form_submit_button("Sign In", type="primary")
            
            if signin_submitted:
                if email and password:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        if response.user:
                            st.session_state.user = response.user
                            st.session_state.session = response.session
                            st.success("✅ Successfully signed in!")
                            st.rerun()
                        else:
                            st.error("❌ Sign in failed. Please check your credentials.")
                    except Exception as e:
                        st.error(f"❌ Sign in error: {str(e)}")
                else:
                    st.error("Please enter both email and password.")
    
    with tab2:
        st.subheader("Create Account")
        with st.form("signup_form"):
            new_email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_submitted = st.form_submit_button("Create Account", type="secondary")
            
            if signup_submitted:
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            try:
                                response = supabase.auth.sign_up({
                                    "email": new_email,
                                    "password": new_password
                                })
                                if response.user:
                                    st.success("✅ Account created! Please check your email to verify your account, then sign in.")
                                else:
                                    st.error("❌ Account creation failed.")
                            except Exception as e:
                                st.error(f"❌ Signup error: {str(e)}")
                        else:
                            st.error("Password must be at least 6 characters long.")
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.error("Please fill in all fields.")
    
    return False

def load_user_data():
    """Load data for the current user from Supabase"""
    try:
        user_id = st.session_state.user.id
        response = supabase.table('food_anxiety_entries').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert created_at to timestamp for compatibility
            df['timestamp'] = df['created_at']
            return df
        else:
            # Return empty DataFrame with expected columns
            columns = [
                'id', 'user_id', 'created_at', 'timestamp', 'food_source', 'eating_location', 
                'anxiety_level', 'breathing_difficulty', 'swallowing_difficulty', 
                'scratchy_throat', 'stomach_pain', 'chest_pain', 'reflux', 
                'food_eaten', 'concerns', 'additional_comments', 'took_meds', 
                'med_types', 'meds_helped'
            ]
            return pd.DataFrame(columns=columns)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def save_entry(entry_data):
    """Save a new entry to Supabase"""
    try:
        user_id = st.session_state.user.id
        entry_data['user_id'] = user_id
        
        response = supabase.table('food_anxiety_entries').insert(entry_data).execute()
        
        if response.data:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error saving entry: {str(e)}")
        return False

def delete_entry(entry_id):
    """Delete an entry from Supabase"""
    try:
        response = supabase.table('food_anxiety_entries').delete().eq('id', entry_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting entry: {str(e)}")
        return False

def severity_to_numeric(severity):
    """Convert severity text to numeric value"""
    mapping = {"None": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
    return mapping.get(severity, 0)

def main():
    # Check authentication first
    if not check_authentication():
        st.stop()
    
    # Main app interface
    st.title("🍽️ Food Anxiety Tracker")
    st.markdown(f"Welcome back, {st.session_state.user.email}!")
    
    # Load user data
    data = load_user_data()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Data Entry", "Visualizations", "Data Management"])
    
    # Add user info and logout in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Logged in as:**\n{st.session_state.user.email}")
    
    if st.sidebar.button("🔓 Logout"):
        try:
            supabase.auth.sign_out()
            st.session_state.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Logout error: {str(e)}")
    
    # Page routing
    if page == "Data Entry":
        data_entry_page(data)
    elif page == "Visualizations":
        visualizations_page(data)
    elif page == "Data Management":
        data_management_page(data)

def data_entry_page(data):
    st.header("📝 Data Entry")
    
    with st.form("anxiety_form"):
        st.subheader("Food Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            food_source = st.radio(
                "Are you eating food made at home or from somewhere else?",
                ["Home", "Out"]
            )
        
        with col2:
            eating_location = st.radio(
                "Are you eating at home or out?",
                ["Home", "Out"]
            )
        
        st.subheader("Anxiety Level")
        anxiety_level = st.slider("Rank your current anxiety level", 0, 10, 0)
        
        st.subheader("Physical Symptoms")
        severity_options = ["None", "Mild", "Moderate", "Severe"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            breathing_difficulty = st.selectbox("Difficulty catching breath?", severity_options)
            swallowing_difficulty = st.selectbox("Difficulty swallowing?", severity_options)
            scratchy_throat = st.selectbox("Scratchy Throat?", severity_options)
        
        with col2:
            stomach_pain = st.selectbox("Stomach pain?", severity_options)
            chest_pain = st.selectbox("Chest pain?", severity_options)
            reflux = st.selectbox("Reflux?", severity_options)
        
        st.subheader("Food Details")
        food_eaten = st.text_area("What did you eat? Where was it from?", height=100)
        concerns = st.text_area("What are your concerns with what you are eating?", height=100)
        additional_comments = st.text_area("Additional Comments:", height=100)
        
        st.subheader("Medication")
        took_meds = st.radio("Did you take meds to manage symptoms?", ["No", "Yes"])
        took_meds_bool = took_meds == "Yes"
        
        med_types = []
        if took_meds_bool:
            st.write("If so, which ones did you take?")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.checkbox("Allergy"):
                    med_types.append("Allergy")
            with col2:
                if st.checkbox("Anxiety"):
                    med_types.append("Anxiety")
            with col3:
                if st.checkbox("Other"):
                    med_types.append("Other")
            
            meds_helped = st.radio("Did they help?", ["No", "Yes"])
            meds_helped_bool = meds_helped == "Yes"
        else:
            meds_helped_bool = False
        
        # Submit button
        submitted = st.form_submit_button("Submit Entry", type="primary")
        
        if submitted:
            # Create new entry
            entry_data = {
                'food_source': food_source,
                'eating_location': eating_location,
                'anxiety_level': anxiety_level,
                'breathing_difficulty': breathing_difficulty,
                'swallowing_difficulty': swallowing_difficulty,
                'scratchy_throat': scratchy_throat,
                'stomach_pain': stomach_pain,
                'chest_pain': chest_pain,
                'reflux': reflux,
                'food_eaten': food_eaten,
                'concerns': concerns,
                'additional_comments': additional_comments,
                'took_meds': took_meds_bool,
                'med_types': ', '.join(med_types) if med_types else '',
                'meds_helped': meds_helped_bool
            }
            
            if save_entry(entry_data):
                st.success("✅ Entry submitted successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to save entry. Please try again.")

def visualizations_page(data):
    st.header("📊 Visualizations")
    
    if data.empty:
        st.warning("No data available. Please enter some data first.")
        return
    
    # Convert timestamp to datetime
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Visualization selector
    viz_type = st.selectbox(
        "Select Visualization Type:",
        ["Anxiety Over Time", "Symptom Severity", "Food Source Analysis", "Medication Effectiveness"]
    )
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if viz_type == "Anxiety Over Time":
        if len(data) > 1:
            ax.plot(data['timestamp'], data['anxiety_level'], marker='o', linewidth=2, markersize=8)
            ax.set_title('Anxiety Level Over Time', fontsize=16, fontweight='bold')
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Anxiety Level (0-10)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 10)
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'Need at least 2 data points for time series', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
    
    elif viz_type == "Symptom Severity":
        symptoms = ['breathing_difficulty', 'swallowing_difficulty', 'scratchy_throat', 
                   'stomach_pain', 'chest_pain', 'reflux']
        
        severity_data = {}
        for symptom in symptoms:
            if symptom in data.columns:
                numeric_values = data[symptom].apply(severity_to_numeric)
                severity_data[symptom.replace('_', ' ').title()] = numeric_values.mean()
        
        if severity_data:
            bars = ax.bar(severity_data.keys(), severity_data.values(), 
                         color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd'])
            ax.set_title('Average Symptom Severity', fontsize=16, fontweight='bold')
            ax.set_ylabel('Average Severity (0-3)', fontsize=12)
            ax.set_ylim(0, 3)
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{height:.1f}', ha='center', va='bottom')
    
    elif viz_type == "Food Source Analysis":
        if 'food_source' in data.columns and 'anxiety_level' in data.columns:
            food_anxiety = data.groupby('food_source')['anxiety_level'].mean()
            bars = ax.bar(food_anxiety.index, food_anxiety.values, 
                         color=['#ff6b6b', '#4ecdc4'])
            ax.set_title('Average Anxiety by Food Source', fontsize=16, fontweight='bold')
            ax.set_ylabel('Average Anxiety Level', fontsize=12)
            ax.set_ylim(0, 10)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height:.1f}', ha='center', va='bottom')
    
    elif viz_type == "Medication Effectiveness":
        if 'took_meds' in data.columns and 'meds_helped' in data.columns:
            med_data = data[data['took_meds'] == True]
            if not med_data.empty:
                helped_count = med_data['meds_helped'].sum()
                total_count = len(med_data)
                effectiveness = helped_count / total_count * 100
                
                bars = ax.bar(['Helped', 'Did Not Help'], 
                             [effectiveness, 100 - effectiveness],
                             color=['#4ecdc4', '#ff6b6b'])
                ax.set_title('Medication Effectiveness', fontsize=16, fontweight='bold')
                ax.set_ylabel('Percentage', fontsize=12)
                ax.set_ylim(0, 100)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{height:.1f}%', ha='center', va='bottom')
            else:
                ax.text(0.5, 0.5, 'No medication data available', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Display summary statistics
    st.subheader("📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Entries", len(data))
    
    with col2:
        if not data.empty and 'anxiety_level' in data.columns:
            avg_anxiety = data['anxiety_level'].mean()
            st.metric("Average Anxiety", f"{avg_anxiety:.1f}")
    
    with col3:
        if not data.empty and 'took_meds' in data.columns:
            med_usage = (data['took_meds'] == True).sum()
            st.metric("Times Meds Taken", med_usage)
    
    with col4:
        if not data.empty and 'food_source' in data.columns:
            home_percentage = (data['food_source'] == 'Home').mean() * 100
            st.metric("Home Food %", f"{home_percentage:.1f}%")

def data_management_page(data):
    st.header("🗂️ Data Management")
    
    if data.empty:
        st.info("No data available.")
        return
    
    st.subheader("Data Overview")
    st.write(f"Total entries: {len(data)}")
    
    # Display recent entries with delete option
    st.subheader("Your Entries")
    if not data.empty and 'id' in data.columns:
        # Sort by timestamp (most recent first)
        if 'created_at' in data.columns:
            display_data = data.sort_values('created_at', ascending=False)
        else:
            display_data = data
        
        # Show entries with delete buttons
        for idx, row in display_data.iterrows():
            # Create timestamp display
            if 'created_at' in row and pd.notna(row['created_at']):
                timestamp_str = pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')
            else:
                timestamp_str = "Unknown time"
            
            # Create anxiety display
            anxiety_str = f"{row['anxiety_level']}/10" if 'anxiety_level' in row and pd.notna(row['anxiety_level']) else "N/A"
            
            with st.expander(f"Entry from {timestamp_str} - Anxiety: {anxiety_str}"):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    if 'food_source' in row:
                        st.write(f"**Food Source:** {row['food_source']}")
                    if 'eating_location' in row:
                        st.write(f"**Eating Location:** {row['eating_location']}")
                    if 'anxiety_level' in row:
                        st.write(f"**Anxiety Level:** {row['anxiety_level']}/10")
                    if 'food_eaten' in row and row['food_eaten']:
                        st.write(f"**Food Eaten:** {row['food_eaten']}")
                    if 'concerns' in row and row['concerns']:
                        st.write(f"**Concerns:** {row['concerns']}")
                
                with col2:
                    if 'id' in row and pd.notna(row['id']):
                        if st.button(f"🗑️ Delete", key=f"delete_{row['id']}"):
                            if delete_entry(row['id']):
                                st.success("Entry deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete entry")
                    else:
                        st.write("Cannot delete - no ID")
    elif not data.empty:
        st.warning("Data exists but missing ID column. This might be old CSV data.")
    
    # Data export
    st.subheader("Export Data")
    if not data.empty:
        # Prepare data for export (remove internal fields)
        export_data = data.drop(columns=['id', 'user_id'], errors='ignore')
        csv = export_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Your Data (CSV)",
            data=csv,
            file_name=f"food_anxiety_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()