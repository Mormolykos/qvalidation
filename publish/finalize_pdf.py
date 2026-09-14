"""Publish a freshly built PDF, or fail. There is no third outcome.

WHY (Astra, 3643bbc differential — NEW-BUILD-01)
    `build_paper.sh` pointed Chromium straight at `publish/paper.pdf`. When that file was
    already open in another process — a viewer, a PyMuPDF handle, anything holding a
    Windows lock — Chromium could not write it, said so on stderr, and exited 0. The
    script printed "built publish/paper.pdf" and returned success.

    Yesterday's PDF was then still sitting at the destination, and every downstream check
    validated it. Astra hit this during the review: a stage-13 PASS that was evidence
    about a stale file, not about the build. The reviewer caught it from the build log;
    nothing in this repository would have.

    The defect is not "Chromium's exit code is unreliable". It is that SUCCESS WAS
    INFERRED FROM THE COMMAND RETURNING rather than from an artifact existing. The same
    mistake as reading a rejection out of console text (V4-07): evidence about an outcome
    in place of the outcome.

THE CONTRACT
    Build to a unique temporary path. Then, and only then:

      1. the temporary file exists, is a PDF, is not truncated, and has pages;
      2. it is moved onto the destination;
      3. the destination is re-read and must now BE that file, byte for byte.

    Any failure is nonzero and says which step failed. A locked destination therefore
    fails loudly instead of silently republishing the previous build. The temporary file
    is left on disk when replacement fails, so nothing is lost while the lock is cleared.

USAGE
    python publish/finalize_pdf.py <freshly-built.pdf> <destination.pdf>
"""

import hashlib
import os
import re
import shutil
import sys

MIN_BYTES = 50_000          # the paper is ~420 KB; a truncated write is far below this
MIN_PAGES = 5               # it is 14 pages. Anything under 5 is not this document.


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def inspect(path):
    """Reasons `path` is not a usable freshly built PDF. Empty list means it is."""
    bad = []
    if not os.path.isfile(path):
        return [f"no file was produced at {path}"]
    size = os.path.getsize(path)
    if size < MIN_BYTES:
        bad.append(f"{size:,} bytes is below the {MIN_BYTES:,}-byte floor — the write "
                   f"was truncated or the render was empty")
    with open(path, "rb") as fh:
        head = fh.read(8)
        fh.seek(max(0, size - 2048))
        tail = fh.read()
    if not head.startswith(b"%PDF-"):
        bad.append(f"does not begin with %PDF- (got {head!r})")
    if b"%%EOF" not in tail:
        bad.append("has no %%EOF trailer — the file is incomplete")
    with open(path, "rb") as fh:
        blob = fh.read()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", blob))
    if pages < MIN_PAGES:
        bad.append(f"{pages} page(s), fewer than the {MIN_PAGES} a real build produces")
    return bad


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    fresh, dest = sys.argv[1], sys.argv[2]

    bad = inspect(fresh)
    if bad:
        print(f"  ✗ the build did not produce a usable PDF at {fresh}:", file=sys.stderr)
        for b in bad:
            print(f"      {b}", file=sys.stderr)
        sys.exit(1)

    want = digest(fresh)
    print(f"  fresh build: {os.path.getsize(fresh):,} bytes, sha256 {want[:16]}…")

    # The destination may be unreadable as well as unwritable — an exclusive handle
    # (a PDF viewer holds one) denies everything. Finding that out must produce the
    # explanation below, not a traceback: a crash here is indistinguishable from a bug
    # in this script, and the person reading it needs to know to close their viewer.
    before = None
    try:
        if os.path.isfile(dest):
            before = digest(dest)
    except OSError as exc:
        locked(dest, fresh, exc)

    try:
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        shutil.move(fresh, dest)
    except OSError as exc:
        locked(dest, fresh, exc)

    try:
        got = digest(dest)
    except OSError as exc:
        locked(dest, fresh, exc)
    return finish(dest, want, got, before)


def locked(dest, fresh, exc):
    """The destination could not be read, replaced or re-read. Never a traceback."""
    print(f"\n  ✗ COULD NOT PUBLISH TO {dest}: {exc}\n"
          f"      The destination is locked or unwritable — most often it is open in a "
          f"PDF viewer.\n"
          f"      Whatever is there now is NOT this build. The fresh PDF has been left "
          f"at\n      {fresh}; close whatever holds the destination, then move it into "
          f"place.\n"
          f"      Reporting success here would publish an older document under today's "
          f"claims.", file=sys.stderr)
    sys.exit(1)


def finish(dest, want, got, before):
    # The destination must now BE the fresh build. Read it back: a move that reported
    # success and left the old bytes is exactly what this file exists to prevent.
    if got != want:
        print(f"\n  ✗ {dest} does not contain the file that was just built.\n"
              f"      expected sha256 {want}\n      found    sha256 {got}",
              file=sys.stderr)
        sys.exit(1)
    if before == got:
        print("  note: the destination's bytes are unchanged — the rebuild was "
              "byte-identical,\n        which Chromium's embedded timestamp normally "
              "prevents. Check the build.")
    print(f"  ✓ published {dest} ({os.path.getsize(dest):,} bytes), verified by "
          f"re-reading it")


if __name__ == "__main__":
    main()
