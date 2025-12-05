# -*- coding: utf-8 -*-
# Chris Kinley
# Updated for DS5110 Pipeline Integration

import os
import re
from docx import Document

# -------------------------------------------------------
# MAIN FUNCTIONS
# -------------------------------------------------------

def main(path, pdf_path=""):
    """
    Renames DOCX and TXT files in `path`, and optionally renames
    PDFs in `pdf_path` based on extracted keywords and dates.
    """

    print("\n🔤 Running file renaming module...")

    # Regex cleaning patterns
    regex = re.compile('[^a-zA-Z0-9]')
    regex_no_num = re.compile('[^a-zA-Z]')

    # Stopwords list
    stopwords = ['', "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
                 "you", "your", "yours", "yourself", "yourselves", "he", "him",
                 "his", "himself", "she", "her", "hers", "herself", "it", "its",
                 "itself", "they", "them", "their", "theirs", "themselves", "what",
                 "which", "who", "whom", "this", "that", "these", "those", "am",
                 "is", "are", "was", "were", "be", "been", "being", "have", "has",
                 "had", "having", "do", "does", "did", "doing", "a", "an", "the",
                 "and", "but", "if", "or", "because", "as", "until", "while", "of",
                 "at", "by", "for", "with", "about", "against", "between", "into",
                 "through", "during", "before", "after", "above", "below", "to",
                 "from", "up", "down", "in", "out", "on", "off", "over", "under",
                 "again", "further", "then", "once", "here", "there", "when",
                 "where", "why", "how", "all", "any", "both", "each", "few", "more",
                 "most", "other", "some", "such", "no", "nor", "not", "only", "own",
                 "same", "so", "than", "too", "very", "s", "t", "can", "will",
                 "just", "don", "should", "now", "shall", "page", "---"]

    # -------------------------------------------------------
    # Helper functions inside main()
    # -------------------------------------------------------

    def getText(filename):
        """Extract text from a DOCX file."""
        try:
            doc = Document(filename)
            raw = "\n".join(p.text for p in doc.paragraphs)
            return raw.split()
        except:
            return []

    def find_dates(tokens):
        """Find month-year combinations in text."""
        return_dict = {}
        months = ["january","february","march","april","may","june",
                  "july","august","september","october","november","december"]

        for i in range(len(tokens)):
            for month in months:
                if month in tokens[i].lower():
                    for j in range(max(i-4,0), i+5):
                        try:
                            year = int(tokens[j])
                            if 1900 < year < 2100:
                                date = f"{month} {year}"
                                return_dict.setdefault(date, []).append(i)
                        except:
                            continue

        return {k: v for k, v in sorted(return_dict.items(), key=lambda x: x[1], reverse=True)}

    def generate_name(text_entered, freq_dict_entered, bifreq_dict_entered):
        """Creates a name based on frequencies and seed words."""

        freq_hits = list(freq_dict_entered.keys())[0:5]
        bi_hits = [k for k in list(bifreq_dict_entered.keys())[0:5] if bifreq_dict_entered[k] >= 2]

        title_seed = ""
        for w in freq_hits:
            for b in bi_hits:
                if w in b:
                    title_seed = w
                    break
            if title_seed:
                break

        if not title_seed:
            return "not found"

        # Build name
        for i in range(len(text_entered)):
            cleaned = regex.sub('', text_entered[i].lower())
            if title_seed in cleaned:
                slice_words = text_entered[max(0,i-2):i+12]
                cleaned_list = [regex_no_num.sub('', w.lower()) for w in slice_words]
                break

        title = " ".join(w for w in cleaned_list if w not in stopwords)

        # Add date if present
        date_list = list(find_dates(text_entered).keys())
        if date_list:
            title += " " + date_list[0]

        return title.title()

    def gen_freq_dicts(text_whole):
        """Generate frequency and bi-frequency dictionaries."""

        cleaned_text = [regex_no_num.sub('', w.lower()) for w in text_whole
                        if 0 < len(regex_no_num.sub('', w.lower())) < 14]

        cleaned_text = cleaned_text[:250]  # limit early words

        freq = {}
        for w in cleaned_text:
            if w not in stopwords and 2 < len(w) < 14:
                freq[w] = freq.get(w, 0) + 1

        bifreq = {}
        prev = ""
        for w in cleaned_text:
            if w not in stopwords and 2 < len(w) < 14:
                two = f"{prev} {w}"
                bifreq[two] = bifreq.get(two, 0) + 1
                prev = w

        return cleaned_text, dict(sorted(freq.items(), key=lambda x: x[1], reverse=True)), dict(sorted(bifreq.items(), key=lambda x: x[1], reverse=True))

    def generate_title_dictionary(folder_path):
        """Generate mapping of original names → new title strings."""
        title_dictionary = {}

        for filename in os.listdir(folder_path):

            if filename.endswith(".docx"):
                tokens = getText(os.path.join(folder_path, filename))
            elif filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), "r") as f:
                    tokens = f.read().split()
            else:
                continue

            text_short, freq, bifreq = gen_freq_dicts(tokens)
            new_name = generate_name(text_short, freq, bifreq)

            title_dictionary[filename] = filename if new_name == "not found" else new_name.strip()

        return title_dictionary

    def rename_files(title_dictionary, file_path, pdf_file_path):
        """Renames TXT, DOCX, and optionally PDFs."""

        pdf_dict = {}
        if pdf_file_path:
            for f in os.listdir(pdf_file_path):
                if f.endswith(".pdf"):
                    pdf_dict[f[:-4]] = f[:-4]

        for original in title_dictionary:

            old_path = os.path.join(file_path, original)
            new_title = title_dictionary[original]

            if old_path.endswith(".txt"):
                txt_name = new_title if new_title.endswith(".txt") else new_title + ".txt"
                new_path = os.path.join(file_path, txt_name)

                # Sync PDF name if same base name
                base = original[:-4]
                if base in pdf_dict:
                    pdf_dict[base] = new_title

            elif old_path.endswith(".docx"):
                docx_name = new_title if new_title.endswith(".docx") else new_title + ".docx"
                new_path = os.path.join(file_path, docx_name)

            else:
                continue

            os.rename(old_path, new_path)

        # Rename PDFs
        for base, new in pdf_dict.items():
            old_pdf = os.path.join(pdf_file_path, base + ".pdf")
            new_pdf = os.path.join(pdf_file_path, new + ".pdf")
            if old_pdf != new_pdf:
                os.rename(old_pdf, new_pdf)


    # -------------------------------------------------------
    # RUN THE RENAMING LOGIC
    # -------------------------------------------------------

    title_dict = generate_title_dictionary(path)
    rename_files(title_dict, path, pdf_path)

    print("✔ File renaming complete.")
    return True


# -------------------------------------------------------
# OPTIONAL: Allow script to be run directly
# -------------------------------------------------------
if __name__ == "__main__":
    print("Running document title script manually...")
    # Default paths for standalone testing
    main("data_folder_here", "pdf_folder_here")
