import sys
print(sys.executable)

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from docx import Document
import os
import time
from tqdm import tqdm

# Load in the dataset
full_df = pd.read_excel("draftMeasures_en (2).xlsx")

# Create a new variable that only contains the first part of the document number
full_df['D_ID'] = full_df['Document'].str.split('/').str[0]

# Count the number of unique D_ID values
print("Unique D_IDs:", full_df['D_ID'].nunique())

# Count the number of unique Document values
print("Unique Documents:", full_df['Document'].nunique())

# Count the number of rows in full_df
print("Number of rows in full_df:", len(full_df))



#--------------------------NEW DF BASED ON DATE FILTER----------------------------

# Get D_IDs with "Dossier end date" after 30-11-2019
end_date_cutoff = pd.to_datetime("30-11-2019", format="%d-%m-%Y")
filtered_ids = full_df.loc[pd.to_datetime(full_df['Dossier end date'], format="%d-%m-%Y") > end_date_cutoff, 'D_ID'].unique()

# Create new df with only rows where D_ID is in filtered_ids
df_vdl = full_df[full_df['D_ID'].isin(filtered_ids)]

# Count the number of unique D_ID values
print("Unique D_IDs in df_vdl:", df_vdl['D_ID'].nunique())

# Count the number of unique Document values
print("Unique Documents in df_vdl:", df_vdl['Document'].nunique())

# Count the number of rows in df_vdl
print("Number of rows in df_vdl:", len(df_vdl))

# Select the bottom 25% rows of df_vdl and store in df_newest
bottom_5pct_count = int(len(df_vdl) * 0.05)
df_newest = df_vdl.tail(bottom_5pct_count)

print("Number of rows in df_newest (bottom 5%):", len(df_newest))





#Definining the fucntion to ectract and fetch data from the links in the File column
def fetch_and_extract_text_and_format(url):
    if pd.isna(url) or str(url).strip() == "":
        print("Empty file link encountered.")
        return ("", "empty file")
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "").lower()
        if (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type
            or str(url).endswith(".docx")
        ):
            file_stream = BytesIO(resp.content)
            doc = Document(file_stream)
            text = "\n".join([para.text for para in doc.paragraphs])
            fmt = "Word"
        elif "text/html" in content_type or "<html" in resp.text.lower():
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            fmt = "html"
        else:
            text = f"[Unsupported content type: {content_type}]"
            fmt = "Other format"
        print(f"Success: Retrieved text from {url} ({fmt})")
        time.sleep(3)
        return (text, fmt)
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        time.sleep(3)
        return (f"[Error: {e}]", "Other format")

# Apply the function to the File column with progress bar and create two new columns: text and format
df_newest[["text", "format"]] = [fetch_and_extract_text_and_format(url) for url in tqdm(df_newest["File"], desc="Processing files")]

print("Text and format extraction complete.")

# Write df_newest to CSV in the current folder
df_newest.to_csv("df_newest.csv", index=False)




