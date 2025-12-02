import os
import shutil
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/Applications/miniconda3/bin/tesseract"

# -------------------------------------------------------
# COUNT PDF & DOCX FILES IN ALL SUBFOLDERS
# -------------------------------------------------------

# This is your messy folder containing many subfolders
source_root = "raw_files"
pdf_input_dir = "pdf_files_up"
docx_input_dir = "docx_files_up"

os.makedirs(pdf_input_dir, exist_ok=True)
os.makedirs(docx_input_dir, exist_ok=True)

pdf_count = 0
docx_count = 0

print("\n📂 Collecting files from subfolders...\n")

def safe_copy(src, dst_dir):
    """
    Copies a file without overwriting existing ones.
    If filename exists, creates filename (1).pdf, (2).pdf, etc.
    """
    base = os.path.basename(src)
    name, ext = os.path.splitext(base)
    dst = os.path.join(dst_dir, base)

    counter = 1
    while os.path.exists(dst):
        dst = os.path.join(dst_dir, f"{name} ({counter}){ext}")
        counter += 1

    shutil.copy2(src, dst)
    return dst


for root, dirs, files in os.walk(source_root):

    for file in files:
        lower = file.lower()

        # Skip MS Office temp files (corrupt)
        if lower.startswith("~$"):
            continue

        full_path = os.path.join(root, file)

        # --- 1. Extract ZIP FILES ---
        if lower.endswith(".zip"):
            print(f"📦 Extracting ZIP: {file}")
            try:
                with zipfile.ZipFile(full_path, 'r') as z:
                    z.extractall(root)
            except Exception as e:
                print(f"   ⚠️ Could not unzip {file}: {e}")
            continue

        # --- 2. PDF FILES ---
        if lower.endswith(".pdf"):
            safe_copy(full_path, pdf_input_dir)
            pdf_count += 1
            print(f"  ➜ Copied PDF: {file}")

        # --- 3. DOCX FILES ---
        elif lower.endswith(".docx"):
            safe_copy(full_path, docx_input_dir)
            docx_count += 1
            print(f"  ➜ Copied DOCX: {file}")

print("\n✅ All files collected.")
print(f"📊 Total PDFs: {pdf_count}")
print(f"📊 Total DOCX: {docx_count}\n")
# -------------------------------------------------------
# STEP 1: YOUR EXISTING PDF → TEXT EXTRACTION PIPELINE
# -------------------------------------------------------

input_dir = pdf_input_dir                     # keep consistent
output_dir = "ocr_text_output_2"
os.makedirs(output_dir, exist_ok=True)

def extract_text_pdfplumber(pdf_path):
    """Try to extract text directly using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
    except Exception as e:
        print(f" pdfplumber failed for {os.path.basename(pdf_path)}: {e}")
        return ""

def ocr_pdf(pdf_path):
    """Convert each page to an image and perform OCR with progress feedback."""
    text = ""
    try:
        pages = convert_from_path(
            pdf_path,dpi=200,
            poppler_path="/opt/homebrew/opt/poppler/bin")
        total_pages = len(pages)
        print(f" Running OCR on {total_pages} pages...")
        for i, page in enumerate(pages, start=1):
            print(f"   Processing page {i}/{total_pages} ...", end="\r")
            page_text = pytesseract.image_to_string(page, lang="eng")
            text += f"\n--- Page {i} ---\n{page_text}"
        print(f"\n Finished OCR for {os.path.basename(pdf_path)}")
        return text.strip()
    except Exception as e:
        print(f" OCR failed for {os.path.basename(pdf_path)}: {e}")
        return ""

print("🔎 Beginning text extraction...\n")

for file in os.listdir(input_dir):
    if not file.lower().endswith(".pdf"):
        continue

    pdf_path = os.path.join(input_dir, file)
    print(f"\n📄 Processing {file}...")

    # Step 1: Try normal text extraction
    text = extract_text_pdfplumber(pdf_path)

    # Step 2: If little or no text, switch to OCR
    if len(text) < 100:
        print("Little or no text found — switching to OCR mode.")
        text = ocr_pdf(pdf_path)

    # Step 3: Save output
    if text:
        out_path = os.path.join(output_dir, file.replace(".pdf", ".txt"))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text saved: {out_path} ({len(text):,} characters)")
    else:
        print(f"No text extracted for {file}")
