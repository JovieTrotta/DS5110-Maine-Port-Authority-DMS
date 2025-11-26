import os
import re
import shutil
import numpy as np
from docx import Document
from sentence_transformers import SentenceTransformer, util


# --------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------
TEXT_DIR = "ocr_text_output_2"
PDF_DIR = "pdf_files_up"
DOCX_DIR = "docx_files_up"
OUTPUT_DIR = "organized_folders_final_up"

INITIAL_PAIR_THRESHOLD = 0.8   # similarity needed to form a pair
ASSIGN_THRESHOLD = 0.2        # similarity needed to join an existing group
MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------------------
def clean_text(text):
    """Clean extracted text for better semantic embeddings."""
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"--- page \d+ ---", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())

# This is because not all the files worked with tesseract to extract!
def is_empty_extraction(text):
    """Detect extremely short or useless OCR outputs."""
    words = re.findall(r"[a-zA-Z]{3,}", text)
    return len(words) < 20


# --------------------------------------------------------------
# LOAD DOCUMENTS (TXT + DOCX)
# --------------------------------------------------------------
documents = []
meta = []

# 1) TXT files (representing PDFs)
for fname in os.listdir(TEXT_DIR):
    if fname.lower().endswith(".txt"):
        path = os.path.join(TEXT_DIR, fname)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()

        if is_empty_extraction(raw):
            print(f"Skipping empty extraction: {fname}")
            continue

        cleaned = clean_text(raw)
        base = os.path.splitext(fname)[0]

        documents.append(cleaned)
        meta.append({"base": base, "kind": "pdf"})


# 2) DOCX files
for fname in os.listdir(DOCX_DIR):
    if fname.lower().endswith(".docx"):
        path = os.path.join(DOCX_DIR, fname)
        try:
            doc = Document(path)
            raw = "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            print(f"Could not read DOCX {fname}: {e}")
            continue

        cleaned = clean_text(raw)
        base = os.path.splitext(fname)[0]

        documents.append(cleaned)
        meta.append({"base": base, "kind": "docx"})

n_docs = len(documents)
print(f"Loaded {n_docs} usable documents.")


# --------------------------------------------------------------
# EMBEDDINGS + SIMILARITY
# --------------------------------------------------------------
print("\nLoading model...")
model = SentenceTransformer(MODEL_NAME)

print("Encoding documents...")
emb = model.encode(documents, convert_to_tensor=True)
sim = util.cos_sim(emb, emb).cpu().numpy()


# --------------------------------------------------------------
# INITIAL PAIRING — strong pairs only
# --------------------------------------------------------------
groups = []        # list of clusters (list of doc indices)
paired = set()     # docs that formed pairs (only these are “locked”)

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
        print(f"Pair formed: {i} & {best_j} (sim={best_score:.3f})")


# --------------------------------------------------------------
# THE SINGLE FILES GO TO REMAINING (to be reconsidered!)
# --------------------------------------------------------------
# Only paired docs are locked. Singletons will be reassigned.
all_indices = set(range(n_docs))
assigned_pairs = paired.copy()

remaining = list(all_indices - assigned_pairs)

print(f"\nInitial groups (pairs only): {len(groups)}")
print(f"Docs to be assigned iteratively: {len(remaining)}")


# --------------------------------------------------------------
# ITERATIVE ASSIGNMENT — improve grouping
# --------------------------------------------------------------
def mean_similarity(idx, group_indices):
    return float(np.mean([sim[idx][g] for g in group_indices]))


round_no = 1
while remaining:
    best_idx = None
    best_group_id = None
    best_score = -1

    # find the best match among all remaining
    for idx in remaining:
        for g_id, g in enumerate(groups):
            score = mean_similarity(idx, g)
            if score > best_score:
                best_score = score
                best_idx = idx
                best_group_id = g_id

    if best_score < ASSIGN_THRESHOLD:
        print(f"\n Stopping assignment: best sim={best_score:.3f} < {ASSIGN_THRESHOLD}")
        # remaining docs become singleton groups
        for idx in remaining:
            groups.append([idx])
        break

    # assign best doc to best group
    groups[best_group_id].append(best_idx)
    remaining.remove(best_idx)

    print(f"Round {round_no}: assigned doc {best_idx} → group {best_group_id} (sim={best_score:.3f})")
    round_no += 1

print(f"\nFinal number of groups: {len(groups)}")

# --------------------------------------------------------------
# GROUP NAME FROM FILENAMES
# --------------------------------------------------------------
import re
from collections import Counter

def generate_group_name(filenames):
    # filenames is a list of file names, e.g. ["Americold Training 2021.pdf", ...]

    # Join all filenames and split into words
    all_words = []
    for name in filenames:
        words = re.split(r"[^A-Za-z0-9]+", name)
        all_words.extend(words)

    # Filter out short or meaningless words
    meaningful = [w.lower() for w in all_words if len(w) > 3]

    # Pick most common meaningful word
    keyword = Counter(meaningful).most_common(1)
    keyword = keyword[0][0].capitalize() if keyword else "Group"

    # Detect year from file names
    years = re.findall(r"\b(19|20)\d{2}\b", " ".join(filenames))
    year = "_" + years[0] if years else ""

    # Build clean folder name
    name = f"{keyword}{year}"
    name = re.sub(r"[^A-Za-z0-9_\-]", "_", name)

    return name


# --------------------------------------------------------------
# COPY ORIGINAL FILES INTO NAMED FOLDERS
# --------------------------------------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

for g_id, group in enumerate(groups, start=1):

    # Collect *filenames* for naming
    group_filenames = []
    for idx in group:
        entry = meta[idx]
        base = entry["base"]
        ext = ".pdf" if entry["kind"] == "pdf" else ".docx"
        group_filenames.append(base + ext)

    # Create group folder name from filenames
    folder_name = generate_group_name(group_filenames)
    folder_path = os.path.join(OUTPUT_DIR, folder_name)

    os.makedirs(folder_path, exist_ok=True)
    print(f"\n Group {g_id}: '{folder_name}' ({len(group)} files)")

    # Copy each file into the new folder
    for idx in group:
        entry = meta[idx]
        base = entry["base"]
        kind = entry["kind"]

        src = os.path.join(
            PDF_DIR if kind == "pdf" else DOCX_DIR,
            base + ("." + kind)
        )

        if os.path.exists(src):
            shutil.copy2(src, folder_path)
        else:
            print(f"   ⚠️ Missing file: {src}")

print("\n DONE — folders created, files copied, meaningful clustering achieved!")



