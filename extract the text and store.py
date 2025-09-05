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
import pdfplumber
from difflib import SequenceMatcher


# Load in the dataset
full_df = pd.read_excel("draftMeasures_en (2).xlsx")

# Create a new variable that only contains the first part of the document number
full_df['D_ID'] = full_df['Document'].str.split('/').str[0]

# Create a new variable 'version' that takes everything after '/' in Document
full_df['version'] = full_df['Document'].str.split('/').str[1]
full_df["version"] = full_df["version"].astype(str).str.lstrip("0")  # remove leading zeros




# Combine Document and Document title into one variable
full_df['D_ID_and_Title'] = full_df['D_ID'].astype(str) + " - " + full_df['Document title'].astype(str)

# Combine Document and Document title into one variable
full_df['Document_and_Title'] = full_df['Document'].astype(str) + " - " + full_df['Document title'].astype(str)

# Create an order variable: 'a', 'b', 'c', ... for each Document/version group
def num_to_letter(n):
    # n is zero-based
    return chr(ord('a') + n)

full_df['order'] = (
    full_df.groupby(['Document'])
    .cumcount()
    .map(num_to_letter)
)

# Count the number of unique D_ID values
print("Unique D_IDs:", full_df['D_ID'].nunique())

# Count the number of unique combinations of Document and Document title
print("Unique D_IDs:", full_df['Document_and_Title'].nunique())

# Count the number of unique Document values
print("Unique Documents:", full_df['Document'].nunique())

# Count the number of rows in full_df
print("Number of rows in full_df:", len(full_df))


# Frequency table of version variable
version_freq = full_df['version'].value_counts()
print("Frequency table of 'version':")
print(version_freq)


#Find out how many 2 or third versions that do not have 1 first verison with same title to find out how many titles have been updated. 
v02_rows = full_df[full_df['version'] == "02"]
v01_titles = set(full_df.loc[full_df['version'] == "01", 'D_ID_and_Title'])
missing_v01_count = (~v02_rows['D_ID_and_Title'].isin(v01_titles)).sum()
print("Number of version '02' rows without a matching version '01' (same D_ID_and_Title):", missing_v01_count)

# Print again
print("Number of version '02' rows without a matching version '01' (same D_ID_and_Title):", missing_v01_count)


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

print("Variables in df_vdl:", df_vdl.columns.tolist())

empty_file_count = df_vdl['File'].isna().sum() + (df_vdl['File'].astype(str).str.strip() == "").sum()
print("Number of rows in df_vdl where File is empty or NaN:", empty_file_count)

#antal filer siden 30-11-2019
32226-4925
#27301 filer

df_vdl.head(100).to_excel("df_vdl_test.xlsx", index=False)

df_vdl.to_excel("df_vdl.xlsx", index=False)




# Select the bottom 25% rows of df_vdl and store in df_newest
bottom_05pct_count = int(len(df_vdl) * 0.01)
df_oldest_01_pct = df_vdl.head(bottom_05pct_count)




print("Number of rows in df_newest (bottom 0,5%):", len(df_oldest_01_pct))





#Definining the fucntion to ectract and fetch data from the links in the File column
def fetch_and_extract_text_and_format(url):
    if pd.isna(url) or str(url).strip() == "":
        print("Empty file link encountered.")
        return ("", "empty file")

    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "").lower()

        # Handle Word (.docx)
        if (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type
            or str(url).endswith(".docx")
        ):
            file_stream = BytesIO(resp.content)
            doc = Document(file_stream)
            text = "\n".join([para.text for para in doc.paragraphs])
            fmt = "Word"

        # Handle PDF
        elif "application/pdf" in content_type or str(url).endswith(".pdf"):
            file_stream = BytesIO(resp.content)
            text_chunks = []
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_chunks.append(page_text)
            text = "\n".join(text_chunks) if text_chunks else "[No text found in PDF]"
            fmt = "PDF"

        # Handle HTML
        elif "text/html" in content_type or "<html" in resp.text.lower():
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            fmt = "HTML"

        # Everything else
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
df_oldest_01_pct[["text", "format"]] = [fetch_and_extract_text_and_format(url) for url in tqdm(df_oldest_01_pct["File"], desc="Processing files")]

print("Text and format extraction complete.")


# Write df_newest to CSV in the current folder
df_oldest_01_pct.to_excel("df_oldest_01_pct.xlsx", index=False)




#---------------------------Comparison of the text values--------------------------

print("Number of rows in df_newest (bottom 0,5%):", len(df_oldest_01_pct))

df_oldest_01_pct_nonempty = df_oldest_01_pct[
    df_oldest_01_pct['File'].notna() & (df_oldest_01_pct['File'].str.strip() != "")
] #259 rows

df_oldest_01_pct_nonempty = df_oldest_01_pct_nonempty[~df_oldest_01_pct_nonempty['text'].str.contains("Unsupported content", na=False)]
#224 rows


print("Number of rows in df_newest (bottom 0,5%):", len(df_oldest_01_pct_nonempty))

df=df_oldest_01_pct_nonempty

df["version"] = df["version"].astype(str).str.lstrip("0")  # remove leading zeros

df['version'] = pd.to_numeric(df['version'], errors='coerce')

#df = df[['D_ID', 'order', 'text', 'version']]

v1 = df[df['version'] == 1]

# Get highest version rows per (D_id, order)
vmax = df.loc[df.groupby(['D_ID', 'order'])['version'].idxmax()]

# Merge them side-by-side
merged = pd.merge(
    v1, vmax,
    on=['D_ID', 'order'],
    suffixes=('_v1', '_vmax')
)

# Compare text similarity
merged['similarity'] = merged.apply(
    lambda row: SequenceMatcher(None, row['text_v1'], row['text_vmax']).ratio(),
    axis=1
)

# Compare format variable
merged['format_compare'] = merged.apply(
    lambda row: "same" if row['format_v1'] == row['format_vmax'] else "not similar",
    axis=1
)

pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.width', None)        # don't wrap columns
print(merged[['D_ID', 'order', 'version_v1', 'version_vmax', 'similarity', 'format_compare']])


df.to_excel("df_test.xlsx", index=False)
