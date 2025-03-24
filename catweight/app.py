"""
Main Streamlit application for cat weight tracking.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import os
import base64
from db import CatWeightDatabase

# Constants
CATS = ["Mittens", "Cheddar", "Lola"]
CAT_COLORS = {
    "Mittens": "#FF9671",  # Orange
    "Cheddar": "#FFC75F",  # Yellow
    "Lola": "#D65DB1"      # Pink
}
CAT_EMOJIS = {
    "Mittens": "🐱",
    "Cheddar": "🐈",
    "Lola": "😺"
}

# Function to handle the cat image for Cheddar
def get_cat_icon_html(cat_name):
    """Get HTML to display the cat icon (emoji or image)"""
    # Use image files for all cats
    image_name = f"{cat_name.lower()}.png"
    
    # Display the image using HTML for better styling control
    return f"""
    <div class="emoji-container cat-image-container">
        <img src="data:image/png;base64,{get_image_base64(image_name)}" 
             class="cat-image" alt="{cat_name}">
    </div>
    """

def get_image_base64(image_name):
    """Convert an image to base64 string for embedding in HTML"""
    image_path = os.path.join(os.path.dirname(__file__), "images", image_name)
    if not os.path.exists(image_path):
        # Return empty string if image doesn't exist
        return ""
    
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Cat Food Tracker",
        page_icon="🐱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
        }
        # .cat-card {
        #     background-color: rgba(49, 51, 63, 0.7);
        #     border-radius: 10px;
        #     padding: 1.5rem;
        #     margin-bottom: 1rem;
        #     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        #     border-left: 5px solid #1E88E5;
        # }
        .cat-header {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        .stat-card {
            background-color: rgba(49, 51, 63, 0.7);
            border-radius: 5px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .data-card {
            background-color: rgba(49, 51, 63, 0.7);
            border-radius: 8px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin-top: 1rem;
        }
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #ccc;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 0.5rem;
        }
        .cat-emoji {
            font-size: 3rem;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        # .input-section {
        #     background-color: rgba(49, 51, 63, 0.7);
        #     border-radius: 10px;
        #     padding: 1rem;
        #     margin-bottom: 2rem;
        #     box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        #     border: 1px solid rgba(250, 250, 250, 0.1);
        # }
        .weight-input-label {
            font-weight: bold;
            margin-bottom: 0.25rem;
        }
        .cat-name-header {
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .emoji-container {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        /* Cat image styling */
        .cat-image-container {
            text-align: center;
            margin-bottom: 0.8rem;
        }
        .cat-image {
            width: 90px;
            height: 90px;
            border-radius: 0;
            object-fit: contain;
            display: inline-block;
            box-shadow: none;
            border: none;
            transition: none;
        }
        .cat-image:hover {
            transform: none;
            box-shadow: none;
        }
        
        /* Override default Streamlit tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: rgba(49, 51, 63, 0.3);
            border-radius: 8px 8px 0 0;
            padding: 0 10px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: transparent;
            border-radius: 8px 8px 0 0;
            color: white;
            padding: 0 20px;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.1);
            font-weight: bold;
            color: #4287f5;
        }
        
        /* Override Streamlit number input styling */
        input[type="number"] {
            border: 1px solid rgba(250, 250, 250, 0.2) !important;
            background-color: rgba(49, 51, 63, 0.5) !important;
            border-radius: 5px !important;
            color: white !important;
        }
        
        .stButton > button {
            border-radius: 5px;
            background-color: #4287f5;
            color: white;
            border: none;
            padding: 4px 15px;
            font-weight: bold;
        }
        
        .stButton > button:hover {
            background-color: #2d6ecf;
        }
        
        /* Make the tab content section transparent */
        .stTabs [data-baseweb="tab-panel"] {
            background-color: transparent;
            padding: 15px 5px;
        }
        
        /* Fix for info boxes */
        .stAlert {
            background-color: rgba(38, 39, 48, 0.8) !important;
            border: 1px solid rgba(250, 250, 250, 0.1) !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: rgba(49, 51, 63, 0.5) !important;
        }
        
        .streamlit-expanderContent {
            background-color: rgba(38, 39, 48, 0.4) !important;
        }
        
        /* Hide inline streamlit success/error messages */
        [data-testid="stForm"] div[data-baseweb="notification"],
        div[data-baseweb="notification"] {
            display: none !important;
            opacity: 0 !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Hide any cat emoji text that appears under buttons */
        div.stButton + div:has(p:contains("🐱")),
        div.stButton + div:has(p:contains("🐈")),
        div.stButton + div:has(p:contains("😺")),
        /* More aggressive selectors */
        div.stButton + div p,
        div.stButton + div div {
            display: none !important;
            height: 0 !important;
            visibility: hidden !important;
            opacity: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            pointer-events: none !important;
        }
    </style>
    
    <script>
    // Function to hide all inline success and error messages
    function hideInlineMessages() {
        const observer = new MutationObserver((mutations) => {
            // Hide all notifications
            document.querySelectorAll('[data-baseweb="notification"]').forEach(el => {
                el.style.display = 'none';
                el.style.height = '0';
                el.style.opacity = '0';
                el.style.margin = '0';
                el.style.padding = '0';
            });
            
            // Hide any elements after buttons - aggressive approach
            document.querySelectorAll('div.stButton + div').forEach(div => {
                div.style.display = 'none';
                div.style.height = '0';
                div.style.opacity = '0';
                div.style.margin = '0';
                div.style.padding = '0';
            });
        });
        
        observer.observe(document.body, { 
            childList: true, 
            subtree: true 
        });
    }
    
    // Run when DOM is loaded
    document.addEventListener('DOMContentLoaded', hideInlineMessages);
    setTimeout(hideInlineMessages, 100);
    setTimeout(hideInlineMessages, 500);
    setTimeout(hideInlineMessages, 1000);
    </script>
    """, unsafe_allow_html=True)


