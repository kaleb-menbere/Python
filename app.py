import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="CSV Processor", layout="wide")

# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Analytics", "Trim Data", "Filter Data"])

# --- Upload CSV (common for all pages) ---
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    # Use st.cache_data to speed up file reading and data manipulation
    @st.cache_data
    def load_data(file):
        return pd.read_csv(file)

    df = load_data(uploaded_file)

    # --------------------------
    # Page 1: Analytics
    # --------------------------
    if page == "Analytics":
        st.title("📊 CSV Analytics Dashboard")
        st.write(f"Total rows: **{len(df)}**")
        st.write(f"Total columns: **{len(df.columns)}**")

        if "Contact" in df.columns:
            # Ensure 'Contact' is treated as string for prefix extraction
            df['Contact'] = df['Contact'].astype(str)
            
            st.write(f"Total unique phone numbers: **{df['Contact'].nunique()}**")

            # --- Duplicate Analysis ---
            st.subheader("📋 Duplicate Phone Numbers List")
            duplicates = df[df['Contact'].duplicated(keep=False)].sort_values('Contact')
            duplicate_count = len(duplicates)
            st.write(f"Number of duplicate phone numbers: **{duplicate_count}**")

            if not duplicates.empty:
                duplicates_preview = duplicates.copy()
                duplicates_preview.index = duplicates_preview.index + 1  # start index from 1
                st.dataframe(duplicates_preview)
            else:
                st.success("No duplicates found ✅")
            
            # --- Prefix Analytics ---
            st.subheader("📞 Top 10 Prefixes (first 3 digits)")
            df['Prefix_3'] = df['Contact'].str[:3]
            top_prefixes = df['Prefix_3'].value_counts().head(10)
            st.table(top_prefixes)
            
            st.subheader("📞 Top 10 First 6 Digits")
            df['Prefix_6'] = df['Contact'].str[:6]
            top_6 = df['Prefix_6'].value_counts().head(10)
            st.table(top_6)
            
            # --- Non-'9' Starting Contacts Report (NEW FEATURE) ---
            st.subheader("🚫 Non-'9' Starting Contacts Report")
            
            # Filter for numbers that DO NOT start with '9'
            non_9_starters = df[~df['Contact'].str.startswith('9')]
            
            if not non_9_starters.empty:
                count_non_9 = len(non_9_starters)
                percentage_non_9 = (count_non_9 / len(df)) * 100
                
                st.error(f"**{count_non_9}** contacts ({percentage_non_9:.2f}%) **DO NOT** start with '9'.")
                
                # Show a preview and provide download
                non_9_starters_preview = non_9_starters.copy()
                non_9_starters_preview.index = non_9_starters_preview.index + 1
                st.dataframe(non_9_starters_preview.head(10))
                
                st.download_button(
                    label="⬇️ Download Non-'9' List",
                    data=non_9_starters.to_csv(index=False).encode('utf-8'),
                    file_name="non_9_starters.csv",
                    mime='text/csv'
                )
            else:
                st.success("All contacts start with '9' ✅")

            # --- Preview ---
            st.subheader("Preview of first 10 rows")
            preview_df = df.head(10).copy()
            preview_df.index = preview_df.index + 1  # start index from 1
            st.dataframe(preview_df)
        else:
            st.warning("Column 'Contact' not found in your uploaded file!")

    # --------------------------
    # Page 2: Trim Data
    # --------------------------
    elif page == "Trim Data":
        st.title("✂️ Trim / Cut Data")

        st.info(f"Original CSV has **{len(df)} rows**")

        # Input: Number of rows to trim
        max_rows_to_keep = st.number_input(
            "Enter number of rows to keep",
            min_value=1,
            max_value=len(df),
            value=min(300000, len(df)),
            help="The top N rows will be saved as the trimmed file."
        )

        # Input: File names
        output_file_name = st.text_input("Enter file name for trimmed CSV:", value="trimmed_file.csv")
        remaining_file_name = st.text_input("Enter file name for remaining CSV:", value="remaining_file.csv")

        st.subheader("Summary")
        st.write(f"You will save **{max_rows_to_keep} rows** as file: **{output_file_name}**")
        st.write(f"The remaining **{len(df) - max_rows_to_keep} rows** will be saved as: **{remaining_file_name}**")

        # Save button
        if st.button("Save CSVs"):
            date_str = datetime.now().strftime("%Y-%m-%d")
            folder_path = os.path.join("processed_data", date_str)
            os.makedirs(folder_path, exist_ok=True)

            # Split the DataFrame
            df_trimmed = df.head(max_rows_to_keep)
            df_remaining = df.tail(len(df) - max_rows_to_keep)

            # Save files
            trimmed_path = os.path.join(folder_path, output_file_name)
            remaining_path = os.path.join(folder_path, remaining_file_name)

            df_trimmed.to_csv(trimmed_path, index=False)
            df_remaining.to_csv(remaining_path, index=False)

            st.success(f"Trimmed file saved in: {trimmed_path}")
            st.success(f"Remaining file saved in: {remaining_path}")

            # Download buttons
            st.download_button(
                label="⬇️ Download Trimmed CSV",
                data=df_trimmed.to_csv(index=False).encode('utf-8'),
                file_name=output_file_name,
                mime='text/csv'
            )
            st.download_button(
                label="⬇️ Download Remaining CSV",
                data=df_remaining.to_csv(index=False).encode('utf-8'),
                file_name=remaining_file_name,
                mime='text/csv'
            )

    # --------------------------
    # Page 3: Filter Data
    # --------------------------
    elif page == "Filter Data":
        st.title("🚫 Filter Phone Numbers")
        st.info(f"Original CSV has **{len(df)} rows**")

        if "Contact" in df.columns:
            df['Contact'] = df['Contact'].astype(str)

            # 1. List duplicate values
            st.subheader("📋 Duplicate Phone Numbers")
            duplicates = df[df['Contact'].duplicated(keep=False)].sort_values('Contact')
            if not duplicates.empty:
                preview_dups = duplicates.copy()
                preview_dups.index = preview_dups.index + 1
                st.dataframe(preview_dups.head(10))
            else:
                st.success("No duplicates found ✅")

            # 2. VIP prefixes to exclude (numbers starting with these)
            BASE_EXCLUDE_PREFIXES = [
                "91120", "91121", "91122", "91123", "91124", "91125",
                "91126", "91127", "91128", "91129", "91130",
                "9150", "9151", "9152",
                "911", "930", "912", "913"
            ]

            st.subheader("⚠️ VIP Phone Number Prefixes to Exclude")
            
            # --- Prefix Removal Feature (NEW) ---
            selected_prefixes = st.multiselect(
                "Select prefixes to EXCLUDE (uncheck to keep numbers starting with it)",
                options=BASE_EXCLUDE_PREFIXES,
                default=BASE_EXCLUDE_PREFIXES, # By default, all are excluded
                help="Uncheck a prefix to remove it from the exclusion list and KEEP numbers starting with it."
            )
            
            # --- Custom Prefix Addition Feature ---
            custom_prefix_input = st.text_input(
                "Add custom prefixes to exclude (comma separated, e.g., 901, 902)"
            )
            
            # Combine the lists
            current_exclude_prefixes = list(selected_prefixes)
            if custom_prefix_input:
                custom_list = [p.strip() for p in custom_prefix_input.split(",") if p.strip()]
                current_exclude_prefixes.extend(custom_list)
            
            # Ensure the final list is a tuple for filtering and remove duplicates/empty strings
            final_exclude_prefixes = tuple(sorted(set(p for p in current_exclude_prefixes if p)))

            st.markdown(f"**Final Excluded Prefixes:** `{', '.join(final_exclude_prefixes)}`")

            # 3. Filter the DataFrame
            if not final_exclude_prefixes:
                st.warning("No prefixes are currently excluded. All rows will be kept.")
                df_kept = df.copy()
                df_excluded = pd.DataFrame(columns=df.columns)
            else:
                df_filtered = df.copy()
                
                # Excluded: contacts STARTING with any of the final prefixes
                df_excluded = df_filtered[
                    df_filtered['Contact'].str.startswith(final_exclude_prefixes)
                ]
                
                # Kept: contacts NOT STARTING with any of the final prefixes
                df_kept = df_filtered[
                    ~df_filtered['Contact'].str.startswith(final_exclude_prefixes)
                ]

            # Show results
            st.subheader("✅ Filtered (Kept) Numbers")
            st.write(f"Total rows after filtering: **{len(df_kept)}**")
            preview_kept = df_kept.head(10).copy()
            preview_kept.index = preview_kept.index + 1
            st.dataframe(preview_kept)

            st.subheader("❌ Excluded VIP Numbers")
            st.write(f"Total VIP numbers excluded: **{len(df_excluded)}**")
            preview_excluded = df_excluded.head(10).copy()
            preview_excluded.index = preview_excluded.index + 1
            st.dataframe(preview_excluded)
            
            # 4. Save filtered CSV
            output_file_name = st.text_input("Enter file name to save filtered CSV:", value="filtered_file.csv")
            if st.button("Save Filtered CSV"):
                date_str = datetime.now().strftime("%Y-%m-%d")
                folder_path = os.path.join("processed_data", date_str)
                os.makedirs(folder_path, exist_ok=True)

                file_path = os.path.join(folder_path, output_file_name)
                df_kept.to_csv(file_path, index=False)

                st.success(f"Filtered file saved in: {file_path}")
                st.download_button(
                    label="⬇️ Download Filtered CSV",
                    data=df_kept.to_csv(index=False).encode('utf-8'),
                    file_name=output_file_name,
                    mime='text/csv'
                )
        else:
            st.warning("Column 'Contact' not found!")