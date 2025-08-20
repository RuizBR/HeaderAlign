import pandas as pd
import streamlit as st
from io import BytesIO
import os

# Streamlit app title
st.title("Header Alignment")
BASE_PATH = os.path.dirname(os.path.abspath(__file__))  

# Initialize header mapping and reference headers
header_mapping = {}
reference_headers = []

# Load the reference Excel file from the specified folder


# Function to map headers based on the reference file
def get_mapped_header(column_name, header_mapping):
    if column_name in header_mapping:
        return column_name

    for main_header, alt_names in header_mapping.items():
        if column_name in alt_names:
            return main_header

    return None

# Function to align headers with reference headers and retain formats
def align_headers(uploaded_df, reference_headers, header_mapping):
    aligned_df = pd.DataFrame(columns=reference_headers)
    not_found_columns = []  # List to store columns not found in the mapping

    # Iterate through the uploaded DataFrame and map the headers
    for column in uploaded_df.columns:
        mapped_header = get_mapped_header(column, header_mapping)

        if mapped_header:
            aligned_df[mapped_header] = uploaded_df[column]
        else:
            not_found_columns.append(column)  # Collect not found columns

    aligned_df = aligned_df.fillna('')  # Fill missing columns with empty strings

    # Retain data types for common columns only
    common_columns = aligned_df.columns.intersection(uploaded_df.columns)
    for col in common_columns:
        aligned_df[col] = aligned_df[col].astype(uploaded_df[col].dtype)

    return aligned_df, not_found_columns

# File uploader to accept multiple Excel formats
uploaded_file = st.file_uploader(
    "Upload an Excel file to align", 
    type=["xlsx", "xls", "xlsm"]
)

if uploaded_file:
    try:
        file_extension = uploaded_file.name.split('.')[-1]
        print(file_extension)
        file_name = uploaded_file.name.split('-')[0]
        final_file_path_header = file_name + "-header.xlsx"
        template_path = os.path.abspath(os.path.join(BASE_PATH, os.pardir, 'AddtlFiles',final_file_path_header))
        reference_df = pd.read_excel(template_path, header=0, engine='openpyxl')
        # Create header mappings
        for col in reference_df.columns:
            alternates = reference_df[col].dropna().tolist()  # Drop NaNs and convert to list
            if alternates:
                main_header = alternates[0]
                alt_names = alternates[1:]
                header_mapping[main_header] = alt_names

        reference_headers = list(header_mapping.keys())  # Extract main headers

        st.subheader("Reference File")
        st.write("Main headers from the reference file:")
        st.dataframe(pd.DataFrame([reference_headers]))
        st.write("Alternate header mappings:")
        st.dataframe(pd.DataFrame([header_mapping]))
    except Exception as e:
        st.error(f"Error reading reference file: {str(e)}")

    try:
        # Check the file extension
        if file_extension in ["xls", "xlsx", "xlsm"]:
            # Read the uploaded file with appropriate dtype settings
            df = pd.read_excel(uploaded_file, engine='openpyxl', dtype=str)

            # Convert empty strings to NaN to avoid conversion issues
            df.replace('', pd.NA, inplace=True)

            st.subheader("Uploaded File")
            st.write("Original headers of the uploaded file:")
            st.dataframe(df.columns)

            # Align the headers of the uploaded file
            aligned_df, not_found_columns = align_headers(df, reference_headers, header_mapping)

            st.subheader("Aligned File")
            st.write("Aligned version of the file:")
            st.dataframe(aligned_df)

            # Provide an option to download the aligned DataFrame as an Excel file
            def export_to_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl', mode='xlsx') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='Aligned Data')
                output.seek(0)  # Move the pointer to the start of the stream
                return output

            st.download_button(
                label="Download Aligned Excel File",
                data=export_to_excel(aligned_df).getvalue(),
                file_name="aligned_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Display the not found columns as a DataFrame
            if not_found_columns:
                not_found_df = pd.DataFrame(not_found_columns, columns=['Not Found Columns'])
                st.subheader("Columns Not Found in Reference Mapping")
                st.dataframe(not_found_df)  # Display the DataFrame

                # Provide an option to download the not found columns as a separate file
                def export_not_found_to_excel(dataframe):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl', mode='xlsx') as writer:
                        dataframe.to_excel(writer, index=False, sheet_name='Not Found Columns')
                    output.seek(0)  # Move the pointer to the start of the stream
                    return output

                st.download_button(
                    label="Download Not Found Columns",
                    data=export_not_found_to_excel(not_found_df).getvalue(),
                    file_name="not_found_columns.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        else:
            st.error("Uploaded file is not a valid Excel file.")

    except Exception as e:
        st.error(f"Error reading uploaded file: {str(e)}")

else:
    st.info("Please upload a file to align.")
