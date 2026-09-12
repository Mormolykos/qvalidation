# Mutation-test ledger

Target 839ac80cd36ac44c7bab12e3b5a19c9dceb95c76. All mutations are in disposable sibling clones. Source checker code is unchanged except the deliberately mutated data/document. A full-pass result means the actual unmodified verify.py completed all nine stages with exit success. Individual-stage results mean those exact stage programs ran, not a simulated nine-stage result. The full baseline also passes the supplied A–E self-test using git-archive snapshots.

“Science changed” distinguishes actual raw empirical changes from false published claims or uncertainty artifacts. Updating a local manifest never restores identity with the trusted v2 raw bytes.

| ID | Mutation | Scientific impact | Raw integrity impact | Observed result | Reason |
|---|---|---|---|---|---|
| A | One knn_n67 candidate observation 619→10,000,000 | Yes: unresolved;11/25,6/25,3/25 | Yes | 7 FAIL;8 FAIL;6 PASS | Correct: raw classifications/counts and hash disagree |
| B | One knn_n67 candidate observation 619→620 | Yes: small individual risk/theta change;headline unchanged | Yes | 7 PASS;8 FAIL;6 PASS | Correct: integrity rejects bytes/summary drift |
| C | Supplied-style candidate arm×1.09 rounded | Yes: verdict/risk change;eligibility unchanged | Yes | 7 FAIL;8 FAIL;6 PASS | Caught, but the supplied label claiming eligibility movement is inaccurate |
| C2 | One candidate observation 619→3619 | Yes: becomes boundary/unresolved;eligible25 | Yes | 7 FAIL;8 FAIL;6 PASS | Correct: actual boundary/eligibility-changing case |
| D | First saved summary point risk→.999999 | Published derived science changes;raw unchanged | No | 7 PASS;8 FAIL;6 PASS | Correct: summary point-risk mismatch |
| E | Visible ≥5% count7→9 only | Published claim changes;raw unchanged | No | 7 FAIL;8 PASS;6 PASS | Correct: new science stage catches this simple literal edit |
| F | multiplier_n45 candidate7315→7316;regenerate manifest | Yes:exact risk .028724114619→.028726752146;headline unchanged | Yes relative to v2;new manifest self-consistent | FULL 9/9 PASS | Missed immutable-evidence violation;A03 |
| G | knn_n67 candidate619→620;regenerate its row with prereg_analysis.analyse and manifest | Yes:individual risk/theta/intervals;headline unchanged | Yes relative to v2 | 7 PASS;8 PASS;6 FAIL | Correct detection at printed risk rounding16.71 versus16.70 |
| H | All36 saved risk intervals→[.900000,.999999],flags/counts unchanged | Published uncertainty changes;raw unchanged | No | FULL 9/9 PASS | Missed interval inconsistency;A01 |
| I | Issue knn_341 value+44.060%→+94.060% | Published external numeric claim changes | No | 7 PASS;8 PASS;6 PASS | Uncovered claim;no full9-stage claim for this case |
| J | One raw file LF→CRLF;semantic records identical | No | Yes:representation changes | 7 PASS;8 FAIL;6 PASS | Correct under byte-preservation contract;not a scientific discrepancy |
| K | Visible headline fractions→0/26;correct rows in invisible HTML comment | Published primary claim changes;raw unchanged | No | FULL 9/9 PASS | Missed visible-table corruption;A02 |

The supplied whole-arm constant-100 attack is additionally executed by baseline stage9 and caught; it yields11/26,6/26,3/26. Our single-observation A yields11/25,6/25,3/25, because the circuit becomes unresolved. C2 supplements the supplied C because ×1.09 changes reference side, not boundary/eligibility.

Reproduction: [mutations.py](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/mutations.py); [REPRODUCTION.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/REPRODUCTION.md). Per-case exact changes, return codes and durations are in mut*_result.json, with complete stage output in mut*_*.log. Full verifier logs: baseline.log,mutH_full.log,mutK_full.log,mutF_full.log. Mutation K’s rendered false rows are in mutK_rendered.txt.
