"""
organizer2.py
Performs document grouping using semantic similarity and builds final folder structure.
"""

import os
import re
import shutil
import numpy as np
from collections import Counter
from docx import Document
from sentence_transformers import SentenceTransformer, util


# --------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------
INITIAL_PAIR_THRESHOLD = 0.8
ASSIGN_THRESHOLD = 0.2
MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------------------
def clean_text(text):
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"--- page \d+ ---", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def is_empty_extraction(text):
    """Detect extremely short or useless OCR outputs."""
    words = re.findall(r"[a-zA-Z]{3,}", text)
    return len(words) < 20


# --------------------------------------------------------------
# NAME GENERATION FOR GROUP FOLDERS
# --------------------------------------------------------------
def generate_group_name(filenames):
    all_words = []
    for name in filenames:
        words = re.split(r"[^A-Za-z0-9]+", name)
        all_words.extend(words)

    meaningful = [w.lower() for w in all_words if len(w) > 3]
    keyword = Counter(meaningful).most_common(1)
    keyword = keyword[0][0].capitalize() if keyword else "Group"

    years = re.findall(r"\b(19|20)\d{2}\b", " ".join(filenames))
    year = "_" + years[0] if years else ""

    name = f"{keyword}{year}"
    name = re.sub(r"[^A-Za-z0-9_\-]", "_", name)
    return name


# --------------------------------------------------------------
# MAIN FUNCTION FOR FOLDER ORGANIZATION
# --------------------------------------------------------------
def main(text_dir="ocr_text_output_2",
         pdf_dir="pdf_files_up",
         docx_dir="docx_files_up",
         output_dir="organized_folders_final_up"):
    """
    Full grouping pipeline:
    1) Load and clean text (TXT + DOCX)
    2) Compute embeddings and cosine similarity
    3) Build initial strong pairs
    4) Iteratively assign remaining documents
    5) Create folder groups + copy files

    Returns summary dictionary.
    """

    print("\n🔍 Starting document grouping...")

    # --------------------------------------------------------------
    # LOAD DOCUMENTS
    # --------------------------------------------------------------
    documents = []
    meta = []

    # TXT files (PDF extractions)
    for fname in os.listdir(text_dir):
        if fname.lower().endswith(".txt"):
            path = os.path.join(text_dir, fname)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()

            if is_empty_extraction(raw):
                print(f"⚠️ Skipping empty extraction: {fname}")
                continue

            cleaned = clean_text(raw)
            base = os.path.splitext(fname)[0]
            documents.append(cleaned)
            meta.append({"base": base, "kind": "pdf"})

    # DOCX files
    for fname in os.listdir(docx_dir):
        if fname.lower().endswith(".docx"):
            path = os.path.join(docx_dir, fname)
            try:
                doc = Document(path)
                raw = "\n".join(p.text for p in doc.paragraphs)
            except Exception as e:
                print(f"⚠️ Could not read DOCX {fname}: {e}")
                continue

            cleaned = clean_text(raw)
            base = os.path.splitext(fname)[0]
            documents.append(cleaned)
            meta.append({"base": base, "kind": "docx"})

    n_docs = len(documents)
    print(f"📄 Loaded {n_docs} usable documents.")

    if n_docs == 0:
        print("❌ No usable documents found. Exiting.")
        return {"groups": [], "n_docs": 0}

    # --------------------------------------------------------------
    # EMBEDDINGS + SIMILARITY
    # --------------------------------------------------------------
    print("\n⏳ Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("🔢 Encoding documents...")
    emb = model.encode(documents, convert_to_tensor=True)
    sim = util.cos_sim(emb, emb).cpu().numpy()

    # --------------------------------------------------------------
    # INITIAL STRONG PAIRING
    # --------------------------------------------------------------
    groups = []
    paired = set()

    for i in range(n_docs):
        if i in paired:
            continue

        best_j = None
        best_score = -1

        for j in range(i + 1, n_docs):
            if j in paired:
                continue
            score = sim[i, j]
            if score > best_score:
                best_score = score
                best_j = j

        if best_j is not None and best_score >= INITIAL_PAIR_THRESHOLD:
            groups.append([i, best_j])
            paired.add(i)
            paired.add(best_j)
            print(f"✨ Pair formed: {i} & {best_j} (sim={best_score:.3f})")

    all_indices = set(range(n_docs))
    remaining = list(all_indices - paired)

    print(f"\n📦 Initial pair groups: {len(groups)}")
    print(f"🧩 Docs to assign iteratively: {len(remaining)}")

    # --------------------------------------------------------------
    # ITERATIVE ASSIGNMENT
    # --------------------------------------------------------------
    def mean_similarity(idx, group_indices):
        return float(np.mean([sim[idx][g] for g in group_indices]))

    round_no = 1
    while remaining:
        best_idx = None
        best_group_id = None
        best_score = -1

        for idx in remaining:
            for g_id, g in enumerate(groups):
                score = mean_similarity(idx, g)
                if score > best_score:
                    best_score = score
                    best_idx = idx
                    best_group_id = g_id

        if best_score < ASSIGN_THRESHOLD:
            print(f"\n⛔ Stopping assignment: best similarity={best_score:.3f}")
            for idx in remaining:
                groups.append([idx])
            break

        groups[best_group_id].append(best_idx)
        remaining.remove(best_idx)

        print(f"➡️ Round {round_no}: assigned {best_idx} → group {best_group_id} (sim={best_score:.3f})")
        round_no += 1

    print(f"\n📁 Total groups formed: {len(groups)}")

    # --------------------------------------------------------------
    # BUILD OUTPUT FOLDERS
    # --------------------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)

    for g_id, group in enumerate(groups, start=1):
        group_filenames = []

        for idx in group:
            entry = meta[idx]
            ext = ".pdf" if entry["kind"] == "pdf" else ".docx"
            group_filenames.append(entry["base"] + ext)

        folder_name = generate_group_name(group_filenames)
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        print(f"\n📂 Group {g_id}: '{folder_name}' — {len(group)} files")

        for idx in group:
            entry = meta[idx]
            base = entry["base"]
            kind = entry["kind"]

            src_dir = pdf_dir if kind == "pdf" else docx_dir
            src = os.path.join(src_dir, base + ("." + kind))

            if os.path.exists(src):
                shutil.copy2(src, folder_path)
            else:
                print(f"⚠️ Missing file for copying: {src}")

    print("\n🎉 DONE — Documents clustered and folders created.")

    return {
        "n_docs": n_docs,
        "groups": groups,
        "output_dir": output_dir
    }


# --------------------------------------------------------------
# SAFE DIRECT RUN
# --------------------------------------------------------------
if __name__ == "__main__":
    print("Running organizer2.py directly...")
    main()
