# IMPORTS
import os
import sys
import docx

# FUNCTIONS
def get_docx_metadata(path):

    '''
    Parameter: full file path
    Returns: N/A

    Takes a file path as its only parameter, prints various attributes of the DOC.
    '''
    
    doc = docx.Document(path)
    metadata = {}
    prop = doc.core_properties
    print(prop.author)
    print(prop.category)
    print(prop.comments)
    print(prop.created)
    print(prop.created.month)
    print(type(prop.created))
    print(prop.last_modified_by)
    print(prop.modified)
    print(type(prop.modified))
    print(prop.title)

    '''
        year = dt_object.year
        # Extract the month
        month = dt_object.month
    '''

# MAIN
def main():

    input_directory = sys.argv[1]

    for file in os.listdir(input_directory):

        # skip whatever isn't a DOC
        if not file.lower().endswith(".docx"):
            continue

        path = os.path.join(input_directory, file)
        print(f'\nProcessing {file}...')
        get_docx_metadata(path)

if __name__ == "__main__":
    main()
