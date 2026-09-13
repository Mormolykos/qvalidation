# V4 fresh attack ledger — initial, before correction-ledger inspection

Target 4531d97d754c9f116db567e1908cbb59d6016eb2. Detached clean clone, fetched origin/master equal; see PREFLIGHT.json. Formed from verifier/new stage implementations and manuscript. No v4 correction ledger, SETTLED explanations or previous report opened in this v4 audit. One search incidentally returned a prior-audit code excerpt; it was not used as authority. Earlier conversation necessarily contains the v3 findings; every proposed v4 bypass below comes from current implementation inspection and remains untested unless stated otherwise.

| Claim and source | Actual authority observed in source | Falsifying experiment | Independently tested now? |
|---|---|---|---|
| verify.py:18–31:13 checks certify repository intact | Sequential subprocess return codes; stages share imports/inputs | Materially false artifact with13PASS; dependency/instrumentation map | Source read only |
| verify.py:24 / PAPER.md:67–68,668–670:every quantitative figure recomputed | paper_check partial values/string presence; inventory44 values | Change nonheadline number or row attribution while valid table remains | No |
| derived_binding.py:1,13–27:every saved primary field replays original algorithm | prereg_analysis.analyse;18 named fields plus dictionary of circuit rows | H;NaN bound;fractional integer metadata;invalid false boolean;duplicate rows/columns;unlisted topology field | No |
| derived_binding.py:104–120:membership and row count | Dict comprehension collapses duplicate circuit IDs before count | Duplicate row,contradictory earlier row,extra column | No |
| derived_binding.py:75–86,136–150:numeric/boolean equality | int(float(raw));permissive false conversion;abs(float diff)>tol | 200.9 seeds;arbitrary false token;NaN CI or theta | No |
| manuscript_binding.py:14–25:reader-visible unique GFM table | Removes HTML comments only;line-oriented pipe splitting | Hidden div/details/fence,raw HTML table,blockquote,escaped pipes,duplicate rows,Unicode/NBSP | No |
| manuscript_binding.py:138–177:contradictory prose detected | Fractions with denominator26;any correct numerator exempt;counterfactual keywords exempt whole paragraph | Wrong risk attribution using another correct numerator;worded headline;paragraph containing audit/would | No |
| pdf_binding.py:10–16,123–124:same active semantic claims | Presence of three fractions anywhere;version line;6 forbidden phrases;source-nearby withdrawal exemptions | False per-circuit table/issue/abstract;correct fractions only invisible PDF text;stale PDF withversionline | No |
| v2_anchor.py:15–34:historical identity from v2 Git objects | Git show hardcoded commit when available | Raw+manifest+anchor in full history;git replace;missing history fallback | No |
| v2_anchor.py:133–140:offline anchor bound to v2 | Mutable JSON hash list plus equality of commit-name string | Change raw+anchor+manifest+summary in historyless archive;remove expected entries | No |
| v2_anchor.py:85–92,192:byte identity/canonical identity | CRLF→LF normalization;source SHA256 | CRLF raw accepted byhistorical check butnotbyte-identical;assurance wording | No |
| v2_anchor.py:57–62,169–170:78 primary arms+780 duplicate fragments | Recursivefile enumeration;labelbased onpathsubstring;no merge reconciliation | Compare complete record multisets;mutatefragment only;loader openedpaths trace | No |
| pin_check.py:16–18:canonical portable pin | benchpress_canonical_pin plus live commit/dirty checks | CompareGit/LF/CRLF;fallbackmetadata;historylessexternalcheckout | No |
| mutation_test.py:main:required layer catches each mutant | Nonzero exit accepted;no failure-message validation;git archiveHEAD snapshots | Injectcase-specificexceptioninto test copy layer,all11 built-ins failwrongreason | Source read only |
| publish/build_paper.sh:7–8:text AND layout reproduced/checked | Pandoc+fixedWindowsChromepath;CSS hrefpublish/paper_style.css inpublish/paper.html | ResolveCSS URL;differentfonts/layout;stage13extractabletextonly | No |
| PAPER.md:21–35,241–244,400s:primarycounts/modelband | Raw39×2 panels;prioranalysisoriginalbootstrapandseparateexactestimator | Independent integerconvolution/bootstrap/band replay withno projectimports | No |
| PAPER.md:40–43,514:issue own protocol / not reproduced | Externalissue+localratio-of-means/protocolunknown | Primarysourcecheck andcross-sectioncomparison | Apparent contradiction only |
| PAPER.md:160–166,285–286,548–549:limitedrepeatability/everycount reproduced/argumentremovesvariance | Logged0/24 and216counts;unseededbackend remains | Scope ofcontrols versus15600measurements;remainingunqualifiedclaim | Apparent contradiction only |
| PAPER.md:206,217–222,319,664:beforedata/machineexisted versusonlycommitorder | LocalGit history | Inspectchronologyandverifierdescriptions;nonaccessisnotGitfact | Apparent contradiction only |
| Release PDF/ZIP/bundle/SETTLED currentscope | Targettracksbuildinputs,notPDF;stagedpathsawaited | Hash/bytecomparearchive;stale activecopy;changePDFonly;releaseZIPdivergence | Artifactpathsrequested |

Priority: obtain a materially false visible artifact with all13actualstages passing; do not call a single-stagepass a fullpass. Maintain independent rawreconstruction separately fromreplayedsharedcode. Record knownF/H/Kclosure and at leastfive newHmutants; testevery requestedMarkdown/PDFsurface. No severity or finalverdict inferred from source inspection alone.
