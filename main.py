# ==========================================================
# MAIN PIPELINE SCRIPT — FULL PIPELINE (NO SKIPPED STEPS)
# ==========================================================

# -------------------------------
# IMPORTS
# -------------------------------
from extraction.extractwsubfolders import main as extract_files_main
from testing_code.extract_metadata import main as extract_meta_main
from document_title.documenttitling2 import main as title_files_main
from folder_organization.organizer2 import main as organizer_main

# Working directories created during Step 1
pdf_input_dir = "pdf_files_up"
docx_input_dir = "docx_files_up"
text_dir = "ocr_text_output_2"

# -------------------------------
# MAIN FUNCTION
# -------------------------------

def main():

    print("\n=======================================")
    print(" STEP 1: File Collection + OCR Extraction")
    print("=======================================\n")
    extract_files_main()   # collects PDFs, DOCX, extracts text with OCR
    print("✔ File extraction + OCR completed.\n")

    print("=======================================")
    print(" STEP 2: Metadata Extraction")
    print("=======================================\n")
    extract_meta_main(pdf_input_dir)
    extract_meta_main(docx_input_dir)
    print("✔ Metadata extraction completed.\n")

    print("=======================================")
    print(" STEP 3: File Renaming (TXT → DOCX → PDFs)")
    print("=======================================\n")

    # Rename OCR text files + associated PDFs
    print("→ Renaming OCR text files...")
    title_files_main(text_dir, pdf_input_dir)

    # Rename DOCX files + associated PDFs
    print("→ Renaming DOCX and matching PDFs...")
    title_files_main(docx_input_dir, pdf_input_dir)

    print("✔ File renaming completed.\n")

    print("=======================================")
    print(" STEP 4: Semantic Folder Organization")
    print("=======================================\n")
    organizer_main()   # computes similarity, groups files, copies to output
    print("✔ Folder organization completed.\n")

    print("=======================================")
    print(" PIPELINE FINISHED SUCCESSFULLY 🎉")
    print("=======================================\n")


# -------------------------------
# RUN PIPELINE
# -------------------------------

if __name__ == "__main__":
    main()
