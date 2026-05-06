
import streamlit as st
import pandas as pd
import io
import sys
import os
from datetime import datetime

# Add the current directory to Python path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from contact_finder import ContactFinder
except ImportError:
    st.error("contact_finder.py not found. Please ensure it's in the same directory.")
    st.stop()

def main():
    st.set_page_config(
        page_title="Company Contact Finder",
        page_icon="📞",
        layout="wide"
    )

    st.title("📞 Company Contact Finder")
    st.markdown("---")

    st.markdown("""
    ### How it works:
    1. **Upload CSV** with columns: `company_name` (required), `director_name` (optional), `cin` (optional)
    2. **Click "Find Contacts"** to start the search process
    3. **Download** the processed CSV with phone numbers and confidence scores

    **Note:** This tool searches publicly available information only. Processing time: ~30-60 seconds per company.
    """)

    # Sidebar
    st.sidebar.header("📋 Instructions")
    st.sidebar.markdown("""
    **Required CSV Format:**
    - `company_name` (string, required)
    - `director_name` (string, optional)  
    - `cin` (string, optional)

    **Output:**
    - Original data + `phone_number` + `confidence`

    **Confidence Levels:**
    - **High**: Found on business directories
    - **Medium**: Found on company websites
    - **Low**: Found in search results
    """)

    # Sample CSV download
    st.sidebar.markdown("### 📥 Sample CSV")
    sample_data = pd.DataFrame({
        'company_name': [
            'Tata Consultancy Services',
            'Infosys Limited',
            'Reliance Industries'
        ],
        'director_name': [
            'Rajesh Gopinathan',
            'Salil Parekh', 
            'Mukesh Ambani'
        ],
        'cin': [
            'L72900MH1995PLC084781',
            'L85110KA1981PLC013115',
            'L17110MH1973PLC019786'
        ]
    })

    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    st.sidebar.download_button(
        label="Download Sample CSV",
        data=csv_buffer.getvalue(),
        file_name="sample_companies.csv",
        mime="text/csv"
    )

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📤 Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with company information"
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File uploaded successfully! Found {len(df)} companies.")

                # Validate required columns
                required_cols = ['company_name']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"❌ Missing required columns: {missing_cols}")
                    st.stop()

                # Show preview
                st.subheader("📊 Data Preview")
                st.dataframe(df.head(), use_container_width=True)

                # Validation summary
                st.info(f"""
                **Validation Summary:**
                - Total rows: {len(df)}
                - Companies with names: {df['company_name'].notna().sum()}
                - Companies with director names: {df.get('director_name', pd.Series()).notna().sum()}
                - Companies with CIN: {df.get('cin', pd.Series()).notna().sum()}
                """)

                # Limit processing for safety
                if len(df) > 50:
                    st.warning("⚠️ File contains more than 50 rows. Only first 50 will be processed for safety.")
                    df = df.head(50)

            except Exception as e:
                st.error(f"❌ Error reading CSV file: {str(e)}")
                st.stop()

    with col2:
        st.header("⚙️ Processing Options")

        if uploaded_file is not None:
            st.metric("Companies to Process", len(df))
            estimated_time = len(df) * 45  # 45 seconds per company average
            st.metric("Estimated Time", f"{estimated_time//60}m {estimated_time%60}s")

            # Process button
            if st.button("🔍 Find Contacts", type="primary", use_container_width=True):
                process_companies(df)
        else:
            st.info("👆 Upload a CSV file to begin")

def process_companies(df):
    """Process the companies and find contacts"""

    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()

    try:
        # Initialize contact finder
        status_text.text("🔧 Initializing contact finder...")
        finder = ContactFinder()

        # Process companies
        status_text.text("🔍 Starting contact search...")

        # Create a container for live results
        with st.expander("📊 Live Results", expanded=True):
            results_placeholder = st.empty()

        results = []

        for idx, row in df.iterrows():
            company_name = row.get('company_name', '').strip()
            director_name = row.get('director_name', '').strip() if 'director_name' in row else None
            cin = row.get('cin', '').strip() if 'cin' in row else None

            # Update progress
            progress = (idx + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"🔍 Processing {idx + 1}/{len(df)}: {company_name}")

            if not company_name:
                result = {
                    'phone_number': 'Not Available',
                    'confidence': 'N/A'
                }
            else:
                try:
                    result = finder.find_contact_for_company(company_name, director_name, cin)
                except Exception as e:
                    st.error(f"Error processing {company_name}: {str(e)}")
                    result = {
                        'phone_number': 'Not Available',
                        'confidence': 'N/A'
                    }

            results.append(result)

            # Update live results display
            temp_df = df.iloc[:idx+1].copy()
            temp_df['phone_number'] = [r['phone_number'] for r in results]
            temp_df['confidence'] = [r['confidence'] for r in results]

            with results_placeholder.container():
                st.dataframe(temp_df, use_container_width=True)

        # Final results
        result_df = df.copy()
        result_df['phone_number'] = [r['phone_number'] for r in results]
        result_df['confidence'] = [r['confidence'] for r in results]

        # Success message
        progress_bar.progress(1.0)
        status_text.text("✅ Processing completed!")

        # Results summary
        st.success("🎉 Contact search completed!")

        col1, col2, col3 = st.columns(3)
        with col1:
            found_count = len(result_df[result_df['phone_number'] != 'Not Available'])
            st.metric("Contacts Found", f"{found_count}/{len(result_df)}")

        with col2:
            high_conf = len(result_df[result_df['confidence'] == 'High'])
            st.metric("High Confidence", high_conf)

        with col3:
            success_rate = (found_count / len(result_df)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")

        # Display final results
        st.subheader("📋 Final Results")
        st.dataframe(result_df, use_container_width=True)

        # Download button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Download Results CSV",
            data=csv_buffer.getvalue(),
            file_name=f"company_contacts_{timestamp}.csv",
            mime="text/csv",
            type="primary"
        )

    except Exception as e:
        st.error(f"❌ An error occurred during processing: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
