"""
Phase 1a — Document Loaders

GOAL: read a file off disk and return its raw text content, plus enough
metadata to trace an answer back to its source later (filename, and for
PDFs, page number).

-------------------------------------------------------------------------
WHY THIS MATTERS (read before coding)
-------------------------------------------------------------------------
Every later phase depends on this step being done well:
- If you don't preserve page numbers now, you can NEVER add citations
  later without re-parsing the original PDF.
- If your text extraction is messy (broken words, missing spaces), your
  embeddings in Phase 2 will be low quality no matter how good your
  retrieval logic is. Garbage in, garbage out.

-------------------------------------------------------------------------
WHAT TO BUILD
-------------------------------------------------------------------------

1. A small data structure to hold a loaded document. Use a dataclass:

    @dataclass
    class RawDocument:
        text: str          # the full extracted text
        source: str         # just the filename, e.g. "self_rag.pdf"
        doc_type: str        # "pdf", "txt", etc.

2. A function that loads ONE pdf file:

    def load_pdf(path: str) -> RawDocument:
        ...

   HINT: install `pypdf` (already in your requirements.txt).
   Use `pypdf.PdfReader(path)`. It gives you `.pages`, and each page has
   a `.extract_text()` method.

   IMPORTANT DESIGN DECISION: as you extract each page's text, prepend a
   marker like f"[page {page_number}]\\n" before that page's text, then
   join all pages together with "\\n\\n". This lets your chunker later
   recover which page a chunk of text came from, using a regex like
   r"\\[page (\\d+)\\]" -- without this marker, page-level citations are
   impossible to reconstruct after chunking merges text together.

3. A function that loads a directory of PDFs:

    def load_directory(dir_path: str) -> list[RawDocument]:
        ...

   Should loop over every .pdf file in the directory and call load_pdf
   on each one. Use os.listdir() or a similar approach.

   EDGE CASE TO HANDLE: what if one file in the directory is corrupted
   or fails to parse? Should one bad file crash the whole ingestion run,
   or should you skip it and print a warning, continuing with the rest?
   (Think about which is better for a real pipeline, then implement it
   with a try/except around the per-file load.)

-------------------------------------------------------------------------
TEST IT YOURSELF BEFORE MOVING ON
-------------------------------------------------------------------------
Write a throwaway script (or just run this in a Python REPL / VS Code
interactive window) that does:

    docs = load_directory("./data")
    for d in docs:
        print(d.source, "->", len(d.text), "characters")
        print(d.text[:300])   # eyeball the first 300 chars

Look at the printed text carefully. Does it look clean? Are page markers
present? Is any text garbled or missing (common with PDFs that have
tables, multi-column layouts, or embedded images with text)? If pypdf
extracts your paper's text badly, that's worth noting in your project
report as a known limitation -- this is a real issue with PDF parsing
libraries, not a mistake on your part.

-------------------------------------------------------------------------
STRETCH (do this AFTER the above works, not before)
-------------------------------------------------------------------------
Add load_txt() and a dispatcher load_document(path) that picks the right
loader based on file extension, so load_directory can eventually handle
mixed file types.
"""

# TODO: imports go here (os, dataclass, pypdf)


# TODO: RawDocument dataclass


# TODO: def load_pdf(path: str) -> RawDocument:


# TODO: def load_directory(dir_path: str) -> list[RawDocument]:
