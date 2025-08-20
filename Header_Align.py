import pandas as pd
import streamlit as st
from io import BytesIO
import os

# Streamlit app title
st.title("Header Alignment")

# Base path of the script (repo root in Streamlit Cloud)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Initialize header mapping and reference headers
header_mapping = {}
reference_headers = []


# ---------------------------
# Functions
# ---------------------------
def get_mapped_header(column_name, header_mapping):
    """Map uploaded column to reference header."""
    if column_name in header_mapping:
        return column_name

    for main_header, alt_names in header_mapping.items():
        if column_name in alt_names:
            return main_header

    return None


def align_headers(uploaded_df, reference_headers, header_mapping):
    """Align headers of uploaded file to reference headers."""
    aligned_df = pd.DataFrame(columns=reference_headers)
    not_found_columns = []

    for column in uploaded_df.columns:
        mapped_header = get_mapped_header(column, header_mapping)
        if mapped_header:
            aligned_df[mapped_header] = uploaded_df[column]
        else:
            not_found_columns.append(column)

    aligned_df = aligned_df.fillna("")

    # Keep data types where possible
    common_columns = aligned_df.columns.intersection(uploaded_df.columns)
    for col in common_columns:
        aligned_df[col] = aligned_df[col].astype(uploaded_df[col].dtype)

    return aligned_df, not_found_columns


def export_to_excel(dataframe, sheet_name="Aligned Data"):
    """Export dataframe to in-memory Excel file."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output


# ---------------------------
# Upload section
# ---------------------------
uploaded_file = st.file_uploader(
    "Upload an Excel file to align",
    type=["xlsx", "xls", "xlsm"]
)

if uploaded_file:
    try:
        file_extension = uploaded_file.name.split('.')[-1]
        file_name = uploaded_file.name.split('-')[0]
        final_file_path_header = file_name + "-header.xlsx"

        # Path to reference file in AddtlFiles/
        template_path = os.path.join(BASE_PATH, "AddtlFiles", final_file_path_header)

        # If reference file missing, allow manual upload
        if os.path.exists(template_path):
            reference_df = pd.read_excel(template_path, header=0, engine="openpyxl")
        else:
            st.warning(f"Reference file not found at {template_path}")
            ref_file = st.file_uploader("Upload reference header file", type=["xlsx"], key="ref")
            if ref_file is not None:
                reference_df = pd.read_excel(ref_file, header=0, engine="openpyxl")
            else:
                st.stop()

        # Create header mappings
        for col in reference_df.columns:
            alternates = reference_df[col].dropna().tolist()
            if alternates:
                main_header = alternates[0]
                alt_names = alternates[1:]
                header_mapping[main_header] = alt_names

        reference_headers = list(header_mapping.keys())

        st.subheader("Reference File")
        st.write("Main headers from the reference file:")
        st.dataframe(pd.DataFrame([reference_headers]))
        st.write("Alternate header mappings:")
        st.dataframe(pd.DataFrame([header_mapping]))

    except Exception as e:
        st.error(f"Error reading reference file: {str(e)}")
        st.stop()

    try:
        if file_extension in ["xls", "xlsx", "xlsm"]:
            df = pd.read_excel(uploaded_file, engine="openpyxl", dtype=str)
            df.replace("", pd.NA, inplace=True)

            st.subheader("Uploaded File")
            st.write("Original headers of the uploaded file:")
            st.dataframe(df.columns)

            # Align headers
            aligned_df, not_found_columns = align_headers(df, reference_headers, header_mapping)

            st.subheader("Aligned File")
            st.write("Aligned version of the file:")
            st.dataframe(aligned_df)

            # Download aligned file
            st.download_button(
                label="Download Aligned Excel File",
                data=export_to_excel(aligned_df).getvalue(),
                file_name="aligned_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Show & download not found columns
            if not_found_columns:
                not_found_df = pd.DataFrame(not_found_columns, columns=["Not Found Columns"])
                st.subheader("Columns Not Found in Reference Mapping")
                st.dataframe(not_found_df)

                st.download_button(
                    label="Download Not Found Columns",
                    data=export_to_excel(not_found_df, "Not Found Columns").getvalue(),
                    file_name="not_found_columns.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        else:
            st.error("Uploaded file is not a valid Excel file.")

    except Exception as e:
        st.error(f"Error reading uploaded file: {str(e)}")

else:
    st.info("Please upload a file to align.")