def display_header():
    """Display the app header."""
    st.markdown("<h1 class='main-header'>🐱 Cat Food Consumption Tracker 🐱</h1>", unsafe_allow_html=True)
    st.markdown(
        "Track how much food your cats are eating daily. "
        "Record the initial weight when filling their bowls and later add the remaining weight to see consumption patterns."
    )


def create_quick_input_section(db):
    """Create a condensed input section at the top for all cats."""
    # st.markdown("<h2 class='section-title'>Quick Weight Entry</h2>", unsafe_allow_html=True)
    
    # Check for reset flags at the beginning - before any widgets are created
    for cat_name in CATS:
        # Check for initial weight reset flags
        reset_key = f"reset_initial_{cat_name}"
        if reset_key in st.session_state and st.session_state[reset_key]:
            # Clear the input value by removing it from session state
            if f"quick_initial_{cat_name}" in st.session_state:
                del st.session_state[f"quick_initial_{cat_name}"]
            # Reset the flag
            st.session_state[reset_key] = False
        
        # Check for remaining weight reset flags
        # Get open entries for this cat
        open_entries = db.get_todays_open_entries(cat_name)
        for entry in open_entries:
            reset_key = f"reset_remaining_{cat_name}_{entry['id']}"
            if reset_key in st.session_state and st.session_state[reset_key]:
                # Clear the input value
                if f"quick_remaining_{cat_name}_{entry['id']}" in st.session_state:
                    del st.session_state[f"quick_remaining_{cat_name}_{entry['id']}"]
                # Reset the flag
                st.session_state[reset_key] = False
    
    # st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    
    # Add date selector at the top
    col_date, col_reset, *_ = st.columns([2, 1, 1])
    with col_date:
        # Default to today
        if 'selected_date' not in st.session_state:
            st.session_state['selected_date'] = datetime.date.today()
            
        selected_date = st.date_input(
            "Select Date", 
            value=st.session_state['selected_date'],
            max_value=datetime.date.today()
        )
        
        # Store the selected date in session state
        if selected_date != st.session_state['selected_date']:
            st.session_state['selected_date'] = selected_date
            st.rerun()  # Rerun to refresh the UI based on the new date
    
    # Add reset day button
    with col_reset:
        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)  # Align with date input
        if st.button("Reset Day", key="reset_day_button", type="secondary"):
            # Confirm before deletion
            st.session_state['confirm_day_reset'] = True
            st.rerun()
    
    # Handle confirmation for day reset
    if 'confirm_day_reset' in st.session_state and st.session_state['confirm_day_reset']:
        confirm_col1, confirm_col2 = st.columns(2)
        st.markdown(
            f"""<div style="background-color: rgba(255, 0, 0, 0.1); border-radius: 5px; padding: 10px; margin: 10px 0;">
                <p style="color: #ff0000; margin: 0; font-weight: bold;">
                    Delete ALL entries for {selected_date.strftime('%A, %B %d, %Y')}?
                </p>
            </div>""", 
            unsafe_allow_html=True
        )
        
        with confirm_col1:
            if st.button("Yes, Delete Day's Data", key="confirm_delete_day"):
                # Delete all entries for the selected date
                deleted_count = db.delete_entries_by_date(selected_date.isoformat())
                if deleted_count > 0:
                    st.success(f"Deleted {deleted_count} entries for {selected_date.strftime('%B %d, %Y')}")
                else:
                    st.info(f"No entries found for {selected_date.strftime('%B %d, %Y')}")
                # Reset confirmation state
                st.session_state['confirm_day_reset'] = False
                st.rerun()
        
        with confirm_col2:
            if st.button("Cancel", key="cancel_delete_day"):
                st.session_state['confirm_day_reset'] = False
                st.rerun()
    
    # Format the selected date for database queries
    selected_date_str = selected_date.isoformat()
    is_today = selected_date == datetime.date.today()
    
    # Create three columns for the cats
    cols = st.columns(len(CATS))
    
    for idx, cat_name in enumerate(CATS):
        with cols[idx]:
            st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
            st.markdown(f"<div class='cat-name-header' style='color: {CAT_COLORS[cat_name]};'>{cat_name}</div>", unsafe_allow_html=True)
            
            # Get entries for the selected date (not just today)
            if is_today:
                # Use existing function for today's entries
                open_entries = db.get_todays_open_entries(cat_name)
            else:
                # Get entries for the specific date
                all_entries = db.get_entries_by_date_range(selected_date_str, selected_date_str, cat_name)
                open_entries = [e for e in all_entries if e['remaining_weight'] is None]
            
            # Dynamic input behavior based on whether there are open entries
            if open_entries:
                # If there are open entries, show field for remaining weight
                
                # Create a selectbox if there are multiple entries
                if len(open_entries) > 1:
                    selected_entry = st.selectbox(
                        "Select entry",
                        options=[(e["id"], f"Entry #{e['id']} - {e['initial_weight']}g") for e in open_entries],
                        format_func=lambda x: x[1],
                        key=f"select_entry_{cat_name}_{selected_date_str}"
                    )
                    entry_id = selected_entry[0]
                    entry = next(e for e in open_entries if e["id"] == entry_id)
                else:
                    entry = open_entries[0]
                    entry_id = entry["id"]
                    st.info(f"Initial: {entry['initial_weight']}g")
                
                # st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                remaining_weight = st.number_input(
                    "Remaining food (g)",
                    min_value=0.0,
                    max_value=float(entry['initial_weight']),
                    step=1.0,
                    key=f"quick_remaining_{cat_name}_{entry_id}_{selected_date_str}"
                )
                
                if st.button(f"Record Remaining", key=f"quick_btn_remaining_{cat_name}_{entry_id}_{selected_date_str}"):
                    if db.update_remaining_weight(entry_id, remaining_weight):
                        consumed = entry['initial_weight'] - remaining_weight
                        # Set reset flag
                        st.session_state[f"reset_remaining_{cat_name}_{entry_id}"] = True
                        st.rerun()
                    else:
                        st.error("Failed to update")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                # If no open entries, show field for new initial weight
                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                initial_weight = st.number_input(
                    "Initial food weight (g)",
                    min_value=0.0,
                    max_value=1000.0,
                    step=1.0,
                    value=0.0,
                    key=f"quick_initial_{cat_name}_{selected_date_str}"
                )
                
                record_button_label = "Record Initial"
                if not is_today:
                    record_button_label = f"Record for {selected_date.strftime('%b %d')}"
                
                if st.button(record_button_label, key=f"quick_btn_initial_{cat_name}_{selected_date_str}"):
                    if initial_weight > 0:
                        # Pass the selected date when adding a new entry
                        entry_id = db.add_entry(cat_name, initial_weight, selected_date_str)
                        # Set a reset flag instead of directly modifying the session state
                        st.session_state[f"reset_initial_{cat_name}"] = True
                        st.rerun()
                    else:
                        st.error("Enter weight > 0")
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def create_cat_card(cat_name, db):
    """Create a UI card for each cat with statistics."""
    cat_color = CAT_COLORS[cat_name]
    
    st.markdown(
        f"<div class='cat-card'>",
        unsafe_allow_html=True
    )
    
    # Recent statistics
    with st.expander("Recent Statistics", expanded=True):
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=7)).isoformat()
        recent_entries = db.get_entries_by_date_range(start_date, today.isoformat(), cat_name)
        
        if recent_entries:
            # Calculate average consumption for completed entries
            completed_entries = [e for e in recent_entries if e['remaining_weight'] is not None]
            
            if completed_entries:
                avg_consumption = sum(e['initial_weight'] - e['remaining_weight'] for e in completed_entries) / len(completed_entries)
                last_entry = completed_entries[0]
                last_consumed = last_entry['initial_weight'] - last_entry['remaining_weight'] if last_entry['remaining_weight'] is not None else 0
                
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Avg. Daily Consumption (7 days)", f"{avg_consumption:.1f}g")
                
                with cols[1]:
                    st.metric("Last Recorded Consumption", f"{last_consumed:.1f}g")
                
            else:
                st.info("No completed entries in the last 7 days.")
        else:
            st.info("No data recorded in the last 7 days.")
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_history_chart(db):
    """Display food consumption history with all cats in a single comparative chart."""
    st.markdown("<h2 class='section-title'>Food Consumption History</h2>", unsafe_allow_html=True)
    
    # Get data for all cats for the last 30 days
    cat_data = db.get_last_30_days_data()
    
    # Check if we have any data
    has_data = any(cat_data[cat] for cat in CATS)
    
    if not has_data:
        st.info("No data available for the last 30 days. Start tracking to see the history chart!")
        return
    
    # Create a single figure for all cats
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#262730')
    ax.set_facecolor('#262730')
    
    # Use last 10 days for a clear daily view
    num_days = 10
    today = datetime.date.today()
    date_range = [(today - datetime.timedelta(days=i)) for i in range(num_days-1, -1, -1)]
    date_strs = [d.isoformat() for d in date_range]
    
    # Prepare data for each cat by day
    all_cat_daily_consumption = {}
    max_consumption = 0  # Track max for y-axis scaling
    
    # First collect and organize data
    for cat_name in CATS:
        cat_entries = cat_data[cat_name]
        daily_consumption = []
        
        for date in date_range:
            date_str = date.isoformat()
            # Find all entries for this cat on this date
            day_entries = [
                e for e in cat_entries 
                if e['date'].startswith(date_str) and e['remaining_weight'] is not None
            ]
            
            if day_entries:
                # Sum consumption for the day
                total_consumed = sum(e['initial_weight'] - e['remaining_weight'] for e in day_entries)
                daily_consumption.append(total_consumed)
                max_consumption = max(max_consumption, total_consumed)
            else:
                # No data for this day
                daily_consumption.append(0)
        
        all_cat_daily_consumption[cat_name] = daily_consumption
    
    # Set up bar properties
    num_cats = len(CATS)
    bar_width = 0.8 / num_cats  # Width for each cat's bar
    
    # Plot grouped bars for each cat
    for i, cat_name in enumerate(CATS):
        # Calculate bar positions
        x = np.arange(len(date_range))
        offset = (i - num_cats/2 + 0.5) * bar_width
        bar_positions = x + offset
        
        # Get cat's data and color
        cat_consumption = all_cat_daily_consumption[cat_name]
        cat_color = CAT_COLORS[cat_name]
        
        # Create bars for this cat
        bars = ax.bar(
            bar_positions,
            cat_consumption,
            width=bar_width,
            color=cat_color,
            alpha=0.85,
            edgecolor='white',
            linewidth=0.7,
            label=f"{cat_name}"
        )
        
        # Add values on top of bars that have non-zero data
        for j, (bar, value) in enumerate(zip(bars, cat_consumption)):
            if value > 0:  # Only add text for days with data
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 2,
                    f"{value:.1f}g",
                    ha='center',
                    va='bottom',
                    color='white',
                    fontsize=9,
                    fontweight='bold',
                    rotation=0 if len(date_range) < 8 else 90
                )
    
    # Format x-axis with dates
    formatted_dates = [d.strftime('%a\n%m/%d') for d in date_range]  # Day of week + date
    ax.set_xticks(np.arange(len(date_range)))
    ax.set_xticklabels(formatted_dates)
    
    # Set chart title and labels
    ax.set_title(
        'Daily Food Consumption - All Cats', 
        fontsize=18, 
        fontweight='bold', 
        color='white',
        pad=15
    )
    
    # Customize y-axis
    ax.set_ylabel('Consumed Food (grams)', fontsize=14, color='white', labelpad=10)
    ax.tick_params(axis='y', colors='white', labelsize=12)
    
    # Customize x-axis
    ax.tick_params(axis='x', colors='white', labelsize=12)
    ax.set_axisbelow(True)
    
    # Add horizontal grid lines
    ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='gray')
    ax.set_axisbelow(True)  # Put grid below bars
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color('gray')
        spine.set_alpha(0.2)
    
    # Add legend with cat colors
    legend = ax.legend(
        title="Cats", 
        fontsize=12, 
        title_fontsize=14,
        loc='upper left',
        framealpha=0.7,
        facecolor='#262730',
        edgecolor='white',
        labelcolor='white'
    )
    legend.get_title().set_color('white')
    
    # Set y-axis limit with headroom
    if max_consumption > 0:
        ax.set_ylim(0, max_consumption * 1.2)
    
    # Better padding
    plt.tight_layout(pad=3.0)
    
    st.pyplot(fig)


