# DS5110 – Maine Port Authority Document Automation

This repository contains an automated pipeline developed as a final project for DS5110, in order to process, rename, categorize, and extract metadata from documents (PDF, DOCX, TXT) from the Maine Port Authority. Our goal was to create an automated document-management workflow that:

* Extracts text from documents (including scanned/unreadable PDFs via OCR),
* Renames files using meaningful labels (most frequent word/phrase + date),
* Groups documents into folders based on cosine-similarity scores,
* Extracts metadata such as creation dates,
* Outputs a cleaned, organized folder structure suitable for long-term use.

## Project Overview

Many documents provided to us were not directly readable by Python because they were scanned PDFs/not text-extractable. As a result, our scripts integrate several text-extraction strategies as necessary. After text extraction, files are renamed, clustered, and reorganized using cosine similarity, and metadata is extracted.

### 1. Text Extraction (extraction2.py)

This script performs all PDF text extraction for the pipeline and was designed to handle the highly mixed document quality of the Maine Port Authority archive. The extraction process uses two stages: a fast direct extraction and a fallback OCR pipeline. 

#### A. Collecting Files From Nested Folders

Before extraction, the script:
Recursively scans the entire raw_files/ directory
Copies all .pdf files to pdf_files_up/

Copies all .docx files to docx_files_up/
This ensures the program can process deeply nested client folders without manual cleanup. 

#### B. Direct Text Extraction (pdfplumber)

For each PDF:

Attempt to extract text using pdfplumber.
If the output contains ≥ 100 characters, the script treats the file as a digital PDF.
The text is saved immediately with no OCR needed.
This threshold avoids unnecessary OCR for clean, digital documents and significantly speeds up processing. 

#### C. OCR Extraction (Tesseract) for Scanned PDFs

If a PDF contains little or no extractable text:

Convert each page to an image using pdf2image (Poppler backend)
Run Tesseract OCR (via pytesseract) page by page
Print detailed progress updates (e.g., “Processing page 3/56…”)

Save extracted text into a .txt file that mirrors the PDF’s original base name
Example: Lease-2019.pdf → Lease-2019.txt

This consistency is critical for the renaming and cosine similarity grouping steps.  

#### D. Output

All extracted text—whether from pdfplumber or OCR—is saved into:
ocr_text_output_2/

Each file retains the same base name as its original PDF, ensuring a 1:1 mapping used by the renaming and grouping modules.

### 2. Metadata Extraction (getimagemetadata.py)

We have three primary types of documents that we will be examining.

1. .pdf

    More information available here regarding the library: https://pypdf2.readthedocs.io/en/3.x/modules/DocumentInformation.html
    
    This code extracts the metadata available in a document's head.
    
    We can access the following attributes that are part of nearly every PDF file:
    
    ...File Author
    ...File Creation Date
    ...File Creator
    ...File Modified Date
    ...File Producer
    ...File Subject
    ...File Title

2. .doc
   
    *** Look into the Document Python library.
   
3. .txt

    Text files do not contain metadata.

### 3. File Renaming (filename.py)

### 4. Document Organization (organizer2.py)
This script groups documents into meaningful clusters based on semantic similarity using Sentence Transformers.

1. Loads document text
* TXT files (from OCR-processed PDFs)
* DOCX files (read directly)
* Skips files where OCR extracted too little text to be usable. (7/27)

2. Cleans the text
* Lowercases, removes page markers, strips symbols, and normalizes whitespace.

3. Computes embeddings
* Uses the all-MiniLM-L6-v2 sentence-transformer model.
* Computes cosine-similarity between all documents.

4. Creates initial high-similarity pairs
* Forms pairs only when similarity ≥ 0.8).
* Only these “paired” docs become locked into groups.

5. Iteratively assigns remaining documents
* In each round, one non-paired file is assigned to the group with the highest mean similarity.
* Mean similarities with each group are recalculated for the remaining files.
* Assignment continues until the best remaining similarity falls below 0.2 (which holds for all documents here). 

6. Names each group automatically
* Uses the most frequent long word (length > 5) inside the cluster.
* Adds the first year detected (if any) from the combined text.

7. Copies original documents to the output folders
* PDF files → from pdf_files/
* DOCX files → from docx_files/
* Ensures all groups are saved under organized_folders_final.

#### Why TXT Files Are Used for PDFs: 
Not all PDFs yielded usable text from OCR, so TXT files (when available) represent the “best possible” extracted text for grouping. DOCX files use their native text. 

## Notes & Limitations

* A small number of PDFs cannot be processed—acceptable in a larger dataset context.
* Similarity thresholds may need tuning for different document collections.
    



   
   
   

   
