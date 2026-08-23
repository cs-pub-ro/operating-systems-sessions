#!/usr/bin/env python3
"""What counts as a session, and what counts as a task.

Shared by the two things that walk the repository: `gen_pages.py`, which
renders the website, and `gen_zip.py`, which packs the archives handed to
students.  Both have to agree on the answer, so the rule lives here once.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directory names that are never part of a session, at any depth.  `solutions`
# is the important one: it holds the reference solutions, and the flags of the
# session 05 challenges.
EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".claude",
    "_site",
    "archives",
    "docs",
    "node_modules",
    "scripts",
    "site",
    "solutions",
}

# Top-level directories that are treated as sessions.
#
# A session is the student-facing `NN-<name>-work/` directory: the skeletons,
# tasks and hints used during the live lab.  Its sibling `NN-<name>-full-contents/`
# is the reference material -- solutions, and for session 05 the challenge flags
# and exploits -- and is deliberately *not* a session: it is neither published
# on the website nor packed into a student archive, exactly as the old
# `solutions/` directories never were.  The legacy `session-NN-*` form is still
# recognised so nothing breaks if such a directory reappears.
SESSION_PATTERN = re.compile(r"^(?:session-\d+|\d+-.+-work$)")

# Words that plain title casing would get wrong when building a label out of a
# directory name.
ACRONYMS = {
    "os": "OS",
    "io": "IO",
    "db": "DB",
    "gdb": "GDB",
    "json": "JSON",
    "cylab": "CyLab",
}


def prettify(name):
    """Turn a directory name such as `01-string-functions` into a label."""
    without_prefix = re.sub(r"^(?:session-\d+|\d+|bonus|demo)[-_]", "", name)
    # Session directories carry a `-work` / `-full-contents` suffix that is
    # plumbing, not part of the label.
    without_prefix = re.sub(r"[-_](?:work|full-contents)$", "", without_prefix)
    words = re.split(r"[-_]+", without_prefix.strip())
    return " ".join(ACRONYMS.get(word.lower(), word.title()) for word in words if word)


def read_title(readme_path, fallback):
    """Return the first level-one heading of a README, or a fallback."""
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#\s+(.*\S)\s*$", line)
        if match:
            return match.group(1)
    return fallback


def find_tasks(session_dir):
    """Every directory below a session that holds a README, depth-first."""
    tasks = []
    for readme in sorted(session_dir.rglob("README.md")):
        relative = readme.relative_to(session_dir).parent
        if relative == Path("."):
            continue
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        tasks.append(
            {
                "slug": relative.as_posix(),
                "path": readme.parent,
                "readme": readme,
                "title": read_title(readme, prettify(relative.name)),
            }
        )
    return tasks


def find_sessions(repo_root=REPO_ROOT):
    """Every session directory in the repository, in name order."""
    sessions = []
    for entry in sorted(Path(repo_root).iterdir()):
        if not entry.is_dir() or not SESSION_PATTERN.match(entry.name):
            continue
        sessions.append(
            {
                "slug": entry.name,
                "path": entry,
                "label": prettify(entry.name),
                "tasks": find_tasks(entry),
            }
        )
    return sessions
