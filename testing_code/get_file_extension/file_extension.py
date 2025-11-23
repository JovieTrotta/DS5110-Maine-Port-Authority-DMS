# IMPORTS
import os
import sys

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

# MAIN
def main():

    input_directory = sys.argv[1]
    
    for file in os.listdir(input_directory):

        path = os.path.join(input_directory, file)
        ext = get_file_extension(path)

        if ext:
            print(ext)
        else:
            continue

if __name__ == "__main__":
    main()
