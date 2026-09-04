"""Has this attack already been settled? Answer in one second, not one day.

THE PROBLEM THIS SOLVES
    Every new reviewer -- a fresh reviewer thread, a new model session, a new agent --
    arrives with no memory and re-attacks ground that was settled days ago. Re-running a
    settled check costs the operator quota he pays for and hours he does not have. On
    2026-09-04 an external review re-raised eight questions that had already been tested;
    one of them, flagged as "the one thing that could be a real inferential error", was
    disproved in ninety seconds against evidence recorded a day earlier.

    So: before running ANY check in response to a critique, run this first.

THE RULE
    A settled entry is answered FROM THE LEDGER, not by re-running the work.
    It is re-opened only if the challenger supplies NEW EVIDENCE that the recorded
    result is wrong. A restated opinion is not new evidence.

USAGE
    python settled.py --check "bootstrap paired arms"     # is this already answered?
    python settled.py --list                              # everything settled
    python settled.py --open                              # what is still OPEN
"""

import argparse
import json
import os
import sys

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SETTLED.json")


def load():
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


def score(entry, terms):
    hay = " ".join([entry["attack"], entry["result"],
                    " ".join(entry["keywords"])]).lower()
    return sum(1 for t in terms if t in hay)


def show(e, verbose=True):
    flag = "SETTLED" if e["status"] == "SETTLED" else "OPEN   "
    print(f"\n  [{flag}] {e['id']}  settled {e['settled']}  raised by {e['raised_by']}")
    print(f"    ATTACK : {e['attack']}")
    if verbose:
        print(f"    COMMAND: {e['command']}")
        print(f"    RESULT : {e['result']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", help="keywords from the incoming critique")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()
    doc = load()
    entries = doc["entries"]

    if args.list or args.open:
        want = [e for e in entries
                if not args.open or e["status"] == "OPEN"]
        for e in want:
            show(e, verbose=args.open)
        n_s = sum(1 for e in entries if e["status"] == "SETTLED")
        n_o = len(entries) - n_s
        print(f"\n  {n_s} settled, {n_o} OPEN\n")
        return

    if not args.check:
        ap.error("pass --check \"<keywords>\", --list, or --open")

    terms = [t for t in args.check.lower().replace(",", " ").split() if len(t) > 2]
    hits = sorted(((score(e, terms), e) for e in entries),
                  key=lambda x: -x[0])
    hits = [(s, e) for s, e in hits if s > 0]

    if not hits:
        print(f"\n  NOT IN THE LEDGER: \"{args.check}\"")
        print(f"  This appears to be a genuinely new question. Test it, then ADD IT "
              f"to SETTLED.json\n  so nobody has to test it twice.\n")
        sys.exit(2)

    print(f"\n  ALREADY ANSWERED — do not re-run without new evidence.")
    for s, e in hits[:3]:
        show(e)
    print(f"\n  {len(hits)} matching entr{'y' if len(hits)==1 else 'ies'}. "
          f"Answer the critic FROM THIS, and only re-test if they bring new evidence.\n")
    sys.exit(0 if hits[0][1]["status"] == "SETTLED" else 1)


if __name__ == "__main__":
    main()
