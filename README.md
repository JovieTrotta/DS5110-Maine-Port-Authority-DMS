# DS5110 – Maine Port Authority Document Automation

This repository contains an automated pipeline developed as a final project for DS5110, in order to process, rename, categorize, and extract metadata from documents (PDF, DOCX, TXT) from the Maine Port Authority. Our goal was to create an automated document-management workflow that:

* Extracts text from documents (including scanned/unreadable PDFs via OCR),
* Renames files using meaningful labels (most frequent word/phrase + date),
* Groups documents into folders based on cosine-similarity scores,
* Extracts metadata such as creation dates,
* Outputs a cleaned, organized folder structure suitable for long-term use.
