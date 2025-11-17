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
This script handles all text extraction from PDF files, using a two-stage approach:

1. Direct Extraction (pdfplumber): 
Uses pdfplumber to read text from each page. If pdfplumber successfully extracts at least ~100 characters of text, OCR is skipped. This covers digitally generated PDFs or well-formatted text.

2. OCR Extraction (Tesseract): 
If the PDF contains little/no readable text (common for documents for this project), the script converts each page to an image using pdf2image (Poppler backend). It runs Tesseract OCR (pytesseract) on each page, prints progress updates, including page-by-page OCR status, and produces structured text with page markers. Extracted text (from either method) is saved as a .txt file with the same base file name as the original PDF. 

#### Warning: 
A few PDFs could not be processed due to corruption or unsupported structures.
* Executed Sprague Hopper Coop.pdf appears corrupt and cannot be extracted.
* One additional image-only JPEG was just a picture with no text extractable.
* Of the remaining 27 PDFs, the script successfully extracted text from 20.

Overall, these failures stem from file issues rather than pipeline limitations, and the method should scale well to larger datasets.

### 2. File Renaming (filename.py)

### 3. Document Organization (organizer2.py)
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

### 4. Metadata Extraction (getimagemetadata.py)


    



   
   
   

   