def reset_database():
    """Add a database reset section with confirmation mechanism."""
    st.markdown("<h2 class='section-title'>Database Management</h2>", unsafe_allow_html=True)
    
    # Create a container with warning styling
    st.markdown("""
    <div style="background-color: rgba(220, 53, 69, 0.1); border-radius: 10px; padding: 15px; border-left: 5px solid #dc3545; margin-bottom: 20px;">
        <h3 style="color: #dc3545; margin-top: 0;">⚠️ Danger Zone</h3>
        <p>Resetting the database will permanently delete all cat weight data. This action cannot be undone!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Setup confirmation mechanism
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if 'confirm_reset' not in st.session_state:
            st.session_state['confirm_reset'] = False
        
        if st.button("Reset Database", type="primary", use_container_width=True):
            st.session_state['confirm_reset'] = not st.session_state['confirm_reset']
    
    with col2:
        if st.session_state['confirm_reset']:
            st.markdown("""
            <div style="background-color: rgba(255, 0, 0, 0.1); border-radius: 5px; padding: 10px; margin-bottom: 10px;">
                <p style="color: #ff0000; margin: 0; font-weight: bold;">Are you sure? This will delete ALL weight data for ALL cats!</p>
            </div>
            """, unsafe_allow_html=True)
            
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("Yes, Reset Everything", use_container_width=True):
                    # Perform actual database reset
                    db = CatWeightDatabase()
                    db.reset_database()
                    db.close()
                    
                    # Show success notification with standard Streamlit success message
                    st.success("Database has been completely reset!")
                    
                    # Reset confirmation state
                    st.session_state['confirm_reset'] = False
                    
                    # Rerun to refresh the page
                    st.rerun()
            
            with confirm_col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state['confirm_reset'] = False
                    st.rerun()


def create_date_status_indicator(db):
    """Create a 7-day calendar view with color-coded status indicators."""
    # st.markdown("<h2 class='section-title'>Last 7 Days Status</h2>", unsafe_allow_html=True)
        # Add a legend
    st.markdown("<br>", unsafe_allow_html=True)
    legend_cols = st.columns([1, 1, 1, 3])
    with legend_cols[0]:
        st.markdown(
            """<div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 15px; height: 15px; background-color: #4CAF50; margin-right: 5px; border-radius: 3px;"></div>
                <span style="font-size: 0.8rem;">All Complete</span>
            </div>""", 
            unsafe_allow_html=True
        )
    with legend_cols[1]:
        st.markdown(
            """<div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 15px; height: 15px; background-color: #FF9800; margin-right: 5px; border-radius: 3px;"></div>
                <span style="font-size: 0.8rem;">Partial</span>
            </div>""", 
            unsafe_allow_html=True
        )
    with legend_cols[2]:
        st.markdown(
            """<div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 15px; height: 15px; background-color: #F44336; margin-right: 5px; border-radius: 3px;"></div>
                <span style="font-size: 0.8rem;">No Data</span>
            </div>""", 
            unsafe_allow_html=True
        )
    # Get the last 7 days
    today = datetime.date.today()
    date_range = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]  # Last 7 days, most recent at the end
    
    # Query data for all cats in this date range
    start_date = date_range[0].isoformat()
    end_date = date_range[-1].isoformat()
    
    # Initialize status dictionaries for each date
    date_status = {}
    
    # For each date, check status for all cats
    for current_date in date_range:
        date_str = current_date.isoformat()
        cat_statuses = {}
        
        # Check status for each cat
        for cat_name in CATS:
            entries = db.get_entries_by_date_range(date_str, date_str, cat_name)
            
            if not entries:
                # No entries for this cat
                cat_statuses[cat_name] = "none"
            else:
                # Check if any entry has both initial and remaining weights
                has_complete = any(entry['remaining_weight'] is not None for entry in entries)
                if has_complete:
                    cat_statuses[cat_name] = "complete"
                else:
                    cat_statuses[cat_name] = "initial"
        
        # Determine overall status for the day
        if all(status == "complete" for status in cat_statuses.values()):
            date_status[date_str] = "complete"  # Green
        elif all(status == "none" for status in cat_statuses.values()):
            date_status[date_str] = "none"  # Red
        else:
            date_status[date_str] = "partial"  # Orange
    
    # Add CSS for styling
    st.markdown("""
    <style>
        .day-circle {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-size: 1.2rem;
            font-weight: bold;
            color: white;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }
        .status-complete { background-color: #4CAF50; }
        .status-partial { background-color: #FF9800; }
        .status-none { background-color: #F44336; }
        .day-name {
            text-align: center;
            font-size: 0.8rem;
            color: #ccc;
            margin-top: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create columns for each day
    day_cols = st.columns(7)
    
    # Display each day indicator in its own column
    for i, date in enumerate(date_range):
        date_str = date.isoformat()
        status = date_status.get(date_str, "none")
        
        # Determine status class
        status_class = {
            "complete": "status-complete",
            "partial": "status-partial",
            "none": "status-none"
        }.get(status, "status-none")
        
        # Format day name and date
        day_name = date.strftime("%a")
        day_number = date.strftime("%d")
        
        # Display the day indicator within its column
        with day_cols[i]:
            st.markdown(f"""
            <div>
                <div class="day-circle {status_class}">{day_number}</div>
                <div class="day-name">{day_name}</div>
            </div>
            """, unsafe_allow_html=True)
    

def display_fun_statistics(db):
    """Display fun statistics and trends based on the last 7 days of data."""
    st.markdown("<h2 class='section-title'>🎮 Fun Stats & Trends (Last 7 Days) 🎮</h2>", unsafe_allow_html=True)
    
    # Get data for the last 7 days
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=6)).isoformat()  # 7 days including today
    end_date = today.isoformat()
    
    # Create a container with a slightly different background for the fun stats
    # st.markdown("""
    # <div style="background-color: rgba(60, 60, 80, 0.3); border-radius: 10px; padding: 20px; margin-top: 20px; border: 1px solid rgba(100, 100, 150, 0.2);">
    # """, unsafe_allow_html=True)
    
    # Collect consumption data for all cats
    all_cat_data = {}
    has_data = False
    
    for cat_name in CATS:
        entries = db.get_entries_by_date_range(start_date, end_date, cat_name)
        completed_entries = [e for e in entries if e['remaining_weight'] is not None]
        
        if completed_entries:
            has_data = True
            all_cat_data[cat_name] = {
                'entries': completed_entries,
                'daily_consumption': {},
                'total_consumed': 0,
                'avg_consumed': 0,
                'consistency': 0,
                'trend': 'stable'
            }
            
            # Calculate total and daily consumption
            total_consumed = 0
            day_consumptions = []
            
            for entry in completed_entries:
                consumed = entry['initial_weight'] - entry['remaining_weight']
                total_consumed += consumed
                
                # Extract date without time
                date_only = entry['date'].split('T')[0]
                
                # Add to daily consumption
                if date_only not in all_cat_data[cat_name]['daily_consumption']:
                    all_cat_data[cat_name]['daily_consumption'][date_only] = 0
                all_cat_data[cat_name]['daily_consumption'][date_only] += consumed
                
            # Calculate average consumption
            all_cat_data[cat_name]['total_consumed'] = total_consumed
            all_cat_data[cat_name]['avg_consumed'] = total_consumed / len(completed_entries)
            
            # Calculate consumption by day for consistency calculation
            for date, amount in all_cat_data[cat_name]['daily_consumption'].items():
                day_consumptions.append(amount)
            
            # Calculate consistency (standard deviation) if we have enough data
            if len(day_consumptions) > 1:
                all_cat_data[cat_name]['consistency'] = np.std(day_consumptions)
            
            # Determine trend (if we have at least 3 days of data)
            if len(day_consumptions) >= 3:
                # Sort by date
                sorted_days = sorted(all_cat_data[cat_name]['daily_consumption'].items())
                # Get just the consumption values in chronological order
                chronological_consumption = [amount for _, amount in sorted_days]
                
                # Simple trend detection based on first half vs second half
                midpoint = len(chronological_consumption) // 2
                first_half_avg = sum(chronological_consumption[:midpoint]) / midpoint if midpoint > 0 else 0
                second_half_avg = sum(chronological_consumption[midpoint:]) / (len(chronological_consumption) - midpoint) if (len(chronological_consumption) - midpoint) > 0 else 0
                
                if second_half_avg > first_half_avg * 1.1:  # 10% increase
                    all_cat_data[cat_name]['trend'] = 'increasing'
                elif second_half_avg < first_half_avg * 0.9:  # 10% decrease
                    all_cat_data[cat_name]['trend'] = 'decreasing'
    
    # Display stats only if we have data
    if not has_data:
        st.info("Not enough data yet! Complete some feeding records to see fun statistics.")
    else:
        # Create 2 rows of stats
        row1_cols = st.columns(3)
        
        # Stat 1: Biggest Eater
        with row1_cols[0]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the cat with the highest average consumption
            if all_cat_data:
                biggest_eater = max(all_cat_data.items(), key=lambda x: x[1]['avg_consumed'])
                cat_name = biggest_eater[0]
                avg_consumed = biggest_eater[1]['avg_consumed']
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">👑 Biggest Appetite</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Averaging <span style="color: white; font-weight: bold;">{avg_consumed:.1f}g</span> per feeding
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
            
        # Stat 2: Most Consistent Eater
        with row1_cols[1]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the cat with the lowest standard deviation (most consistent)
            consistent_cats = [cat for cat, data in all_cat_data.items() if len(data['daily_consumption']) > 1]
            
            if consistent_cats:
                most_consistent = min([cat for cat in all_cat_data.items() if cat[0] in consistent_cats], 
                                      key=lambda x: x[1]['consistency'])
                cat_name = most_consistent[0]
                consistency = most_consistent[1]['consistency']
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">⏱️ Clockwork Eater</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Most consistent eating patterns<br>
                        <span style="color: white; font-weight: bold;">{consistency:.1f}g</span> standard deviation
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
            
        # Stat 3: Trending Cat
        with row1_cols[2]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find cats with clear trends
            trending_cats = [cat for cat, data in all_cat_data.items() 
                             if data['trend'] in ['increasing', 'decreasing'] and len(data['daily_consumption']) >= 3]
            
            if trending_cats:
                # Prioritize cats with increasing or decreasing trends
                trending_cat_name = trending_cats[0]
                trend = all_cat_data[trending_cat_name]['trend']
                
                trend_icon = "📈" if trend == "increasing" else "📉"
                trend_text = "Increasing appetite" if trend == "increasing" else "Decreasing appetite"
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[trending_cat_name]};">{trend_icon} Trending</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(trending_cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        {trend_text} over the last week
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show the cat with most data points if no clear trends
                most_data_cat = max(all_cat_data.items(), key=lambda x: len(x[1]['daily_consumption']))
                cat_name = most_data_cat[0]
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">🔄 Steady Eater</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Maintaining steady eating patterns
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Row 2: More stats
        row2_cols = st.columns(3)
        
        # Stat 4: Hungriest Day
        with row2_cols[0]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Aggregate consumption by day across all cats
            daily_totals = {}
            
            for cat_name, data in all_cat_data.items():
                for date, amount in data['daily_consumption'].items():
                    if date not in daily_totals:
                        daily_totals[date] = 0
                    daily_totals[date] += amount
            
            if daily_totals:
                # Find the day with highest consumption
                hungriest_day, max_consumed = max(daily_totals.items(), key=lambda x: x[1])
                
                # Convert ISO date to readable format
                hungriest_date = datetime.date.fromisoformat(hungriest_day)
                formatted_date = hungriest_date.strftime("%A %b %d")
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: #4CAF50;">🍽️ Hungriest Day</h3>
                    <div style="font-size: 1.3rem; font-weight: bold; margin: 10px 0;">
                        {formatted_date}
                    </div>
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Total consumption: <span style="color: white; font-weight: bold;">{max_consumed:.1f}g</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Stat 5: Leftover Champion
        with row2_cols[1]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the cat that leaves the most food (highest remaining percentage)
            leftover_percentages = {}
            
            for cat_name, data in all_cat_data.items():
                total_initial = sum(entry['initial_weight'] for entry in data['entries'])
                total_remaining = sum(entry['remaining_weight'] for entry in data['entries'])
                
                if total_initial > 0:
                    leftover_percentages[cat_name] = (total_remaining / total_initial) * 100
            
            if leftover_percentages:
                leftover_champion, leftover_pct = max(leftover_percentages.items(), key=lambda x: x[1])
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[leftover_champion]};">🍱 Leftover Champion</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(leftover_champion), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Leaves <span style="color: white; font-weight: bold;">{leftover_pct:.1f}%</span> of food behind
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Stat 6: Weekly Champion
        with row2_cols[2]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Calculate which cat has the most complete entries this week
            entry_counts = {cat_name: len(data['entries']) for cat_name, data in all_cat_data.items()}
            
            if entry_counts:
                weekly_champion, entry_count = max(entry_counts.items(), key=lambda x: x[1])
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[weekly_champion]};">🏆 Weekly Champion</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(weekly_champion), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Most tracked meals this week: <span style="color: white; font-weight: bold;">{entry_count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Fun fact or tip at the bottom
        fun_facts = [
            "Did you know? Cats typically spend 2/3 of their day sleeping!",
            "Cats have excellent hearing and can detect higher frequencies than both dogs and humans.",
            "A cat's whiskers help them navigate and judge whether they can fit through openings.",
            "Consistent feeding schedules help maintain your cat's health and happiness!",
            "An adult cat spends about 50% of their day grooming.",
            "The technical term for a hairball is a 'bezoar'.",
            "Cats can jump up to six times their length in a single bound.",
            "A group of cats is called a 'clowder'."
        ]
        
        st.markdown(f"""
        <div style="margin-top: 15px; text-align: center; font-style: italic; color: #aaa;">
            <span style="font-size: 0.9rem;">💡 Fun Fact: {np.random.choice(fun_facts)}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_fun_statistics_30days(db):
    """Display fun statistics and trends based on the last 30 days of data."""
    st.markdown("<h2 class='section-title'>📊 Monthly Insights (Last 30 Days) 📊</h2>", unsafe_allow_html=True)
    
    # Get data for the last 30 days
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=29)).isoformat()  # 30 days including today
    end_date = today.isoformat()
    
    # Create a container with a slightly different background for the fun stats
    st.markdown("""
    <div style="background-color: rgba(60, 70, 90, 0.3); border-radius: 10px; padding: 20px; margin-top: 20px; margin-bottom: 30px; border: 1px solid rgba(100, 120, 150, 0.2);">
    """, unsafe_allow_html=True)
    
    # Collect consumption data for all cats
    all_cat_data = {}
    has_data = False
    
    for cat_name in CATS:
        entries = db.get_entries_by_date_range(start_date, end_date, cat_name)
        completed_entries = [e for e in entries if e['remaining_weight'] is not None]
        
        if completed_entries:
            has_data = True
            all_cat_data[cat_name] = {
                'entries': completed_entries,
                'daily_consumption': {},
                'weekday_consumption': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},  # Mon-Sun
                'weekday_counts': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
                'total_consumed': 0,
                'avg_consumed': 0,
                'consistency': 0,
                'days_tracked': set(),
                'most_recent_trend': []  # Last 10 entries for trend analysis
            }
            
            # Calculate total and daily consumption
            total_consumed = 0
            day_consumptions = []
            
            for entry in completed_entries:
                consumed = entry['initial_weight'] - entry['remaining_weight']
                total_consumed += consumed
                
                # Extract date without time
                date_only = entry['date'].split('T')[0]
                entry_date = datetime.date.fromisoformat(date_only)
                
                # Add to daily consumption
                if date_only not in all_cat_data[cat_name]['daily_consumption']:
                    all_cat_data[cat_name]['daily_consumption'][date_only] = 0
                    all_cat_data[cat_name]['days_tracked'].add(date_only)
                
                all_cat_data[cat_name]['daily_consumption'][date_only] += consumed
                
                # Track consumption by day of week
                weekday = entry_date.weekday()
                all_cat_data[cat_name]['weekday_consumption'][weekday] += consumed
                all_cat_data[cat_name]['weekday_counts'][weekday] += 1
                
                # Add to recent trend (last 10 entries)
                all_cat_data[cat_name]['most_recent_trend'].append({
                    'date': entry_date,
                    'consumed': consumed
                })
            
            # Sort recent entries by date
            all_cat_data[cat_name]['most_recent_trend'].sort(key=lambda x: x['date'])
            
            # Calculate average consumption
            all_cat_data[cat_name]['total_consumed'] = total_consumed
            all_cat_data[cat_name]['avg_consumed'] = total_consumed / len(completed_entries)
            
            # Calculate consumption by day for consistency calculation
            for date, amount in all_cat_data[cat_name]['daily_consumption'].items():
                day_consumptions.append(amount)
            
            # Calculate consistency (standard deviation) if we have enough data
            if len(day_consumptions) > 1:
                all_cat_data[cat_name]['consistency'] = np.std(day_consumptions)
    
    # Display stats only if we have data
    if not has_data:
        st.info("Not enough data yet! Complete some feeding records over multiple weeks to see monthly insights.")
    else:
        # Create 2 rows of stats
        row1_cols = st.columns(3)
        
        # Stat 1: Monthly Food Champion
        with row1_cols[0]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the cat with the highest total consumption
            if all_cat_data:
                food_champion = max(all_cat_data.items(), key=lambda x: x[1]['total_consumed'])
                cat_name = food_champion[0]
                total_consumed = food_champion[1]['total_consumed']
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">🏅 Monthly Food Champion</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Consumed <span style="color: white; font-weight: bold;">{total_consumed:.1f}g</span> this month
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
            
        # Stat 2: Most Dedicated Tracking
        with row1_cols[1]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the cat with the most days tracked
            if all_cat_data:
                most_tracked = max(all_cat_data.items(), key=lambda x: len(x[1]['days_tracked']))
                cat_name = most_tracked[0]
                days_count = len(most_tracked[1]['days_tracked'])
                
                # Calculate percentage of the month
                days_percentage = (days_count / 30) * 100
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">📝 Most Tracked</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Tracked for <span style="color: white; font-weight: bold;">{days_count}</span> days<br>
                        <span style="color: white; font-weight: bold;">({days_percentage:.0f}%)</span> of the month
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
            
        # Stat 3: Most Consistent Overall
        with row1_cols[2]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the most consistent cat (minimum standard deviation with enough data points)
            consistent_cats = {cat_name: data for cat_name, data in all_cat_data.items() 
                               if len(data['daily_consumption']) >= 5}
            
            if consistent_cats:
                most_consistent = min(consistent_cats.items(), key=lambda x: x[1]['consistency'])
                cat_name = most_consistent[0]
                consistency = most_consistent[1]['consistency']
                avg_consumed = most_consistent[1]['avg_consumed']
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">🏆 Most Consistent</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Reliably eats <span style="color: white; font-weight: bold;">{avg_consumed:.1f}g</span> per meal<br>
                        <span style="color: white; font-weight: bold;">±{consistency:.1f}g</span> standard deviation
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Row 2: More stats
        row2_cols = st.columns(3)
        
        # Stat 4: Favorite Day of the Week
        with row2_cols[0]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Aggregate consumption by day of week across all cats
            weekday_totals = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            weekday_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            
            for cat_name, data in all_cat_data.items():
                for weekday, amount in data['weekday_consumption'].items():
                    weekday_totals[weekday] += amount
                    weekday_counts[weekday] += data['weekday_counts'][weekday]
            
            # Calculate average consumption by day with enough data
            weekday_avgs = {}
            for day, total in weekday_totals.items():
                if weekday_counts[day] >= 3:  # Only include days with enough data
                    weekday_avgs[day] = total / weekday_counts[day] if weekday_counts[day] > 0 else 0
            
            if weekday_avgs:
                # Find the day with highest average consumption
                favorite_day, avg_consumed = max(weekday_avgs.items(), key=lambda x: x[1])
                
                # Convert weekday number to name
                weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day_name = weekday_names[favorite_day]
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: #64B5F6;">📅 Favorite Day</h3>
                    <div style="font-size: 1.3rem; font-weight: bold; margin: 10px 0;">
                        {day_name}
                    </div>
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Cats eat <span style="color: white; font-weight: bold;">{avg_consumed:.1f}g</span> on average<br>
                        <span style="color: white; font-weight: bold;">{weekday_counts[favorite_day]}</span> meals tracked
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Stat 5: Most Variable Eater
        with row2_cols[1]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Find the cat with the highest standard deviation (most variable eating)
            variable_cats = {cat_name: data for cat_name, data in all_cat_data.items() 
                             if len(data['daily_consumption']) >= 5}
            
            if variable_cats:
                most_variable = max(variable_cats.items(), key=lambda x: x[1]['consistency'])
                cat_name = most_variable[0]
                variability = most_variable[1]['consistency']
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">🎭 Moody Eater</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        Most unpredictable appetite<br>
                        <span style="color: white; font-weight: bold;">±{variability:.1f}g</span> day-to-day variance
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Stat 6: Trend Setter (Most clear long-term trend)
        with row2_cols[2]:
            # st.markdown("""<div class="stat-card" style="height: 160px;">""", unsafe_allow_html=True)
            
            # Analyze trends for cats with enough data points
            trend_data = {}
            for cat_name, data in all_cat_data.items():
                if len(data['daily_consumption']) >= 10:
                    # Get chronological consumption data
                    dates = sorted(data['daily_consumption'].keys())
                    values = [data['daily_consumption'][date] for date in dates]
                    
                    # Calculate slope using numpy polyfit
                    if len(dates) >= 2:
                        x = range(len(values))
                        slope, _ = np.polyfit(x, values, 1)
                        
                        # Normalized slope (percentage change over the period)
                        avg_value = np.mean(values)
                        if avg_value > 0:
                            normalized_slope = (slope * len(values)) / avg_value
                            
                            # Store the absolute normalized slope for ranking
                            trend_data[cat_name] = {
                                'slope': slope,
                                'abs_slope': abs(normalized_slope),
                                'trend': 'increasing' if slope > 0 else 'decreasing'
                            }
            
            if trend_data:
                # Find the cat with the strongest trend (highest absolute slope)
                trendsetter = max(trend_data.items(), key=lambda x: x[1]['abs_slope'])
                cat_name = trendsetter[0]
                trend = trendsetter[1]['trend']
                
                # Determine icon and description based on trend
                trend_icon = "📈" if trend == "increasing" else "📉"
                trend_desc = "Steadily increasing appetite" if trend == "increasing" else "Gradually decreasing appetite"
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin: 0; color: {CAT_COLORS[cat_name]};">{trend_icon} Trend Setter</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the cat icon separately with safe HTML
                st.markdown(get_cat_icon_html(cat_name), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #ccc;">
                        {trend_desc}<br>
                        over the last month
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align: center;"><p>Not enough data for trend analysis</p></div>""", unsafe_allow_html=True)
            
            # st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Monthly fun fact
        monthly_facts = [
            "Did you know? An average house cat can reach speeds of up to 30 mph in short bursts!",
            "A cat's brain is more similar to a human's brain than a dog's brain.",
            "The average cat sleeps for 12-16 hours per day, which means a 9-year-old cat has been awake for only 3 years of its life.",
            "Cats can rotate their ears 180 degrees, with 32 muscles controlling their ear movements.",
            "Cats have 5 toes on their front paws but only 4 on their back paws.",
            "A cat's purring vibrations are at a frequency that promotes bone growth and healing.",
            "Cats only sweat through their paw pads, not their entire bodies like humans do.",
            "Male cats are typically left-pawed, while female cats tend to be right-pawed."
        ]
        
        st.markdown(f"""
        <div style="margin-top: 15px; text-align: center; font-style: italic; color: #aaa;">
            <span style="font-size: 0.9rem;">🔍 Monthly Insight: {np.random.choice(monthly_facts)}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Main application function."""
    # Initialize the database
    db = CatWeightDatabase()
    
    # Setup page configuration and styling
    setup_page()
    
    # Display the header
    # display_header()
    
    # Display the 7-day status indicators
    create_date_status_indicator(db)
    
    # Display the quick input section at the top
    create_quick_input_section(db)
    
    # Create a section for each cat with statistics
    # st.markdown("<h2 class='section-title'>Cat Statistics</h2>", unsafe_allow_html=True)
    
    # Use columns instead of sequential rendering to avoid dividers
    cat_cols = st.columns(len(CATS))
    
    # Handle both normal operation and testing environment
    if cat_cols:  # Check if cat_cols is not empty
        for idx, cat_name in enumerate(CATS):
            if idx < len(cat_cols):  # Safe access
                with cat_cols[idx]:
                    # Add small header with cat name and color for reference
                    # st.markdown(f"<div class='cat-name-header' style='color: {CAT_COLORS[cat_name]};'>{cat_name}</div>", unsafe_allow_html=True)
                    create_cat_card(cat_name, db)
            else:
                create_cat_card(cat_name, db)
    else:
        # Fallback for testing environment
        for cat_name in CATS:
            create_cat_card(cat_name, db)
    
    # Display the 30-day history chart
    display_history_chart(db)
    
    # Display fun statistics section - 7 days
    display_fun_statistics(db)
    
    # Display fun statistics section - 30 days
    display_fun_statistics_30days(db)
    
    # Add database reset functionality
    reset_database()
    
    # Close the database connection when the app is done
    db.close()


if __name__ == "__main__":
    main() 