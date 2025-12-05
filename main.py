# MAIN PIPELINE SCRIPT

# -----------------------------------------
# IMPORTS
# -----------------------------------------
from extraction.extractwsubfolders import main as extract_files_main
from testing_code.extract_metadata import main as extract_meta_main
from document_title.documenttitling2 import main as title_files_main
from folder_organization.organizer2 import main as organizer_main

# Working directories created during extraction
pdf_input_dir = "pdf_files_up"
docx_input_dir = "docx_files_up"

# -----------------------------------------
# MAIN PIPELINE FUNCTION
# -----------------------------------------

def main():

    print("\n==============================")
    print(" STEP 1: File Extraction")
    print("==============================")
    extract_files_main()
    print("✔ File collection and text extraction completed.\n")

    print("==============================")
    print(" STEP 2: Metadata Extraction")
    print("==============================")
    extract_meta_main(pdf_input_dir)
    extract_meta_main(docx_input_dir)
    print("✔ Metadata extraction completed.\n")

    print("==============================")
    print(" STEP 3: File Renaming")
    print("==============================")
    title_files_main(docx_input_dir, pdf_input_dir)
    print("✔ File renaming completed.\n")

    print("==============================")
    print(" STEP 4: Folder Organization")
    print("==============================")
    organizer_main()
    print("✔ Folder organization completed.\n")

    print("=======================================")
    print(" PIPELINE FINISHED SUCCESSFULLY! 🎉")
    print("=======================================\n")

# -----------------------------------------
# RUN MAIN PIPELINE
# -----------------------------------------

if __name__ == "__main__":
    main()

