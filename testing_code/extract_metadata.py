import os
import sys
import docx
from PyPDF2 import PdfReader
from datetime import datetime

# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------

def get_file_extension(path):
    """Returns the file extension as a string."""
    return os.path.splitext(path)[1]


def count_metadata(date_list, date):
    """Adds a metadata datetime (or None) to our tracking list."""
    date_list.append(date)


def safe_date(value):
    """
    Safely converts metadata date values to datetime objects.
    Accepts raw PDF date strings or datetime objects.
    """

    try:
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        cleaned = value.replace("'", "")
        return datetime.strptime(cleaned, "D:%Y%m%d%H%M%S%z")

    except Exception:
        print("...Something didn't work.")
        return None


def get_pdf_metadata(path):
    """Returns PDF creation date as datetime or None."""

    try:
        reader = PdfReader(path)
    except Exception as e:
        print(f"...Could not open PDF at {path}")
        print(f"...ERROR: {e}")
        return None

    metadata = reader.metadata

    if not metadata:
        print(f"...No metadata found at {path}!")
        return None

    # Preferred: standardized field
    if safe_date(metadata.get("/CreationDate")):
        date = safe_date(metadata.get("/CreationDate"))
        print(f"...File Creation Date: {date}")
        return date

    # Fallback: raw date field
    if hasattr(metadata, "creation_date_raw") and safe_date(metadata.creation_date_raw):
        date = safe_date(metadata.creation_date_raw)
        print(f"...File Creation Date: {date}")
        return date

    print(f"...No metadata date could be found at {path}!")
    return None


def get_docx_metadata(path):
    """Returns DOCX creation date as datetime or None."""

    try:
        doc = docx.Document(path)
        prop = doc.core_properties
    except Exception as e:
        print(f"...Could not open DOCX at {path}")
        print(f"...ERROR: {e}")
        return None

    if safe_date(prop.created):
        date = safe_date(prop.created)
        print(f"...File Creation Date: {date}")
        return date

    print(f"...No metadata date could be found at {path}!")
    return None


# -------------------------------------------------------
# MAIN FUNCTION (called from main.py)
# -------------------------------------------------------

def main(input_directory):

    date_list = []

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

    metadata_found = sum(d is not None for d in date_list)
    metadata_not_found = sum(d is None for d in date_list)

    print("\nMETADATA SUMMARY:")
    print(f"Number of files with embedded metadata - {metadata_found}")
    print(f"Number of files without embedded metadata - {metadata_not_found}")


# -------------------------------------------------------
# ALLOW RUNNING MANUALLY (OPTIONAL TEST)
# -------------------------------------------------------

if __name__ == "__main__":
    # Helps for quick testing; does NOT interfere with imports.
    test_dir = sys.argv[1] if len(sys.argv) > 1 else "pdf_files_up"
    main(test_dir)
