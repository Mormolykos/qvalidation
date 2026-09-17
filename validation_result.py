"""The terminal outcome of a validation layer, stated structurally instead of inferred.

WHY (Astra, 3643bbc differential)
    `mutation_test.classify` read a layer's outcome out of its console text: nonzero exit
    plus a `✗` somewhere in the output meant REJECTED. Astra made a layer print its
    expected rejection diagnostic and *then* raise an unrelated RuntimeError. The
    classifier said REJECTED, the declared-reason substring was present, and a crash was
    recorded as successful regression coverage.

    That is the same defect as V4-07's first round, one level down. Round one asked "did
    it print ✗?" instead of "did it exit nonzero?"; both are evidence ABOUT the outcome,
    scraped after the fact, rather than the outcome itself. Neither can distinguish a
    layer that finished and rejected from a layer that rejected and then fell over — and
    a layer that fell over did not finish, so it cannot vouch for anything.

THE CONTRACT
    A layer ends by calling `accept()` or `reject()`. Either one prints, as the LAST
    thing it does before exiting, a single line:

        ##QVALIDATION-RESULT## PASSED
        ##QVALIDATION-RESULT## REJECTED <invariant>

    A reader of that output may conclude the layer reached a verdict if and only if ALL
    THREE hold: that line is the final non-empty line of stdout, stderr carries no
    traceback, and the process exited with the status this module's own accept()/reject()
    produce. Anything else — a crash before it, a crash after it, a silent exit, output
    continuing past it, an exit status the contract never emits — is ERROR, which is
    neither a pass nor a detection and is never counted as either.

    The sentinel is printed immediately before `sys.exit`, so nothing but a `finally`
    block can run between the verdict and the process ending. A traceback raised after it
    still lands on stderr, and therefore still reads as ERROR.

WHY A SENTINEL AND NOT AN EXIT CODE
    Exit codes are one byte with no room for "which invariant", and every interpreter,
    shell and OS can manufacture a nonzero one. The sentinel can only be produced by this
    module, at the end of a validation routine that ran to completion.
"""

import sys

SENTINEL = "##QVALIDATION-RESULT##"
PASSED, REJECTED, ERROR = "PASSED", "REJECTED", "ERROR"

# The exit statuses the contract itself produces. A verdict counts only when the process
# ALSO terminated the way accept()/reject() terminate it.
#
# WHY EXACT AND NOT `!= 0` (Astra, post-4d50a2b)
#     classify() accepted any nonzero status beside a REJECTED sentinel. Astra had a
#     validator print its rejection diagnostic and then exit 23. Nonzero, sentinel
#     present, no traceback — scored REJECTED, and a mutation was credited to a process
#     that did not end through reject() at all.
#
#     "Nonzero" is a property shared by every abnormal death there is: an uncaught signal,
#     os._exit in a finally block, a wrapper's own status, MemoryError under a handler
#     that swallows the traceback, a missing tool. reject() exits exactly REJECT_EXIT, so
#     that is what a rejection looks like. Anything else is ERROR, which is neither a pass
#     nor a detection.
PASS_EXIT = 0
REJECT_EXIT = 1


def accept(*lines):
    """The artifact satisfied every invariant this layer checks. Exits 0."""
    for line in lines:
        print(line)
    print(f"\n{SENTINEL} {PASSED}")
    sys.stdout.flush()
    sys.exit(PASS_EXIT)


def reject(invariant, headline, fails, limit=30):
    """The artifact violated `invariant`. Exits 1.

    `invariant` is a stable identifier, not prose: it is what a caller asserts against,
    so it must survive rewording of the human-readable message beside it.
    """
    print(f"\n  ✗ {headline} — {len(fails)} problem(s):\n")
    for f in list(fails)[:limit]:
        print(f"      {f}")
    if len(fails) > limit:
        print(f"      … and {len(fails) - limit} more")
    print(f"\n{SENTINEL} {REJECTED} {invariant}")
    sys.stdout.flush()
    sys.exit(REJECT_EXIT)


def classify(code, out, err):
    """(outcome, invariant) from a layer's terminal output. Never guesses.

    `out` and `err` must be kept SEPARATE. Concatenating them lets an ordinary stderr
    warning land after the sentinel and read as a crash, and lets a traceback interleave
    ahead of it and read as clean.
    """
    if "Traceback (most recent call last)" in (err or ""):
        return ERROR, "traceback on stderr"
    lines = [ln.strip() for ln in (out or "").splitlines() if ln.strip()]
    if not lines or not lines[-1].startswith(SENTINEL):
        return ERROR, "no terminal verdict: the layer did not reach accept() or reject()"
    parts = lines[-1].split(None, 2)
    verdict = parts[1] if len(parts) > 1 else ""
    invariant = parts[2] if len(parts) > 2 else ""
    if verdict == PASSED and code == PASS_EXIT:
        return PASSED, ""
    if verdict == REJECTED and code == REJECT_EXIT:
        return REJECTED, invariant
    return ERROR, (f"verdict {verdict!r} with exit status {code}; the contract exits "
                   f"{PASS_EXIT} on {PASSED} and {REJECT_EXIT} on {REJECTED}, so this "
                   f"process did not terminate through accept() or reject()")
