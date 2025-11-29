# IMPORTS
import os
import sys
import docx
from PyPDF2 import PdfReader
from datetime import datetime

# FUNCTIONS
def get_file_extension(path):

    '''
    Parameter: full file path
    Returns: file extension as a string

    This is used to extract the file extension so we can tell if a file is a doc, pdf, etc.
    '''

    # turn the file name and extension into a tuple
    file_tuple = os.path.splitext(path)

    # separate the file name and extension
    file_name = file_tuple[0]
    file_extension = file_tuple[1]
    
    return file_extension

def count_metadata(date_list, date):
    
    '''
    Parameter: a list and a date (as datetime object)
    Returns: N/A

    Adds the date to the list. This is used to keep track of all the dates our program has extracted form metadata. 
    '''
    
    date_list.append(date)

def safe_date(value):
    
    '''
    Parameter: a datetime object ideally, if not a date string like D:%Y%m%d%H%M%S%z
    Returns: a datetime object or None

    Helps prevent errors if the value is empty or funky in any way.
    '''

    try:
        
        # if empty, stop
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        # prevents any stray apostrophes from throwing this whole thing off 
        cleaned = value.replace("'", "")

        # returns the string as a datetime object for simplicity 
        return datetime.strptime(cleaned, "D:%Y%m%d%H%M%S%z")

    except Exception:
        
        print("...Something didn't work.")
        return None

def get_pdf_metadata(path):

    '''
    Parameter: full file path
    Returns: a datetime object or None

    Takes a PDF's file path as its only parameter, returns the datetime object associated with the file or None.
    '''

    try:
        
        reader = PdfReader(path)
        
    except Exception as e:

        print(f"...Could not open PDF at {path}")
        print(f"...ERROR: {e}")
        return None

    metadata = reader.metadata

    # no metadata at all
    if not metadata:
        print(f"...No metadata found at {path}!")
        return None

    # first check for the datetime object
    if safe_date(metadata.get("/CreationDate")):

        print(f'...File Creation Date: {safe_date(metadata.get("/CreationDate"))}')
        return safe_date(metadata.get("/CreationDate"))

    # then we settle for the raw date string
    elif safe_date(metadata.creation_date_raw):
        
        print(f'...File Creation Date: {safe_date(metadata.creation_date_raw)}')
        return safe_date(metadata.creation_date_raw)

    # nothing could be found
    else:

        print((f"...No metadata date could be found at {path}!"))
        return None

def get_docx_metadata(path):

    '''
    Parameter: full file path
    Returns: a datetime object or None

    Takes a DOC's file path as its only parameter, returns the datetime object associated with the file or None.
    '''

    try:
        
        doc = docx.Document(path)
        prop = doc.core_properties
        
    except Exception as e:

        print(f"...Could not open DOCX at {path}")
        print(f"...ERROR: {e}")
        return None
    
    # first check for the datetime object
    if safe_date(prop.created):

        print(f'...File Creation Date: {safe_date(prop.created)}')
        return safe_date(prop.created)

    # nothing could be found
    else:

        print((f"...No metadata date could be found at {path}!"))
        return None

# MAIN
def main():

    date_list = []

    # swap this with our input folder path if we choose that route
    input_directory = sys.argv[1]

    for root, dirs, files in os.walk(input_directory):
        
        for file in files:
            
            path = os.path.join(root, file)
            ext = get_file_extension(path).lower()

            if ext == ".docx":
                print(f"\nProcessing DOCX: {path}")
                date = get_docx_metadata(path)
                count_metadata(date_list, date)

            elif ext == ".pdf":
                print(f"\nProcessing PDF: {path}")
                date = get_pdf_metadata(path)
                count_metadata(date_list, date)

            else:
                print(f"\nSkipping unsupported file type: {path}")
    
    metadata_found = 0
    metadata_not_found = 0

    for item in date_list:
        
        if item is not None:
            
            metadata_found += 1
            # print(item)
            
        else:
            
            metadata_not_found += 1

    print("\nMETADATA SUMMARY: ")
    print(f"Number of files with embedded metadata - {metadata_found}")
    print(f"Number of files without embedded metadata - {metadata_not_found}")

if __name__ == "__main__":
    main()
