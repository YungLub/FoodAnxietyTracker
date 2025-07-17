import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Food Anxiety Tracker",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data file path
DATA_FILE = "food_anxiety_data.csv"

@st.cache_data
def load_data():
    """Load existing data or create empty DataFrame"""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        columns = [
            'timestamp', 'food_source', 'eating_location', 'anxiety_level',
            'breathing_difficulty', 'swallowing_difficulty', 'scratchy_throat',
            'stomach_pain', 'chest_pain', 'reflux', 'food_eaten', 'concerns',
            'additional_comments', 'took_meds', 'med_types', 'meds_helped'
        ]
        return pd.DataFrame(columns=columns)

def save_data(df):
    """Save data to CSV file"""
    df.to_csv(DATA_FILE, index=False)
    st.cache_data.clear()  # Clear cache to reload fresh data

def severity_to_numeric(severity):
    """Convert severity text to numeric value"""
    mapping = {"None": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
    return mapping.get(severity, 0)

def main():
    st.title("🍽️ Food Anxiety Tracker")
    st.markdown("Track your food anxiety and symptoms over time")
    
    # Load data
    data = load_data()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Data Entry", "Visualizations", "Data Management"])
    
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
            new_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                'med_types': ', '.join(med_types),
                'meds_helped': meds_helped_bool
            }
            
            # Add to dataframe and save
            new_data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(new_data)
            
            st.success("✅ Entry submitted successfully!")
            st.balloons()

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
    
    # Display recent entries
    st.subheader("Recent Entries")
    if not data.empty:
        # Sort by timestamp (most recent first)
        recent_data = data.sort_values('timestamp', ascending=False).head(10)
        st.dataframe(recent_data, use_container_width=True)
    
    # Data export
    st.subheader("Export Data")
    if not data.empty:
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"food_anxiety_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Data deletion
    st.subheader("⚠️ Data Deletion")
    st.warning("This action cannot be undone!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Delete Last Entry", type="secondary"):
            if not data.empty:
                # Remove the last entry (most recent)
                new_data = data.iloc[:-1]
                save_data(new_data)
                st.success("Last entry deleted!")
                st.rerun()
            else:
                st.error("No data to delete!")
    
    with col2:
        if st.button("Delete All Data", type="secondary"):
            if st.session_state.get('confirm_delete', False):
                # Create empty dataframe with same columns
                empty_df = pd.DataFrame(columns=data.columns)
                save_data(empty_df)
                st.success("All data deleted!")
                st.session_state['confirm_delete'] = False
                st.rerun()
            else:
                st.session_state['confirm_delete'] = True
                st.error("Click again to confirm deletion of ALL data!")

if __name__ == "__main__":
    main()