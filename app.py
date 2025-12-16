import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="CSV Processor", layout="wide")

# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Analytics", "Trim Data", "Filter Data"])

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    @st.cache_data
    def load_data(file):
        return pd.read_csv(file, dtype=str)  # preserve numbers

    df = load_data(uploaded_file)

    # ==========================
    # ANALYTICS PAGE
    # ==========================
    if page == "Analytics":
        st.title("📊 CSV Analytics Report")
        st.write(f"Total rows: **{len(df)}**, Total columns: **{len(df.columns)}**")

        if "Contact" in df.columns:
            df["Contact"] = df["Contact"].astype(str)

            duplicate_count = df["Contact"].duplicated().sum()
            st.subheader("📋 Duplicates Report")
            st.write(f"Duplicate phone numbers: **{duplicate_count}**")

            VIP_PREFIXES = (
                "91120","91121","91122","91123","91124","91125",
                "91126","91127","91128","91129","91130",
                "9150","9151","9152","911","930","912","913"
            )
            vip_count = df["Contact"].str.startswith(VIP_PREFIXES).sum()
            st.subheader("🚨 VIP Numbers")
            st.write(f"VIP numbers count: **{vip_count}**")

            non9_count = (~df["Contact"].str.startswith("9")).sum()
            st.subheader("⚠️ Non-9 Numbers")
            st.write(f"Numbers not starting with 9: **{non9_count}**")
        else:
            st.warning("Column 'Contact' not found!")

    # ==========================
    # TRIM DATA PAGE
    # ==========================
    elif page == "Trim Data":
        st.title("✂️ Trim / Cut Data")
        st.info(f"Original CSV rows: **{len(df)}**")

        max_rows_to_keep = st.number_input(
            "Rows to keep",
            min_value=1,
            max_value=len(df),
            value=min(300000, len(df))
        )

        output_file_name = st.text_input("Trimmed CSV name", "trimmed_file.csv")
        remaining_file_name = st.text_input("Remaining CSV name", "remaining_file.csv")

        if st.button("Save CSVs"):
            date_str = datetime.now().strftime("%Y-%m-%d")
            folder_path = os.path.join("processed_data", date_str)
            os.makedirs(folder_path, exist_ok=True)

            df_trimmed = df.head(max_rows_to_keep)
            df_remaining = df.iloc[max_rows_to_keep:]

            df_trimmed.to_csv(os.path.join(folder_path, output_file_name), index=False)
            df_remaining.to_csv(os.path.join(folder_path, remaining_file_name), index=False)

            st.success("Files saved successfully!")

            st.download_button(
                "⬇️ Download Trimmed CSV",
                df_trimmed.to_csv(index=False).encode("utf-8"),
                output_file_name
            )

            st.download_button(
                "⬇️ Download Remaining CSV",
                df_remaining.to_csv(index=False).encode("utf-8"),
                remaining_file_name
            )

    # ==========================
    # FILTER DATA PAGE (FIXED)
    # ==========================
    elif page == "Filter Data":
        st.title("🚫 Filter & Clean Phone Numbers")
        st.info(f"Original CSV rows: **{len(df)}**")

        if "Contact" in df.columns:
            df["Contact"] = df["Contact"].astype(str).str.strip()

            # --- Remove duplicates ---
            original_count = len(df)
            df = df.drop_duplicates(subset="Contact").reset_index(drop=True)
            duplicates_removed = original_count - len(df)

            # --- Remove '251' ONLY (NO REPLACEMENT) ---
            df_before = df.copy()
            df["Contact"] = df["Contact"].apply(
                lambda x: x[3:] if x.startswith("251") else x
            )
            removed_251_count = (df_before["Contact"] != df["Contact"]).sum()

            # --- VIP Prefixes ---
            VIP_PREFIXES = [
                "91120","91121","91122","91123","91124","91125",
                "91126","91127","91128","91129","91130",
                "91150","91151","91152","930"
            ]

            custom_prefix_input = st.text_input(
                "Add custom VIP prefixes (comma separated)"
            )

            final_prefixes = VIP_PREFIXES.copy()
            if custom_prefix_input:
                final_prefixes.extend(
                    [p.strip() for p in custom_prefix_input.split(",") if p.strip()]
                )

            final_prefixes = tuple(set(final_prefixes))

            df_excluded = df[df["Contact"].str.startswith(final_prefixes)]
            df_filtered = df[~df["Contact"].str.startswith(final_prefixes)]

            # --- Summary ---
            st.subheader("📝 Cleaning Summary")
            st.write(f"✅ Duplicates removed: **{duplicates_removed}**")
            st.write(f"✅ '251' removed: **{removed_251_count}**")
            st.write(f"✅ VIP numbers removed: **{len(df_excluded)}**")

            # --- Preview ---
            st.subheader("✅ Cleaned Numbers")
            st.dataframe(df_filtered.head(10))

            st.subheader("❌ VIP Numbers Removed")
            st.dataframe(df_excluded.head(10))

            # --- Save ---
            output_file_name = st.text_input("Save cleaned CSV as", "cleaned_file.csv")
            if st.button("Save Cleaned CSV"):
                date_str = datetime.now().strftime("%Y-%m-%d")
                folder_path = os.path.join("processed_data", date_str)
                os.makedirs(folder_path, exist_ok=True)

                file_path = os.path.join(folder_path, output_file_name)
                df_filtered.to_csv(file_path, index=False)

                st.success(f"Saved: {file_path}")
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    df_filtered.to_csv(index=False).encode("utf-8"),
                    output_file_name
                )

        else:
            st.warning("Column 'Contact' not found!")
