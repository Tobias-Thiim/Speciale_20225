#load in the dataset
library(readxl)
full_df <- read_excel("draftMeasures_en (2).xlsx")


#I create a new variable that only contain the first part of the document number
full_df$D_ID <- sub("/.*", "", full_df$Document)

# Count the number of unique D_ID values
length(unique(full_df$D_ID)) #= 31405

# Count the number of unique D_ID values
length(unique(full_df$Document)) #= 45701


# Count the number of rows in df_vdl --> Some Document numbers appear multiple times 
nrow(full_df) #=80080



nrow(full_df)
nrow(df_vdl)
nrow(df_vdl_nonempty_file)





#-----------------------------NEW shorter DF ------------------------------

#Now i want to find a deep all documents, where the final version was adopted or rejected after 30-11-2019
#I cant simply just take the "Dossier end data", beaucse maybe some documents have preeceded versions adopted or rejected after 30-11-2019
#I therefore make a list of all D_IDs, where any version was adopted or rejected after 30-11-2019 and then i keep all versions of these D_IDs in the dataset

# Get D_IDs with "Dossier end date" after 30-11-2019 --> VDL stepped in the next day
end_date_cutoff <- as.Date("30-11-2019", format = "%d-%m-%Y")

#Using a logical vector, extract the corresponding values from full_df$D_ID. All dates above the cutoff date. 
filtered_ids <- full_df$D_ID[as.Date(full_df$`Dossier end date`, format = "%d-%m-%Y") > end_date_cutoff]
filtered_ids <- unique(filtered_ids)

# Create new df with only rows where D_ID is in filtered_ids
df_vdl <- full_df[full_df$D_ID %in% filtered_ids, ]

# Count the number of unique D_ID values
length(unique(df_vdl$D_ID)) #= 12068

# Count the number of unique D_ID values
length(unique(df_vdl$Document)) #= 17306

#counting rows
nrow(df_vdl) #=32226

# Print the 10 most frequent Document values and their counts in df_vdl
top_documents <- sort(table(full_df$Document), decreasing = TRUE)[1:10]
print(top_documents)

num_documents_more_than_once <- sum(table(full_df$Document) > 1)
print(num_documents_more_than_once) #26519 document numbers appear more than once
#meaning approx 53500 document numbers appear only once

#all docuemnt that appear more than once have same satus
status_counts_per_document <- tapply(df_vdl$Status, df_vdl$Document, function(x) length(unique(x)))
# Filter those with more than 1 unique Status
multiple_status_docs <- status_counts_per_document[status_counts_per_document > 1]
cat("Number of Document values with multiple Status values:", length(multiple_status_docs), "\n")


#all docuemnt that appear more than do not have reference to the same file
status_counts_per_document <- tapply(df_vdl$File, df_vdl$Document, function(x) length(unique(x)))
# Filter those with more than 1 unique Status
multiple_file_docs <- status_counts_per_document[status_counts_per_document > 1]
cat("Number of Document values with multiple file values:", length(multiple_file_docs), "\n")
#more 1000 document numbers appear with different files These are often anexes or related documents to the main document, so maybe check document title


# Only consider rows where File is not empty
df_vdl_nonempty_file <- df_vdl[trimws(df_vdl$File) != "" & !is.na(df_vdl$File), ]

status_counts_per_document_nonempty <- tapply(df_vdl_nonempty_file$File, df_vdl_nonempty_file$Document, function(x) length(unique(x)))
multiple_file_docs_nonempty <- status_counts_per_document_nonempty[status_counts_per_document_nonempty > 1]
cat("Number of Document values with multiple non-empty file values:", length(multiple_file_docs_nonempty), "\n")


# Print ten examples of Document values with multiple non-empty File values and their File links
example_docs <- names(multiple_file_docs_nonempty)[1:10]
for (doc in example_docs) {
  cat("Document:", doc, "\n")
  print(unique(df_vdl_nonempty_file$File[df_vdl_nonempty_file$Document == doc]))
  cat("\n")
}




# Count different values of 'File'
table(full_df$Status)


# Check if 'File' is a character/text variable and if it contains links
is.character(aviation_data$File)
head(aviation_data$File)

# Optionally, check if values look like links (contain 'http')
any(grepl("http", aviation_data$File))

# Create new variable D_ID by removing everything after and including '/'
all_draft$D_ID <- sub("/.*", "", all_draft$Document)


head(all_draft$D_ID)

# Count the number of unique D_ID values
length(unique(all_draft$D_ID))

# Find the most frequent D_ID and its count
d_id_counts <- table(all_draft$D_ID)
most_common_d_id <- names(which.max(d_id_counts))
most_common_count <- max(d_id_counts)
most_common_d_id
most_common_count

# Count how many D_IDs appear more than once
sum(d_id_counts > 1)

table(all_draft$Status)

# Count different values of procedure for a given value of Status
table(full_df$Procedure[full_df$Status == "Adopted by Commission"])

# Get D_IDs with "Dossier end date" after 30-11-2019
end_date_cutoff <- as.Date("30-11-2019", format = "%d-%m-%Y")
filtered_ids <- full_df$D_ID[as.Date(full_df$`Dossier end date`, format = "%d-%m-%Y") > end_date_cutoff]
filtered_ids <- unique(filtered_ids)
filtered_ids
# Count different values of procedure for a given value of Status
table(full_df$Procedure[full_df$Status == "Adopted by Commission"])

# Get D_IDs with "Dossier end date" after 30-11-2019
end_date_cutoff <- as.Date("30-11-2019", format = "%d-%m-%Y")
filtered_ids <- full_df$D_ID[as.Date(full_df$`Dossier end date`, format = "%d-%m-%Y") > end_date_cutoff]
filtered_ids <- unique(filtered_ids)
filtered_ids

# For each Document in df_vdl, count number of unique Status values

# Count number of Document values that appear more than once
num_documents_more_than_once <- sum(table(full_df$Document) > 1)
print(num_documents_more_than_once)




