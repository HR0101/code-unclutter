#!/usr/bin/env python3
"""
scripts/scanner.py - Code Smells & Metrics Scanner for code-unclutter
Detects smells from '100 Refactorings Catalog' across files, modules, or git diffs.
Zero external dependencies (uses standard library only).
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path


class CodeSmellDetector:
    def __init__(self, target_path, is_diff=False, symbol_filter=None):
        self.target_path = Path(target_path) if target_path else None
        self.is_diff = is_diff
        self.symbol_filter = symbol_filter
        self.results = []

    def run(self):
        files_to_scan = self._get_files()
        for f in files_to_scan:
            try:
                self._scan_file(f)
            except Exception as e:
                # Log scan failure without crashing
                self.results.append({
                    "file": str(f),
                    "line": 0,
                    "rule_id": "SCAN_ERROR",
                    "severity": "info",
                    "message": f"Could not parse file: {e}"
                })
        return self.results

    def _get_files(self):
        if self.is_diff:
            cmd = ["git", "diff", "--name-only", "--diff-filter=d", "HEAD"]
            try:
                out = subprocess.check_output(cmd, text=True).strip().splitlines()
                return [Path(p) for p in out if Path(p).is_file() and self._is_supported(p)]
            except Exception:
                return []

        if not self.target_path:
            return []

        if self.target_path.is_file():
            return [self.target_path] if self._is_supported(self.target_path) else []

        valid_files = []
        for p in self.target_path.rglob("*"):
            if p.is_file() and self._is_supported(p):
                # ignore common build/git directories
                parts = p.parts
                if any(x in parts for x in [".git", "node_modules", "dist", "build", ".venv", "__pycache__"]):
                    continue
                valid_files.append(p)
        return valid_files

    def _is_supported(self, path):
        ext = Path(path).suffix.lower()
        return ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".php", ".rb"]

    def _scan_file(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.splitlines()

        ext = file_path.suffix.lower()

        # 1. Regex / line-based heuristics (universal across languages)
        self._scan_universal_patterns(file_path, lines)

        # 2. Python-specific AST scanning
        if ext == ".py":
            self._scan_python_ast(file_path, content)

    def _scan_universal_patterns(self, file_path, lines):
        nested_indent_level = 0
        in_multiline_comment = False

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Check Yoda conditions (No.75 Modern Override)
            yoda_match = re.search(r'\b(if|while)\s*\(\s*(?:\d+|true|false|null|nil|None)\s*([=!]=)\s*[a-zA-Z_]', line)
            if yoda_match:
                self.results.append({
                    "file": str(file_path),
                    "line": idx,
                    "rule_id": "R-075-MODERN-REJECT",
                    "category": "Modern Override",
                    "source_no": 75,
                    "severity": "warning",
                    "message": f"Found Yoda condition: '{yoda_match.group(0)}'. Modern standard enforces natural order ('x == const')."
                })

            # Check Swallowed Exception (No.71)
            if re.search(r'catch\s*\([^)]*\)\s*\{\s*\}', line) or re.search(r'except(?:\s+\w+)?:\s*(?:pass|\.\.\.)', line):
                self.results.append({
                    "file": str(file_path),
                    "line": idx,
                    "rule_id": "R-071",
                    "category": "Quick-Wins (P1)",
                    "source_no": 71,
                    "severity": "critical",
                    "message": "Swallowed exception detected. Must log or re-throw."
                })

            # Check Magic Numbers (No.05)
            # Find numbers >= 10 not declared in a const/variable assignment
            magic_num_matches = re.finditer(r'(?<![a-zA-Z0-9_#$])([1-9]\d{2,})(?![a-zA-Z0-9_])', line)
            for m in magic_num_matches:
                val = m.group(1)
                # Ignore ports like 8080 or HTTP status 200, 404, 500 if common, but flag suspicious numbers
                if not re.search(r'(const|final|let|var|val|\b[A-Z_]{3,}\b)\s*=', line):
                    self.results.append({
                        "file": str(file_path),
                        "line": idx,
                        "rule_id": "R-005",
                        "category": "Quick-Wins (P1)",
                        "source_no": 5,
                        "severity": "low",
                        "message": f"Potential magic number literal '{val}'. Extract to named constant."
                    })

            # Check Indent depth for Deep Nesting (No.04 / No.51)
            indent = len(line) - len(line.lstrip())
            # Assuming 2 or 4 spaces per indent
            estimated_depth = indent // 4 if indent % 4 == 0 else indent // 2
            if estimated_depth >= 4 and any(kw in line for kw in ["if ", "for ", "while ", "switch "]):
                self.results.append({
                    "file": str(file_path),
                    "line": idx,
                    "rule_id": "R-051",
                    "category": "Quick-Wins (P1)",
                    "source_no": [4, 51],
                    "severity": "high",
                    "message": f"Deep nesting detected (depth ~{estimated_depth}). Refactor with guard clause."
                })

    def _scan_python_ast(self, file_path, content):
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            # Check function length (No.01 Long Function / No.26 Extract Function)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self.symbol_filter and node.name != self.symbol_filter:
                    continue

                loc = (node.end_lineno - node.lineno) if hasattr(node, 'end_lineno') else len(node.body)
                if loc > 35:
                    self.results.append({
                        "file": str(file_path),
                        "line": node.lineno,
                        "symbol": node.name,
                        "rule_id": "R-001-026",
                        "category": "Logic Purification (P2)",
                        "source_no": [1, 26],
                        "severity": "medium",
                        "message": f"Long function '{node.name}' ({loc} lines). Target for function extraction."
                    })

                # Check argument count (No.07 Long Parameter List / No.33 Parameter Object)
                num_args = len(node.args.args)
                if num_args >= 5:
                    self.results.append({
                        "file": str(file_path),
                        "line": node.lineno,
                        "symbol": node.name,
                        "rule_id": "R-007-033",
                        "category": "Logic Purification (P2)",
                        "source_no": [7, 33],
                        "severity": "medium",
                        "message": f"Function '{node.name}' has {num_args} parameters. Bundle into Parameter Object."
                    })

                # Check swallowed exception inside Python AST
                for sub in ast.walk(node):
                    if isinstance(sub, ast.ExceptHandler):
                        if len(sub.body) == 1 and isinstance(sub.body[0], (ast.Pass, ast.Expr)):
                            self.results.append({
                                "file": str(file_path),
                                "line": sub.lineno,
                                "symbol": node.name,
                                "rule_id": "R-071",
                                "category": "Quick-Wins (P1)",
                                "source_no": 71,
                                "severity": "critical",
                                "message": f"Empty exception handler (pass) in '{node.name}'."
                            })


def format_report(results, as_json=False):
    if as_json:
        return json.dumps({"total_smells": len(results), "smells": results}, indent=2)

    if not results:
        return "[CLEAN] No immediate code smells detected! Codebase meets Phase 1 cleanliness standards."

    # Group by category / priority
    p1_items = [r for r in results if "P1" in r.get("category", "") or r.get("severity") in ["critical", "high"]]
    p2_items = [r for r in results if "P2" in r.get("category", "")]
    overrides = [r for r in results if "Modern Override" in r.get("category", "")]
    others = [r for r in results if r not in p1_items and r not in p2_items and r not in overrides]

    lines = [
        f"# [CLEAN] Code Unclutter Scan Report ({len(results)} issues found)",
        "",
        f"- [P1] **High-Priority Quick-Wins (P1 - まず直す)**: {len(p1_items)}",
        f"- [P2] **Logic Purification Candidates (P2)**: {len(p2_items)}",
        f"- [WARN] **Modern Best Practice Violations**: {len(overrides)}",
        f"- [INFO] **Other / Info**: {len(others)}",
        "",
        "---",
        "## [P1] [Phase 1] High-Priority Quick-Wins (Immediate Action)",
    ]

    for item in p1_items[:15]:
        sym = f" `[{item['symbol']}]`" if "symbol" in item else ""
        lines.append(f"- **{item['file']}:{item['line']}**{sym} - `{item['rule_id']}`: {item['message']}")

    if len(p1_items) > 15:
        lines.append(f"- *(...and {len(p1_items) - 15} more Phase 1 items)*")

    lines.extend([
        "",
        "## [P2] [Phase 2] Logic & Scope Candidates",
    ])
    for item in p2_items[:10]:
        sym = f" `[{item['symbol']}]`" if "symbol" in item else ""
        lines.append(f"- **{item['file']}:{item['line']}**{sym} - `{item['rule_id']}`: {item['message']}")

    if overrides:
        lines.extend([
            "",
            "## [WARN] Modern Best-Practice Overrides",
        ])
        for item in overrides:
            lines.append(f"- **{item['file']}:{item['line']}** - {item['message']}")

    lines.extend([
        "",
        "---",
        "[TIP] **Recommended Next Step**: Run `code-unclutter --mode quick-win` to automatically resolve P1 issues safely."
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Code Unclutter Smell Scanner")
    parser.add_argument("path", nargs="?", default=".", help="Target file or directory to scan")
    parser.add_argument("--diff", action="store_true", help="Scan only git changed/staged files")
    parser.add_argument("--symbol", help="Filter for specific function or class name")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")

    args = parser.parse_args()

    detector = CodeSmellDetector(
        target_path=args.path,
        is_diff=args.diff,
        symbol_filter=args.symbol
    )
    results = detector.run()
    print(format_report(results, as_json=args.json))


if __name__ == "__main__":
    main()
