# -*- coding: utf-8 -*-

"""
Document Titling Script (Updated)
---------------------------------
This version:
 - extracts dates + WIN numbers from document text
 - prepends them to filenames when appropriate
 - renames TXT, DOCX, and matching PDFs
 - returns a count of renamed files for visibility
"""

import os
import re
from docx import Document


# ------------------------------------------------------
# Helper functions
# ------------------------------------------------------

def get_text_docx(filename):
    """Extract raw words from a DOCX file."""
    try:
        doc = Document(filename)
        raw = "\n".join(p.text for p in doc.paragraphs)
        return raw.split()
    except Exception:
        return []


def get_text_txt(filename):
    """Extract raw words from a TXT file."""
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().split()
    except Exception:
        return []


def find_dates(words):
    """Return dict of month+year mentions in a document."""
    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]
    return_dict = {}

    for i in range(len(words)):
        for month in months:
            if month in words[i].lower():
                for j in range(max(i-4, 0), i+5):
                    try:
                        year = int(words[j])
                    except:
                        continue
                    if 1900 < year < 2100:
                        date = f"{month} {year}"
                        return_dict.setdefault(date, []).append(i)

    return {k: v for k, v in sorted(return_dict.items(), key=lambda x: x[1], reverse=True)}


def generate_name_metadata(words, old_filename):
    """Attach month/year and WIN number to filename."""
    regex_clean = re.compile("[^a-zA-Z0-9]")
    regex_only_nums = re.compile("[^0-9]")

    # clean first 250 words
    text = [regex_clean.sub("", w.lower()) for w in words if 0 < len(regex_clean.sub("", w.lower())) < 17]
    text = text[:250]

    # ------ Detect year if already in filename ------
    already_has_year = any(str(y) in old_filename for y in range(1990, 2035))

    # ------ Detect month/year pairs ------
    date = ""
    if not already_has_year:
        date_list = list(find_dates(words).keys())
        if date_list:
            date = date_list[0].title()

    # ------ Detect WIN number ------
    win_num = 0
    for i, w in enumerate(text):
        if w == "win":
            for offset in range(3):
                candidate = regex_only_nums.sub("", text[i + offset]) if i + offset < len(text) else ""
                if len(candidate) > 6:
                    win_num = int(candidate)
                    break

    # ------ Construct name ------
    new_name = old_filename

    if win_num > 0 and date:
        new_name = f"{win_num} {date} {old_filename}"
    elif win_num > 0:
        new_name = f"{win_num} {old_filename}"
    elif date:
        new_name = f"{date} {old_filename}"

    return new_name.strip()


# ------------------------------------------------------
# Build dictionary of new names
# ------------------------------------------------------

def generate_title_dictionary(folder_path):
    """Return dict mapping original filenames → new filenames."""
    title_dict = {}
    directory = os.listdir(folder_path)

    for filename in directory:
        full_path = os.path.join(folder_path, filename)

        if filename.lower().endswith(".docx"):
            words = get_text_docx(full_path)

        elif filename.lower().endswith(".txt"):
            words = get_text_txt(full_path)

        else:
            continue

        new_name = generate_name_metadata(words, filename)
        title_dict[filename] = new_name

    return title_dict


# ------------------------------------------------------
# Renaming function
# ------------------------------------------------------

def rename_files(title_dict, text_dir, pdf_dir):
    """Rename TXT/DOCX files and corresponding PDFs."""
    renamed_count = 0

    # Map PDFs by stem
    pdf_map = {}
    if pdf_dir:
        for f in os.listdir(pdf_dir):
            if f.lower().endswith(".pdf"):
                stem = f[:-4]
                pdf_map[stem] = f

    # Rename TXT/DOCX
    for old_name, new_name in title_dict.items():
        old_path = os.path.join(text_dir, old_name)

        # Preserve file extension
        ext = ".docx" if old_name.endswith(".docx") else ".txt"
        if not new_name.endswith(ext):
            new_name = f"{new_name}{ext}"

        new_path = os.path.join(text_dir, new_name)

        if old_path != new_path:
            os.rename(old_path, new_path)
            renamed_count += 1

    # Rename PDFs with matching text stems
    for stem, pdf_filename in pdf_map.items():
        # Does text rename affect this?
        for old_text_name, new_text_name in title_dict.items():
            if old_text_name.startswith(stem):
                new_stem = new_text_name.replace(".txt", "").replace(".docx", "")
                old_pdf_path = os.path.join(pdf_dir, pdf_filename)
                new_pdf_path = os.path.join(pdf_dir, f"{new_stem}.pdf")
                if old_pdf_path != new_pdf_path:
                    os.rename(old_pdf_path, new_pdf_path)
                break

    print(f"✓ {renamed_count} documents renamed")
    return renamed_count


# ------------------------------------------------------
# MAIN FUNCTION (callable from main.py)
# ------------------------------------------------------

def main(text_directory, pdf_directory=""):
    """
    text_directory = folder containing TXT/DOCX extracted files
    pdf_directory  = folder containing PDFs to rename (optional)
    """
    print(f"\n--- Running document titling on: {text_directory} ---")
    title_dict = generate_title_dictionary(text_directory)
    rename_files(title_dict, text_directory, pdf_directory)
    print("--- Titling complete ---\n")

