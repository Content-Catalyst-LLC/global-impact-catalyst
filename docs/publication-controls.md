# Publication and Withdrawal Controls

A publication begins as a draft bound to the SHA-256 hash of its subject snapshot. Publishing requires:

1. an approval decision for the same subject;
2. a submitted quality assessment meeting the configured threshold;
3. no open correction records for the subject; and
4. a current subject hash identical to the draft hash.

If content changes after the draft is created, the draft cannot be published. A new publication draft must be created so the approval and quality records correspond to the exact released content.

Published records preserve the approval decision, quality assessment, revision snapshot, publisher, publication time, and event history. Withdrawal requires a reason and appends a withdrawal event. It does not delete the release.

Publication workflow documents internal governance. It is not external assurance, ESG verification, regulatory approval, or causal validation.
