#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
import re

RULE_RE = re.compile(r'^dimwishlist:item=(-?)(\\d+)&perks=([^#]*)#notes:(.*)$')
DIM_RE = re.compile(r'^dimwishlist:item=(-?\\d+)(?:&perks=)?([\\d|,]*)(?:#notes:)?([^|]*)')

BASE_SHA = "08063a43baccaf360d7551ffcd51475d50a7fdc4"
VERSION = "v1.0.1"
FIREFRIGHT_HASH = 2778013407

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def serialize_notes(notes):
    notes = re.sub(r'\\s*\\|\\s*', '; ', notes.strip())
    notes = notes.replace('score-model:v1.0', 'score-model:v1.0.1')
    return notes

def canonical_for_compare(notes):
    notes = re.sub(r'\\s*\\|\\s*', '; ', notes.strip())
    notes = notes.replace('score-model:v1.0.1', 'score-model:v1.0')
    return notes

def signature(match):
    return (bool(match.group(1)), int(match.group(2)), match.group(3))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--audit", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    src = pathlib.Path(args.source).read_text(encoding="utf-8")
    source_lines = src.splitlines()
    out_lines = []

    source_rules = []
    output_rules = []
    old_note_pipe_rules = 0
    new_note_pipe_rules = 0
    semantic_diffs = []
    signature_diffs = []
    firefright_visible = False
    firefright_notes = None

    for line_no, line in enumerate(source_lines, 1):
        m = RULE_RE.match(line)
        if not m:
            new_line = line
            if line.startswith("description:[v1.0 "):
                new_line = line.replace("description:[v1.0 ", "description:[v1.0.1 ", 1)
            elif line.startswith("// 2026 Return v1.0 "):
                new_line = line.replace("// 2026 Return v1.0 ", "// 2026 Return v1.0.1 ", 1)
            out_lines.append(new_line)
            continue

        old_notes = m.group(4)
        if "|" in old_notes:
            old_note_pipe_rules += 1

        new_notes = serialize_notes(old_notes)
        if "|" in new_notes:
            new_note_pipe_rules += 1

        new_line = f"dimwishlist:item={m.group(1)}{m.group(2)}&perks={m.group(3)}#notes:{new_notes}"
        out_lines.append(new_line)

        nm = RULE_RE.match(new_line)
        source_rules.append((line_no, signature(m), old_notes))
        output_rules.append((line_no, signature(nm), new_notes))

        if signature(m) != signature(nm):
            signature_diffs.append({"line": line_no, "before": signature(m), "after": signature(nm)})

        if canonical_for_compare(old_notes) != canonical_for_compare(new_notes):
            semantic_diffs.append({
                "line": line_no,
                "before": canonical_for_compare(old_notes),
                "after": canonical_for_compare(new_notes),
            })

        dm = DIM_RE.match(new_line)
        visible_notes = dm.group(3) if dm else None
        if visible_notes != new_notes:
            semantic_diffs.append({
                "line": line_no,
                "reason": "DIM parser did not expose the complete note",
                "expected": new_notes,
                "visible": visible_notes,
            })

        if int(m.group(2)) == FIREFRIGHT_HASH and "match:fox-favorite" in new_notes:
            firefright_notes = new_notes
            required = ("CPVE:50", "PVE:76E", "CPVP:50", "PVP:63E", "match:fox-favorite", "evidence:favorite")
            firefright_visible = dm is not None and all(x in visible_notes for x in required)

    out_text = "\\n".join(out_lines) + "\\n"

    if len(source_rules) != len(output_rules):
        signature_diffs.append({"reason": "rule count changed", "before": len(source_rules), "after": len(output_rules)})

    header_ok = any(x.startswith("description:[v1.0.1 ") for x in out_lines[:5]) and any(
        x.startswith("// 2026 Return v1.0.1 ") for x in out_lines[:12]
    )

    audit = {
        "candidate_version": VERSION,
        "base_v1_commit": BASE_SHA,
        "source_sha256": sha256_text(src),
        "candidate_sha256": sha256_text(out_text),
        "source_rules": len(source_rules),
        "candidate_rules": len(output_rules),
        "source_rules_with_pipe_in_notes": old_note_pipe_rules,
        "candidate_rules_with_pipe_in_notes": new_note_pipe_rules,
        "signature_differences": len(signature_diffs),
        "semantic_differences": len(semantic_diffs),
        "header_version_ok": header_ok,
        "firefright_full_note_visible_to_dim_parser": firefright_visible,
        "firefright_notes": firefright_notes,
        "failures": {
            "signature_differences": signature_diffs[:20],
            "semantic_differences": semantic_diffs[:20],
        },
    }

    pathlib.Path(args.output).write_text(out_text, encoding="utf-8")
    pathlib.Path(args.audit).write_text(json.dumps(audit, indent=2), encoding="utf-8")
    pathlib.Path(args.report).write_text(
        "# Fox Armory 2026 Return — v1.0.1 DIM Note Serialization Fix\\n\\n"
        f"- Base v1.0 commit: {BASE_SHA}\\n"
        f"- Rules audited: **{len(source_rules)}**\\n"
        f"- v1.0 rules whose notes contained DIM-terminating pipes: **{old_note_pipe_rules}**\\n"
        f"- v1.0.1 rules whose notes still contain pipes: **{new_note_pipe_rules}**\\n"
        f"- Rule signature changes: **{len(signature_diffs)}**\\n"
        f"- Semantic note changes beyond delimiter/model-version serialization: **{len(semantic_diffs)}**\\n"
        f"- Firefright full metadata visible through DIM-equivalent parser: **{firefright_visible}**\\n"
        f"- Candidate SHA-256: {sha256_text(out_text)}\\n\\n"
        "## Fix\\n\\n"
        "DIM's current wishlist parser captures #notes only until the first pipe character. "
        "v1.0 used pipes as metadata separators, causing DIM to display only the first field. "
        "v1.0.1 replaces note-field pipes with semicolon separators and bumps score-model:v1.0 to "
        "score-model:v1.0.1. Item hashes, positive/negative state, perk lists, scores, classifications, "
        "ordering, and coverage remain unchanged.\\n",
        encoding="utf-8",
    )

    print(json.dumps(audit, indent=2))
    if signature_diffs or semantic_diffs or new_note_pipe_rules or not header_ok or not firefright_visible:
        raise SystemExit("v1.0.1 serialization audit failed")

if __name__ == "__main__":
    main()
