# CSV Email Matcher

A streamlined Streamlit web application for matching email addresses between two CSV files and generating a new CSV file with the matching records.

## 🚀 Features

- **Easy-to-use interface** for uploading and comparing CSV files
- **Intelligent column detection** to automatically find email columns
- **Manual column selection** options for custom matching
- **Configurable matching options**:
  - Case-sensitive or case-insensitive matching
  - Whitespace trimming
  - Duplicate email handling
- **Interactive data previews** of both source files
- **Comprehensive results** with statistics and visualizations
- **Download options** for both matched and unmatched data

## 📋 How It Works

1. **Upload two CSV files**:
   - A "verified emails" CSV containing a column with email addresses
   - A "full data" CSV containing your complete dataset with email addresses

2. **Configure matching**:
   - Select which columns to use for matching
   - Adjust matching options (case sensitivity, etc.)

3. **Process and view results**:
   - See statistics about the matching process
   - Preview the matching records
   - Download the results as a new CSV file

## 🛠️ Installation

### Local Development

1. Clone this repository
   ```bash
   git clone https://github.com/YourUsername/Streamlit-web-application-for-matching-email.git
   cd csv-email-matcher
