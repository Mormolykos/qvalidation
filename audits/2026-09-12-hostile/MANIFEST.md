# Hostile audit of qvalidation v2 — preserved evidence, 2026-09-12

These two files are **immutable audit evidence**. They are preserved exactly as the
auditor produced them and are never edited, reformatted, summarised in place, or
corrected — including where this project later disputes a finding. A dispute is recorded
in `V3_CORRECTION_LEDGER.md`, never by altering the audit.

## What was audited

Published Zenodo v2, DOI `10.5281/zenodo.22689920`, at commit
`17e08f3e92533ff8266b1b586e35f20da2923da8`. The audit ran in a separate temporary copy;
the repository itself was not modified, and `results/raw/` is unchanged since v2.

## Preserved bytes

| file | bytes | SHA-256 |
|---|---|---|
| `HOSTILE_AUDIT.md` | 37,910 | `34574eaa95162ec3314fc181ab955a78dcc6de7d2f9424b3c457fb4061311999` |
| `CLAIM_LEDGER.md` | 5,679 | `486fd96ec1ba3d635a9326b7ac1745935ccb502518f4ea7a3caab37cb6c4507d` |

`CLAIM_LEDGER.md` was constructed by the auditor **before** it inspected any prior review,
so it is an independent enumeration of what the manuscript claims.

## Verdict, as delivered

**CORE SURVIVES, MAJOR CORRECTIONS REQUIRED.** 22 findings, six attacks defeated, and
**no fatal chain**.

Independently reconstructed and reproducing: **12/26** risk-bootstrap intervals excluding
zero, **7/26** risks ≥ 5%, **4/26** risks ≥ 10%, and all 36 reported risk-bootstrap
intervals.

## The finding that matters most

A mutation of the **raw primary dataset** moves the endpoint to **11/26, 6/26, 3/26**
while `verify.py` still reports **6/6 PASS**.

This does not invalidate the measurements. It invalidates the claim that the verification
apparatus protects them. The empirical result survived; the assurance layer did not.

That distinction is the reason this directory exists rather than a quiet fix: a verifier
that always agrees is worthless, and the only evidence that one is worth anything is a
demonstration that it can turn red.
