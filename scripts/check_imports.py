#!/usr/bin/env python3
"""CI gate: fail if any import uses unapproved packages.

This script parses pyproject.toml to extract the approved dependencies,
and then scans all Python files in the prism/ directory for imports.
If an import is found that belongs to a non-standard-library package
that is not listed in pyproject.toml, the CI gate fails.
"""

import sys
import ast
import re
from pathlib import Path

# Standard library modules (a reasonably comprehensive heuristic list for Python 3.11)
STDLIB = {
    "abc", "argparse", "array", "ast", "asyncio", "atexit", "base64", "binascii", "bisect", "builtins",
    "calendar", "cmath", "cmd", "code", "codecs", "codeop", "collections", "colorsys", "compileall",
    "concurrent", "configparser", "contextlib", "contextvars", "copy", "copyreg", "csv", "ctypes", "curses",
    "dataclasses", "datetime", "dbm", "decimal", "difflib", "dis", "doctest", "email", "encodings",
    "ensurepip", "enum", "errno", "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch", "fractions",
    "ftplib", "functools", "gc", "getopt", "getpass", "gettext", "glob", "graphlib", "gzip", "hashlib",
    "heapq", "hmac", "html", "http", "imaplib", "imghdr", "imp", "importlib", "inspect", "io", "ipaddress",
    "itertools", "json", "keyword", "lib2to3", "linecache", "locale", "logging", "lzma", "mailbox",
    "mailcap", "marshal", "math", "mimetypes", "mmap", "modulefinder", "multiprocessing", "netrc",
    "nis", "nntplib", "numbers", "opcode", "operator", "optparse", "os", "pathlib", "pdb", "pickle",
    "pickletools", "pkgutil", "platform", "plistlib", "poplib", "posix", "pprint", "profile", "pstats",
    "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random", "re", "readline",
    "reprlib", "rlcompleter", "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex",
    "shutil", "signal", "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "sqlite3",
    "sre_compile", "sre_constants", "sre_parse", "ssl", "stat", "statistics", "string", "stringprep",
    "struct", "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny", "tarfile",
    "telnetlib", "tempfile", "termios", "textwrap", "threading", "time", "timeit", "tkinter", "token",
    "tokenize", "tomllib", "trace", "traceback", "tracemalloc", "tty", "turtle", "turtledemo", "types",
    "typing", "unicodedata", "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
    "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile",
    "zipimport", "zlib", "zoneinfo"
}

def get_approved_packages() -> set[str]:
    """Parse pyproject.toml to extract package names."""
    approved = set()
    try:
        content = Path("pyproject.toml").read_text()
        # Find the dependencies list
        deps_match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if deps_match:
            deps_block = deps_match.group(1)
            # Extract strings like "httpx[http2]" or "pydantic>=2.0"
            packages = re.findall(r'["\']([^"\']+)["\']', deps_block)
            for pkg in packages:
                # Strip extras and versions
                clean_pkg = re.split(r'\[|>=|==|<=|<|>', pkg)[0].strip().replace("-", "_")
                approved.add(clean_pkg.lower())
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
    
    # Also add the project's own module
    approved.add("prism")
    return approved

def extract_imports(filepath: Path) -> set[str]:
    """Extract top-level imported modules from a Python file."""
    imports = set()
    try:
        tree = ast.parse(filepath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    # Get base module
                    base = name.name.split(".")[0]
                    imports.add(base)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base = node.module.split(".")[0]
                    imports.add(base)
    except Exception as e:
        print(f"Failed to parse {filepath}: {e}")
    return imports

def main() -> None:
    approved_packages = get_approved_packages()
    violations = []

    for path in Path("prism").rglob("*.py"):
        file_imports = extract_imports(path)
        for imp in file_imports:
            # Check if it's a known standard library module
            if imp in STDLIB:
                continue
            
            # Check if it's an approved package (ignoring case and underscores)
            imp_normalized = imp.lower().replace("-", "_")
            if imp_normalized not in approved_packages:
                violations.append((path, imp))

    if violations:
        print("IMPORT AUDIT FAILED — Disallowed packages found per AGENTS.md §1.3:")
        for path, imp in violations:
            print(f"  ✗ {path} imports '{imp}' (not in pyproject.toml)")
        sys.exit(1)

    print("✓ Import audit passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
