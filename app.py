import pandas as pd
import streamlit as st
import io
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="CSV Email Matcher",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "CSV Email Matcher App - Match emails between two CSV files"
    }
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
        font-weight: 500;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .section {
        background-color: #f5f7f9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #1E88E5;
    }
    .highlight {
        color: #1E88E5;
        font-weight: 600;
    }
    .success-message {
        background-color: #e6f4ea;
        color: #137333;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #137333;
    }
    .info-badge {
        background-color: #e8f0fe;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        color: #1967d2;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .stats-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for app configuration
with st.sidebar:
    st.markdown("<h2>App Settings</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Theme selection
    theme = st.selectbox(
        "Select theme",
        ["Blue", "Green", "Purple", "Orange"],
        index=0
    )

    # Map theme selection to colors
    theme_colors = {
        "Blue": "#1E88E5",
        "Green": "#43A047",
        "Purple": "#8E24AA",
        "Orange": "#FB8C00"
    }
    primary_color = theme_colors[theme]

    # Apply theme color to elements
    st.markdown(f"""
        <style>
            .section {{
                border-left: 5px solid {primary_color} !important;
            }}
            .main-header, .highlight {{
                color: {primary_color} !important;
            }}
            /* Update other theme-dependent elements */
            .stButton>button {{
                background-color: {primary_color} !important;
                color: white !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    # Case sensitivity option
    case_sensitive = st.checkbox("Case-sensitive matching", value=False)

    # Options for handling duplicates
    handle_duplicates = st.radio(
        "Handle duplicate emails in verified list",
        ["Keep all duplicates", "Keep only unique emails"],
        index=1
    )

    # Advanced options
    with st.expander("Advanced options"):
        trim_whitespace = st.checkbox("Trim whitespace from emails", value=True)
        preview_rows = st.slider("Number of preview rows", 5, 50, 10)
        max_display_rows = st.slider("Maximum rows to display in results", 5, 100, 20)


# Helper functions
def get_download_link(df, filename, button_text):
    """Generate a styled download button for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    button_uuid = "download_" + filename.replace(".", "_")
    button_id = button_uuid

    custom_css = f"""
        <style>
            #{button_id} {{
                background-color: {primary_color};
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                border: none;
                text-decoration: none;
                font-weight: 500;
                cursor: pointer;
                display: inline-block;
                margin: 0.5rem 0;
                transition: all 0.3s;
            }}
            #{button_id}:hover {{
                opacity: 0.8;
            }}
        </style>
    """

    dl_link = custom_css + f'<a id="{button_id}" href="data:file/csv;base64,{b64}" download="{filename}">{button_text}</a>'
    return dl_link


def create_aggrid(df, key):
    """Create an interactive AgGrid table"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False
    )
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    return AgGrid(
        df,
        gridOptions=grid_options,
        theme="streamlit",
        enable_enterprise_modules=False,
        height=300,
        key=key
    )


def find_email_columns(df):
    """Find columns that might contain email addresses"""
    potential_email_cols = []
    for col in df.columns:
        # Check if column name contains 'email' (case insensitive)
        if 'email' in col.lower():
            potential_email_cols.append(col)
    return potential_email_cols


def create_metric_card(title, value, delta=None, help_text=None):
    """Create a styled metric card"""
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<h3 style='color:#555; font-size:1rem; margin-bottom:0;'>{title}</h3>", unsafe_allow_html=True)
        if help_text:
            st.caption(help_text)
    with col2:
        st.markdown(f"<h2 style='color:{primary_color}; font-size:1.8rem; font-weight:bold; margin:0;'>{value}</h2>",
                    unsafe_allow_html=True)
        if delta:
            st.markdown(f"<p style='color:#555; font-size:0.9rem; margin:0;'>{delta}</p>", unsafe_allow_html=True)


# Main app header
st.markdown(f"<h1 class='main-header' style='color:{primary_color};'>CSV Email Matcher</h1>", unsafe_allow_html=True)

st.markdown(f"""
<div class='section' style='border-left: 5px solid {primary_color};'>
This app helps you match emails between two CSV files and create a new file with the matching records.
<ul>
    <li>Upload a CSV with <span class='highlight' style='color:{primary_color};'>verified emails</span></li>
    <li>Upload a CSV with <span class='highlight' style='color:{primary_color};'>full data</span> containing emails</li>
    <li>Select which columns to match</li>
    <li>Get a new CSV with only the records that match</li>
</ul>
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown(f"<h2 class='sub-header' style='color:{primary_color};'>1. Upload CSV Files</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>", unsafe_allow_html=True)
    st.subheader("Verified Emails CSV")
    verified_emails_file = st.file_uploader(
        "Choose a CSV file with verified emails",
        type="csv",
        key="verified",
        help="This file should contain the email addresses you want to match"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>", unsafe_allow_html=True)
    st.subheader("Full Data CSV")
    full_data_file = st.file_uploader(
        "Choose a CSV file with full data",
        type="csv",
        key="full_data",
        help="This file contains all records, we'll extract only the matching ones"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Process files when both are uploaded
if verified_emails_file and full_data_file:
    # Create expanders for previewing data
    st.markdown(f"<h2 class='sub-header' style='color:{primary_color};'>2. Preview & Configure</h2>",
                unsafe_allow_html=True)

    try:
        # Load verified emails CSV
        verified_emails_df = pd.read_csv(verified_emails_file)

        # Load full data CSV
        full_data_df = pd.read_csv(full_data_file)

        # File info container
        st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>", unsafe_allow_html=True)
        cols = st.columns(4)

        with cols[0]:
            create_metric_card(
                "Verified Emails Rows",
                f"{len(verified_emails_df):,}",
                help_text="Total rows in verified emails file"
            )

        with cols[1]:
            create_metric_card(
                "Verified Emails Columns",
                f"{len(verified_emails_df.columns):,}",
                help_text="Number of columns in first file"
            )

        with cols[2]:
            create_metric_card(
                "Full Data Rows",
                f"{len(full_data_df):,}",
                help_text="Total rows in full data file"
            )

        with cols[3]:
            create_metric_card(
                "Full Data Columns",
                f"{len(full_data_df.columns):,}",
                help_text="Number of columns in second file"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Find potential email columns
        verified_email_cols = find_email_columns(verified_emails_df)
        full_data_email_cols = find_email_columns(full_data_df)

        # Column selection
        st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>", unsafe_allow_html=True)
        st.subheader("Column Selection")
        col1, col2 = st.columns(2)

        with col1:
            # Choose email column from verified emails CSV
            if verified_email_cols:
                default_verified_col = verified_email_cols[0] if 'Email' in verified_email_cols else \
                verified_email_cols[0]
                verified_email_column = st.selectbox(
                    "Select email column from verified emails CSV",
                    options=verified_emails_df.columns,
                    index=list(verified_emails_df.columns).index(
                        default_verified_col) if default_verified_col in verified_emails_df.columns else 0,
                    help="Choose the column containing the email addresses to match"
                )
            else:
                verified_email_column = st.selectbox(
                    "Select email column from verified emails CSV",
                    options=verified_emails_df.columns,
                    help="Choose the column containing the email addresses to match"
                )

        with col2:
            # Choose email column from full data CSV
            if full_data_email_cols:
                default_full_data_col = 'Email 1' if 'Email 1' in full_data_email_cols else full_data_email_cols[0]
                full_data_email_column = st.selectbox(
                    "Select email column from full data CSV",
                    options=full_data_df.columns,
                    index=list(full_data_df.columns).index(
                        default_full_data_col) if default_full_data_col in full_data_df.columns else 0,
                    help="Choose the column containing the email addresses to match against"
                )
            else:
                full_data_email_column = st.selectbox(
                    "Select email column from full data CSV",
                    options=full_data_df.columns,
                    help="Choose the column containing the email addresses to match against"
                )
        st.markdown("</div>", unsafe_allow_html=True)

        # Data preview tabs
        st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Verified Emails Preview", "Full Data Preview"])

        with tab1:
            st.subheader("Verified Emails Data")
            create_aggrid(verified_emails_df.head(preview_rows), "verified_preview")

            # Show sample of email column
            st.subheader(f"Sample of selected column: '{verified_email_column}'")
            email_sample = verified_emails_df[verified_email_column].dropna().head(5).tolist()
            email_sample_str = '<div style="margin: 10px 0;">'
            for email in email_sample:
                email_sample_str += f'<span class="info-badge">{email}</span>'
            email_sample_str += '</div>'
            st.markdown(email_sample_str, unsafe_allow_html=True)

        with tab2:
            st.subheader("Full Data Preview")
            create_aggrid(full_data_df.head(preview_rows), "full_data_preview")

            # Show sample of email column
            st.subheader(f"Sample of selected column: '{full_data_email_column}'")
            email_sample = full_data_df[full_data_email_column].dropna().head(5).tolist()
            email_sample_str = '<div style="margin: 10px 0;">'
            for email in email_sample:
                email_sample_str += f'<span class="info-badge">{email}</span>'
            email_sample_str += '</div>'
            st.markdown(email_sample_str, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Process button
        st.markdown(f"<h2 class='sub-header' style='color:{primary_color};'>3. Process Data</h2>",
                    unsafe_allow_html=True)

        process_button = st.button(
            "Match CSV Files",
            type="primary",
            help="Click to find matching records based on selected email columns"
        )

        if process_button:
            with st.spinner("Processing data..."):
                # Prepare verified emails for matching
                if handle_duplicates == "Keep only unique emails":
                    verified_emails = set()
                else:
                    verified_emails = []

                # Extract and process verified emails
                for email in verified_emails_df[verified_email_column]:
                    if pd.notna(email) and isinstance(email, str):
                        if trim_whitespace:
                            email = email.strip()

                        if not case_sensitive:
                            email = email.lower()

                        if handle_duplicates == "Keep only unique emails":
                            verified_emails.add(email)
                        else:
                            verified_emails.append(email)

                if handle_duplicates != "Keep only unique emails":
                    verified_emails = set(verified_emails)

                # Check for matches and create a new dataframe
                matched_rows = []
                for index, row in full_data_df.iterrows():
                    email = row[full_data_email_column]
                    # Check if the email exists and is a string before comparing
                    if pd.notna(email) and isinstance(email, str):
                        if trim_whitespace:
                            email = email.strip()

                        # Compare emails
                        if not case_sensitive:
                            compare_email = email.lower()
                        else:
                            compare_email = email

                        if compare_email in verified_emails:
                            matched_rows.append(row)

                # Create a new dataframe with matched rows
                matched_df = pd.DataFrame(matched_rows)

                # Display results
                st.markdown(f"<h2 class='sub-header' style='color:{primary_color};'>4. Results</h2>",
                            unsafe_allow_html=True)

                st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>",
                            unsafe_allow_html=True)
                # Stats cards
                col1, col2, col3 = st.columns(3)

                with col1:
                    create_metric_card(
                        "Verified Emails",
                        f"{len(verified_emails):,}",
                        help_text="Number of unique verified emails"
                    )

                with col2:
                    create_metric_card(
                        "Records Matched",
                        f"{len(matched_df):,}",
                        help_text="Number of matching records found"
                    )

                with col3:
                    if len(verified_emails) > 0:
                        match_percentage = (len(matched_df) / len(verified_emails)) * 100
                        create_metric_card(
                            "Match Rate",
                            f"{match_percentage:.1f}%",
                            help_text="Percentage of verified emails found in full data"
                        )
                    else:
                        create_metric_card(
                            "Match Rate",
                            "0%",
                            help_text="No valid emails to match"
                        )
                st.markdown("</div>", unsafe_allow_html=True)

                # Visualize results
                if len(matched_df) > 0:
                    st.markdown(f"<div class='section' style='border-left: 5px solid {primary_color};'>",
                                unsafe_allow_html=True)
                    st.subheader("Matched Data")

                    # Download button for matched data
                    st.markdown(
                        get_download_link(matched_df, "matched_data.csv", "📥 Download Matched Data CSV"),
                        unsafe_allow_html=True
                    )

                    # Display matched data
                    create_aggrid(matched_df.head(max_display_rows), "matched_data")

                    # If we have more columns with numeric data, show a sample visualization
                    numeric_cols = matched_df.select_dtypes(include=[np.number]).columns.tolist()
                    if len(numeric_cols) >= 1:
                        st.subheader("Data Visualization")
                        viz_col = st.selectbox("Select a numeric column to visualize:", numeric_cols)

                        fig = px.histogram(
                            matched_df,
                            x=viz_col,
                            title=f"Distribution of {viz_col}",
                            color_discrete_sequence=[primary_color]
                        )
                        fig.update_layout(
                            xaxis_title=viz_col,
                            yaxis_title="Count",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Summary of unmatched
                    unmatched_count = len(verified_emails) - len(matched_df)
                    if unmatched_count > 0:
                        st.subheader("Unmatched Emails Summary")
                        st.markdown(f"""
                        <div class="stats-container">
                            <p>There are <b style="color:{primary_color}">{unmatched_count:,} emails</b> from your verified list that weren't found in the full data.</p>
                            <p>Would you like to download a list of unmatched emails?</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Create unmatched emails list
                        matched_emails = set()
                        for email in matched_df[full_data_email_column]:
                            if pd.notna(email) and isinstance(email, str):
                                if not case_sensitive:
                                    matched_emails.add(email.lower())
                                else:
                                    matched_emails.add(email)

                        unmatched_emails = []
                        for email in verified_emails_df[verified_email_column]:
                            if pd.notna(email) and isinstance(email, str):
                                compare_email = email.lower() if not case_sensitive else email
                                if compare_email not in matched_emails:
                                    unmatched_emails.append({"Email": email})

                        unmatched_df = pd.DataFrame(unmatched_emails)

                        # Download button for unmatched data
                        st.markdown(
                            get_download_link(unmatched_df, "unmatched_emails.csv", "📥 Download Unmatched Emails"),
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Summary section
                    st.markdown(f"""
                    <div style="background-color: #e6f4ea; color: #137333; padding: 1rem; border-radius: 5px; border-left: 5px solid #137333;">
                    <h3>Summary</h3>
                    <p>Successfully matched <b>{len(matched_df):,}</b> out of <b>{len(verified_emails):,}</b> verified emails.</p>
                    <p>The matched data contains all columns from the full data file, but only includes rows where the email matched.</p>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.warning("No matching emails found between the two CSV files.")
                    st.markdown("""
                    Possible reasons for no matches:
                    - Email formats may be different between files
                    - Check if case sensitivity setting is appropriate
                    - Verify the correct columns are selected
                    - Examine if there are leading/trailing spaces in emails
                    """)

    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")
        st.markdown("""
        Common issues:
        - CSV file format issues
        - Column selection mismatch
        - Memory constraints with very large files

        Try uploading smaller files or check your file formats.
        """)

# Instructions when files not yet uploaded
else:
    st.info("Please upload both CSV files to begin processing.")

    # Example data section
    with st.expander("See example of expected data format"):
        st.markdown("""
        ### Example format for verified emails CSV:
        | Email | Name | Source |
        | ----- | ---- | ------ |
        | john@example.com | John | Website |
        | sarah@example.com | Sarah | Campaign |
        | mike@example.com | Mike | Referral |

        ### Example format for full data CSV:
        | ID | First Name | Last Name | ... | Email 1 | ... |
        | -- | ---------- | --------- | --- | ------- | --- |
        | 1 | John | Smith | ... | john@example.com | ... |
        | 2 | Emily | Jones | ... | emily@example.com | ... |
        | 3 | Michael | Brown | ... | mike@example.com | ... |

        The app will find records in the full data CSV where 'Email 1' matches any email in the verified emails CSV.
        """)

# Add footer
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <span style="color: #666; font-size: 0.8rem;">CSV Email Matcher v1.0</span>
    <span style="color: #666; font-size: 0.8rem;">Made for PyCharm on MacOS M2</span>
</div>
""", unsafe_allow_html=True)