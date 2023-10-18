import pandas as pd
import streamlit as st
from io import BytesIO
import zipfile

def create_excel_file(df):
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx', options={'remove_timezone': True}) as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return excel_file.getvalue()

def process_and_save_files(uploaded_files):
    processed_files = []

    for i, file in enumerate(uploaded_files):
        df = pd.read_excel(file)

        def replace_words_v2(description, row):
            if not isinstance(description, str):  # Controleren of de beschrijving een string is
                return description

            for header in df.columns:
                if header in description:
                    value = row[header]
                    if pd.isna(value):  # Als de waarde NaN is, sla deze kolom over
                        continue
                    description = description.replace(f'[{header}]', str(value))
            return description

        # Update de beschrijvingen in de 'Product description' kolom opnieuw
        df['Product description updated'] = df.apply(lambda row: replace_words_v2(row['Product description'], row), axis=1)

        # Save the processed Excel file
        excel_data = create_excel_file(df)
        processed_files.append({'name': f'processed_file_{i}.xlsx', 'data': excel_data})

    return processed_files

st.title("Multiple File Upload and Processing")

# Upload multiple files
uploaded_files = st.file_uploader("Upload Files", type="xlsx", accept_multiple_files=True)

if uploaded_files is not None and len(uploaded_files) > 0:
    processed_files = process_and_save_files(uploaded_files)

    # Create a zip archive containing all processed files
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_info in processed_files:
            zipf.writestr(file_info['name'], file_info['data'])

    # Provide download link for the zip archive
    st.download_button(label='Download All Processed Files', data=zip_buffer.getvalue(), file_name='processed_files.zip')

# Display processed files individually
for i, file_info in enumerate(processed_files):
    st.subheader(f"Processed File {i + 1}")
    st.download_button(label=f'Download Processed File {i + 1}', data=file_info['data'], file_name=file_info['name'])
