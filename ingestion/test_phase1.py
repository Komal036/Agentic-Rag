"""
Phase 1 — manual test script.

Run this after you've implemented loaders.py and chunking.py to sanity
check your work on your real documents:

    python -m ingestion.test_phase1

This is deliberately simple -- just print statements, no assertions yet.
Your job is to READ the output and judge quality yourself before moving
to Phase 2. (We'll add proper automated tests in a later phase once
there's more to test.)
"""

# TODO: from ingestion.loaders import load_directory
# TODO: from ingestion.chunking import chunk_document

DATA_DIR = "./data"


def main():
    # TODO:
    # 1. docs = load_directory(DATA_DIR)
    # 2. print how many documents were loaded, and character count of each
    # 3. for each doc, chunk_document(...) and print:
    #      - total chunk count
    #      - the first 2 chunks in full (so you can read them)
    #      - confirm page metadata looks right
    pass


if __name__ == "__main__":
    main()
