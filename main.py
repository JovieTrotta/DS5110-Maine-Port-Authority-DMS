# IMPORTS
from extraction.extractwsubfolders import *
from testing_code.extract_metadata import main as extract_meta_main

pdf_input_dir = "pdf_files_up"
docx_input_dir = "docx_files_up"

# MAIN
def main():

    extract_meta_main(pdf_input_dir)
    extract_meta_main(docx_input_dir)

    print("hello world")

if __name__ == "__main__":
    main()
