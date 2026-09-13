# Astra hostile audit of v4 — preserved evidence

**Target reviewed:** `4531d97d754c9f116db567e1908cbb59d6016eb2`
**Verdict as delivered:** CORE SURVIVES MAJOR CORRECTIONS — 6 MAJOR, 4 MINOR
(V4-01 … V4-10). No fatal counterexample to the empirical endpoint was found.

The auditor worked in disposable copies under the system temp directory and did not
write to this repository. `FINAL_STATE.json` records that the author's working tree was
unchanged at the end of the review, with the same HEAD it started from.

These files are copied here verbatim. They are **not** edited to agree with the repairs
made in response to them; a correction ledger that could be reconciled with the audit by
editing the audit would record nothing.

## Contents

| SHA-256 | bytes | file |
|---|---:|---|
| `e19c245d7773f9ea8e51f24be9323c9332a91722fc6e2c8e323b0708d685f2c3` | 39,807 | `V4_FINAL_REPRODUCIBILITY_REVIEW.md` — the review, sections A–J |
| `e174a0d137d830b39e83320134b1b18fa421dede248a762caa6b355bacf02ad1` | 5,524 | `V4_FRESH_ATTACK_LEDGER.md` — claims written BEFORE reading this repository's own correction ledger |
| `aebe46a6d4239ab486c39bb3b2ee31eed96276d3eafdf6430311f80bcde4de7e` | 616 | `PREFLIGHT.json` — target resolution and starting state |
| `8383437ec29d6e80aceb3e50c7cfe8c07a68880642fc18f26ff475fa269e4a4f` | 238 | `FINAL_STATE.json` — the author's tree, unchanged, at completion |
| `8042abb6478b5c1435be6cce9288e3d00eb029ddf8f26fcf8ffa23173055a3c5` | 34,427 | `independent.json` — reconstruction using no project analysis imports |
| `db3049e1f96139c41e29ce834afc2784183c9c12f6e4be2bd0062629247af33a` | 1,559 | `independent.log` |
| `13c2c47c5236307663ba333b5f32f16472faa5c059503259d3f4801aa348bc81` | 9,741 | `bootstrap_replay.json` — all 36 original risk intervals, replayed |
| `24df63ad4e75c7712a25fba0b210c2031dd7427500a510a587afc9c7c0edd345` | 6,282 | `bootstrap_replay.log` |
| `b7d5a30c0fd5b326010bb6eb017cac83b7f93a584d76e22dec2167632c69a42b` | 25,450 | `supplementary.json` — bands, k-sweep, selection test, cross-machine |
| `fa75f99e34d0b1bb592eaea05acb13631b50c5a3ab46e7dc47178eaf0fe51b10` | 1,822 | `supplementary.log` |
| `7090e8c780847e8929603268517654b9a2313d550e6974b2d35ac145c8387a9e` | 1,559 | `document_qa.json` — the hidden-div and wrong-abstract states (V4-03) |
| `2cc590620c3f8844c907c93a8151f3dcc102b8cd2a2c25e92e334b1b6c4b37ab` | 2,445 | `pdf_visual_qa.json` — the stylesheet path and page count (V4-08) |
| `dc45e0aa32bc3928ae8862c44618c784d77f5b7b64430724b20eb74669cbacbb` | 4,196 | `portability_threshold_qa.json` — rational oracle vs both implementations (V4-09) |
| `1c695e21f53adb2ade56082e5d671db6304af4a2895266ded77cb6c6c3b5060c` | 211 | `git_checkout_qa.json` — LF and CRLF pinned checkouts (V4-10) |
| `eb5dbfb1c1a59b2618233e4be65121ca73a543b38009afa915cad6d6c285e326` | 261 | `archive_qa.json` — historyless source archive (V4-06) |
| `f25bdd8816c7df9fe40be790f85a5fc0026f40319e9b934672da58f306f3bdb6` | 13,043 | `reader_claim_matches.txt` — the active surfaces carrying superseded claims (V4-04) |

Hashes are over the bytes as stored. `audits/** -text` in `.gitattributes` keeps a
checkout from rewriting line endings, so these hashes hold on every platform — the
defect Astra recorded as A14 and that this directory would otherwise repeat.

## The external binding Astra recorded

Section D of the review records the review-time SHA-256 of this repository's offline
evidence transcript:

```
V2_EVIDENCE_ANCHOR.json   cc31e9b2f43d9a4ca6332e0e300e7f0c391c59c17dfe32804269800446ab9827
```

Astra confirmed independently, by `git cat-file --batch` against the real v2 objects at
`17e08f3e92533ff8266b1b586e35f20da2923da8`, that all 858 entries in that transcript match.
This is worth more than it looks: a transcript distributed beside the data it describes
cannot authenticate that data (V4-06), and a hash of it published by a **third party** is
exactly the external binding the offline mode lacks. `v2_anchor.py` deliberately does not
contain this hash — a reference stored next to what it authenticates would have the same
defect.

## What was NOT established

- No v4 ZIP was reviewed; none exists. Nothing here certifies an unpublished archive.
- The 13-stage workflow is not archive-only runnable: stage 9 needs `git archive HEAD`.
- The review establishes readiness defects. It does not authorise publication.

## Response

Every finding is dispositioned in
[`../../V4_ASTRA_CORRECTION_LEDGER.md`](../../V4_ASTRA_CORRECTION_LEDGER.md), which
covers A01–A14 (the v3 audit) and V4-01–V4-10 (this one).
