# DS5110 – Maine Port Authority Document Automation

This repository contains an automated pipeline developed as a final project for DS5110, in order to process, rename, categorize, and extract metadata from documents (PDF, DOCX, TXT) from the Maine Port Authority. Our goal was to create an automated document-management workflow that:

* Extracts text from documents (including scanned/unreadable PDFs via OCR),
* Renames files using meaningful labels (most frequent word/phrase + date),
* Groups documents into folders based on cosine-similarity scores,
* Extracts metadata such as creation dates,
* Outputs a cleaned, organized folder structure suitable for long-term use.

## Project Overview

Many documents provided to us were not directly readable by Python because they were scanned PDFs/not text-extractable. As a result, our scripts integrate several text-extraction strategies as necessary. After text extraction, files are renamed, clustered, and reorganized using cosine similarity, and metadata is extracted.

### 1. Text Extraction (extractwsubfolders.py)

This script performs all PDF text extraction for the pipeline and was designed to handle the highly mixed document quality of the Maine Port Authority archive. The extraction process uses two stages: a fast direct extraction and a fallback OCR pipeline. 

#### A. Collecting Files From Nested Folders

Before extraction, the script provides counts of PDF and DOCX files, and then:
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

Save the extracted text into a .txt file that mirrors the PDF’s original base name
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
This script groups documents into coherent, topic-based clusters using semantic similarity. It operates after text extraction and renaming, relying on cleaned text to determine which documents belong together.

#### A. Loading Document Text

The script loads text from all available processed files:

* TXT files generated from PDFs (via direct extraction or OCR)

* DOCX files using python-docx

* Files are skipped if they contain too little usable text (e.g., scanned maps, images, or extraction failures).

#### B. Cleaning the Text

Before computing embeddings, each document’s text is standardized:

* Lowercasing, removing OCR noise (page markers, stray characters, symbols), and removing punctuation

* Discarding files with fewer than ~20 meaningful words

This ensures that embeddings capture meaningful content rather than noise.

#### C. Embedding & Similarity Computation

The script converts all documents into numerical vectors using "all-MiniLM-L6-v2" (SentenceTransformer).

Then it computes pairwise cosine similarity between all documents.
Cosine similarity provides a continuous measure of how similar two documents are in meaning.

#### D. Forming High-Confidence Initial Pairs

To identify strong connections early on, the script:

* Finds the strongest match for each document

* Creates a pair only if similarity ≥ 0.8 (can be changed)

* Uses these pairs as seed groups that form the backbone of the final clusters

These initial pairs represent documents that are extremely close in content and, therefore, safe to group immediately.

#### E. Iterative Assignment of Remaining Files

After seed groups are created, the algorithm assigns the rest of the documents, for each ungrouped file:

* Compute its average cosine similarity to each existing group.

* Assign it to the group with the highest mean similarity.

* Repeat until all files are processed.

If a file’s best similarity is below 0.2, a new single-file group is created. This hybrid strategy combines strong early pairs with flexible clustering for weaker matches.

#### F. Automatically Naming Each Group

To give each folder an interpretable name, the script:

* Collects the final filenames inside the group

* Extracts frequent, meaningful keywords (ignoring very short words)

* Picks the most common informative word as the cluster label

* Detects the first year-like pattern (e.g., 2018, 2021) and adds it to the name when present

This produces group names such as:

"Logistics_2019"
"Contracts_2021"
"Terminal_20"

#### G. Exporting Final Organized Folders

For every group:

* A new folder is created under organized_folders_final/

* All corresponding PDF and DOCX files are copied into the folder

* Original filenames and extensions are preserved

* TXT files are used only for grouping, not exported

This results in a clean, searchable, topic-based folder system.

### Why TXT Files Are Used for PDFs

TXT files contain the best extracted text from the PDFs (whether via pdfplumber or OCR). Since PDFs vary in structure and quality, TXT files provide a standardized, reliable text format for computing document similarity. DOCX files, on the other hand, supply their own text directly.

## Notes & Limitations

A small portion of the PDFs cannot be processed fully, typically because they are corrupted, extremely low-quality scans, or image-only documents containing almost no text. In practice, this is expected when working with large, heterogeneous file collections and does not meaningfully affect the overall clustering results, for the larger sample. Even when OCR succeeds, its output can introduce misread characters, spacing issues, and leftover page markers, which the cleaning portion of the code reduces but cannot eliminate. Some documents may still carry imperfect or incomplete textual representations into the similarity model.

Metadata also provides limited support. Many files lack embedded metadata altogether, and even when present, creation dates or author fields may not correspond to the document’s true origin. This inconsistency makes metadata helpful when available, but unreliable for direct use for grouping or naming.

Additionally, very long or multi-topic files can have several categories at once, making their similarity scores less decisive. Embedding models capture meaning quite well, but they can still struggle with documents that shift topics or combine unrelated material, occasionally leading to ambiguous or imperfect group assignments.

Finally, the similarity thresholds used in this project, high-confidence pairing at 0.8 and minimum assignment at 0.2, work well for this dataset but are not universal. Different collections may require tuning depending on document length, OCR quality, and overall topic diversity. The workflow is also computationally heavy: OCRing many long PDFs and generating embeddings for every file takes both time and processing power. These constraints are not unencountered in large-scale document organization, and they seem to be manageable within the overall pipeline.
    


   
