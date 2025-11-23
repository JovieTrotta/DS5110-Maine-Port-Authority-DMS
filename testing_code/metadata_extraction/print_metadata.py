# IMPORTS
import os
import sys
from PyPDF2 import PdfReader
from datetime import datetime

# FUNCTIONS
def get_pdf_metadata(path):

    '''
    Parameter: full file path
    Returns: N/A

    Takes a file path as its only parameter, prints various attributes of the PDF. This uses metadata stored in the PDF's header, NOT file system meta data.
    '''

    # helper to avoid crashing on malformed timestamps
    def safe_date(value):
        '''
        Takes a raw date value and returns it safely.
        If PyPDF2 gives an empty string or malformed date, returns None instead of raising an exception.
        '''
        try:
            if not value:   # None or empty string
                return None
            if isinstance(value, datetime):  # already parsed
                return value
            # PyPDF2 strips apostrophes in odd ways sometimes
            value = value.replace("'", "")
            return datetime.strptime(value, "D:%Y%m%d%H%M%S%z")
        except Exception:
            return None

    try:
        reader = PdfReader(path)
    except Exception as e:
        print(f"ERROR: Could not open PDF — {e}")
        return

    metadata = reader.metadata

    if metadata:

        author = metadata.author
        print(f'...File Author: {author}')

        author_raw = metadata.author_raw
        print(f'...File Author: {author_raw}')

        creation_date_raw = metadata.creation_date_raw
        print(f'...File Creation Date: {creation_date_raw}')
        # print(f'...File Creation Date (Variable Type): {type(creation_date_raw)}')

        creation_date = safe_date(creation_date_raw)
        print(f'...File Creation Date: {creation_date}')
        # print(f'...File Creation Date (Variable Type): {type(creation_date)}')

        creator = metadata.creator
        print(f'...File Creator: {creator}')

        creator_raw = metadata.creator_raw
        print(f'...File Creator: {creator_raw}')
        
        modification_date_raw = metadata.modification_date_raw
        print(f'...File Modified: {modification_date_raw}')

        modification_date = safe_date(metadata.modification_date_raw)
        print(f'...File Modified: {modification_date}')

        producer = metadata.producer
        print(f'...File Producer: {producer}')

        producer_raw = metadata.producer_raw
        print(f'...File Producer: {producer_raw}')

        subject = metadata.subject
        print(f'...File Subject: {subject}')

        subject_raw = metadata.subject_raw
        print(f'...File Subject: {subject_raw}')

        title = metadata.title
        print(f'...File Title: {title}')

        title_raw = metadata.producer
        print(f'...File Title: {title_raw}')

    else:
        print("...No metadata found in this PDF!")

# MAIN
def main():

    input_directory = sys.argv[1]

    for file in os.listdir(input_directory):

        # skip whatever isn't a PDF
        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(input_directory, file)
        print(f'\nProcessing {file}...')
        get_pdf_metadata(path)

if __name__ == "__main__":
    main()
