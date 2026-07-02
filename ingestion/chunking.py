"""
Phase 1b — Chunking

GOAL: split each document's raw text into smaller overlapping pieces
("chunks") that are small enough to embed meaningfully and retrieve
precisely, while preserving enough context that a chunk still makes
sense on its own.

-------------------------------------------------------------------------
WHY THIS MATTERS (read before coding -- this is a genuinely important
design decision, not busywork)
-------------------------------------------------------------------------

Why not just embed the WHOLE document as one vector?
  Because embeddings compress meaning -- a 10-page paper crammed into one
  embedding vector loses almost all specific detail. When someone asks
  "what's the chunk-id parameter for," you need a small, specific piece
  of text to retrieve, not the whole paper.

Why not just split every 500 characters, ignoring sentence/paragraph
boundaries?
  Because you'd frequently cut a sentence in half, e.g. chunk 1 ends with
  "...the retrieval grader outputs a verdict of" and chunk 2 starts with
  "sufficient, insufficient, off_topic, or rewrite." Neither chunk makes
  sense alone, and neither will embed well or retrieve well.

Why overlap between chunks?
  If a key sentence sits right at the boundary between chunk 4 and
  chunk 5, splitting with NO overlap could sever it entirely so that
  neither chunk fully contains the idea. Overlap (e.g. carrying the last
  100-150 characters of chunk 4 into the start of chunk 5) reduces the
  chance an idea gets orphaned across a chunk boundary.

Why does chunk_size matter?
  Too small (e.g. 100 chars): you lose context, retrieval becomes noisy,
  and you need way more chunks (slower, more storage).
  Too large (e.g. 3000 chars): you dilute relevance -- a chunk might
  contain the answer AND four unrelated paragraphs, which hurts
  embedding precision and wastes context window space in generation.
  A common starting point is 500-1000 characters with 10-20% overlap --
  you'll tune this later once you can SEE retrieval quality in Phase 2.

-------------------------------------------------------------------------
WHAT TO BUILD
-------------------------------------------------------------------------

1. A Chunk dataclass:

    @dataclass
    class Chunk:
        id: str                # unique id -- use uuid.uuid4()
        text: str
        source: str              # which document this came from
        chunk_index: int          # 0, 1, 2... order within the document
        metadata: dict             # at minimum: {"page": <page number or None>}

2. A recursive/hierarchical splitting function. This is the core logic:

    def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
        ...

   APPROACH (think through this yourself, this is the actual learning):
   - First try splitting on paragraph breaks ("\\n\\n"). If a paragraph
     unit is small enough, keep it as-is; if paragraphs are already
     smaller than chunk_size, greedily PACK multiple paragraphs together
     up to chunk_size before starting a new chunk.
   - If a document has no paragraph breaks at all (some PDFs extract as
     one giant blob), fall back to splitting on single newlines, then to
     splitting on sentence boundaries (". "), in that order -- only fall
     back if the previous method didn't produce small-enough units.
   - When you close off a chunk and start a new one, carry the trailing
     `overlap` characters of the previous chunk into the start of the
     new one.
   - Handle the edge case where a single unit (e.g. one giant paragraph)
     is STILL bigger than chunk_size even alone -- you'll need to
     hard-split it by character count as a last resort.

   This is intentionally a non-trivial function. Expect to iterate on it
   a few times once you see real output in the test step below.

3. A wrapper that turns one document's text into a list of Chunk objects,
   pulling the page number back out of your "[page N]" markers from
   loaders.py using a regex, and putting it into chunk.metadata:

    def chunk_document(raw_text: str, source: str) -> list[Chunk]:
        ...

-------------------------------------------------------------------------
TEST IT YOURSELF BEFORE MOVING ON
-------------------------------------------------------------------------
Using a document you loaded in loaders.py:

    chunks = chunk_document(doc.text, source=doc.source)
    print(f"{len(chunks)} chunks created")
    for c in chunks[:5]:
        print(f"--- chunk {c.chunk_index} (page {c.metadata['page']}) ---")
        print(c.text)
        print()

Things to actually check, don't skip this:
  - Do consecutive chunks have the expected overlap (last ~100-150 chars
    of one chunk appearing at the start of the next)?
  - Does any chunk cut off mid-sentence in a way that loses meaning?
  - Is the page metadata correct? Spot check 2-3 chunks against the
    actual PDF.
  - How many total chunks did your ~3 papers produce? (You'll want this
    number later when writing your project report -- "X documents,
    Y pages, Z chunks" is a good stat to have on hand.)

-------------------------------------------------------------------------
CHECKPOINT BEFORE PHASE 2
-------------------------------------------------------------------------
You should be able to explain, without looking at your code:
  - What happens if overlap is set to 0
  - What happens if chunk_size is set very large (e.g. 5000)
  - Why paragraph-first splitting is preferred over always doing a hard
    character-count split
"""

# TODO: imports go here (re, uuid, dataclass)


# TODO: Chunk dataclass


# TODO: def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:


# TODO: def chunk_document(raw_text: str, source: str) -> list[Chunk]:
