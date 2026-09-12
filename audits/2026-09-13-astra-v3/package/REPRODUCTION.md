# Exact reproduction commands

All original/audited-source files are read-only inputs. Output is confined to this audit directory and disposable copies. Interpreter: Python3.10.10,NumPy2.2.6,SciPy1.15.3. PDF tooling was installed only into this audit directory’s pdfdeps. The pinned snapshot was created with git clone --no-hardlinks --no-checkout, then a detached checkout of the full target hash.

```powershell
$audit = 'C:\Users\User\AppData\Local\Temp\astra-v3-839ac80-h1_mhdhj'
$py = 'C:\Users\User\Desktop\research\qvalidation\envs\bp202\Scripts\python.exe'
$env:BENCHPRESS_PATH = 'C:\Users\User\Desktop\benchpress_test'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
Set-Location $audit
& $py independent.py snapshot independent.json
& $py bootstrap_replay.py
& $py supplementary.py
& $py integrity_history.py
& $py metadata_checks.py
& $py final_numeric_checks.py
```

integrity_history.py creates autocrlf_true and autocrlf_false disposable clones. Run in a fresh audit directory when reproducing, as scripts refuse to overwrite existing mutation copies. independent.py checks saved summaries **only after** constructing all raw-derived rows. Its counts.boundary field is the all-circuit flag count13; resolved boundary exclusions are10. The original bootstrap stream is replayed separately, not substituted by the exact-inner stream.

```powershell
Set-Location "$audit\snapshot"
& $py verify.py
Set-Location $audit
& $py mutations.py A
& $py mutations.py B
& $py mutations.py C
& $py mutations.py C2
& $py mutations.py D
& $py mutations.py E
& $py mutations.py F
& $py mutations.py G
& $py mutations.py H --full
& $py mutations.py I
& $py mutations.py J
& $py mutations.py K --full
& $py edge_cases.py
Set-Location "$audit\mutF"
& $py verify.py
Set-Location $audit
pandoc mutK/PAPER.md --from=markdown+pipe_tables+raw_html --to=plain --wrap=none --output=mutK_rendered.txt
```

Mutation G calls the actual prereg_analysis.analyse function for the changed circuit and rewrites that row using its returned values; all other rows are untouched. No tests are disabled. Stage9 deliberately archives HEAD, so its own test snapshots remain pristine regardless of current worktree mutation. This is documented behavior, not an audit workaround.

PDF commands used (the stylesheet is an external author-supplied input absent from the target):

```powershell
pandoc snapshot/PAPER.md --from=markdown+pipe_tables+raw_html --to=html5 --standalone --css='C:/Users/User/Desktop/bad/paper_style.css' --output=rebuilt.html
pandoc snapshot/PAPER.md --from=markdown+pipe_tables+raw_html --to=plain --wrap=none --output=manuscript_plain.txt
```

Headless Microsoft Edge (Chromium) was launched with a separate scratch user-data directory and arguments --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 --print-to-pdf=<audit>/rebuilt.pdf file:///<audit>/rebuilt.html. The process was launched with WindowStyle Hidden. The supplied original PDF was not overwritten. PyMuPDF renders/compares the results in pdf_audit.py. Its extracted-character count differs by extractor from the user’s quoted count; whitespace-normalized staged/rebuilt text is identical.

```powershell
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pdf_audit.py
```

PDF/ZIP paths and hashes are captured in pdf_audit.json. All1,034 archived tracked files were compared with a fresh git archive HEAD, not with the mutable original working tree. The new external toolchain portability check is in metadata_checks.py: each source Git blob equals the CRLF checkout converted to LF, and all five LF hashes fail the recorded comparison.

Read ASTRA_FINAL_HOSTILE_AUDIT.md for exact claim locations, caveats and conclusions. Findings and results are also available as JSON. The report can be regenerated using build_report.py; this writes review artifacts only.
