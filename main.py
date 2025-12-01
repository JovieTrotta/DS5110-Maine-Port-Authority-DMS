# IMPORTS
from extraction.extractwsubfolders import *
from testing_code.extract_metadata import main as extract_meta_main
from document_title.documenttitling2 import main as title_files_main
from folder_organization.organizer2 import *

pdf_input_dir = "pdf_files_up"
docx_input_dir = "docx_files_up"

# MAIN
def main():

    print("...extraction completed")

    print("...running metadata function")

    extract_meta_main(pdf_input_dir)
    extract_meta_main(docx_input_dir)

    print("...running title function")

    title_files_main(docx_input_dir, pdf_input_dir)

    print("...running folder function")

if __name__ == "__main__":
    main()
