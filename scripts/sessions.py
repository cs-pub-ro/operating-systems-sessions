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
# session 05 challenges.  `utils` holds support code vendored into a task -- the
# mpaland/printf library under `bonus-printf/utils/` -- which is packed with its
# task but is not a task of its own, so it gets no page and no navigation entry.
EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".claude",
    ".venv",
    "_site",
    "archives",
    "docs",
    "node_modules",
    "scripts",
    "site",
    "solutions",
    "utils",
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

# The `Session NN:` lead-in of a session README title, which the name built
# from that title carries as its index instead.
SESSION_TITLE_PREFIX = re.compile(r"^session\s*\d+\s*[:.-]?\s*", re.IGNORECASE)

# An article opening a title: dropped, so that "The Software Stack" becomes
# `software-stack` rather than `the-software-stack`.
LEADING_ARTICLE = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)


def prettify(name):
    """Turn a directory name such as `01-string-functions` into a label."""
    without_prefix = re.sub(r"^(?:session-\d+|\d+|bonus|demo)[-_]", "", name)
    # Session directories carry a `-work` / `-full-contents` suffix that is
    # plumbing, not part of the label.
    without_prefix = re.sub(r"[-_](?:work|full-contents)$", "", without_prefix)
    words = re.split(r"[-_]+", without_prefix.strip())
    return " ".join(ACRONYMS.get(word.lower(), word.title()) for word in words if word)


def slugify(text):
    """Turn a title such as `Memory Operations` into `memory-operations`."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_title(readme_path, fallback):
    """Return the first level-one heading of a README, or a fallback."""
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#\s+(.*\S)\s*$", line)
        if match:
            return match.group(1)
    return fallback


def session_title(session_dir):
    """The title of a session, from its README, without the `Session NN:` lead.

    `01-software-stack-work/README.md` opens with `# Session 01: The Software
    Stack`, so the title is `The Software Stack`.  A session without a README,
    or one whose README has no heading, falls back to its directory name.
    """
    fallback = prettify(session_dir.name)
    readme = session_dir / "README.md"
    if not readme.is_file():
        return fallback
    title = SESSION_TITLE_PREFIX.sub("", read_title(readme, fallback))
    return title.strip() or fallback


def session_name(session_dir):
    """The name a session is shown under on the website.

    The directory name is plumbing -- `01-software-stack-work` says `-work` to
    students for no reason -- and the README title alone would lose the order
    the sessions are taken in.  The name is therefore the index of the session
    followed by its title, as a slug: `01-software-stack`, `03-memory-operations`.
    """
    title = LEADING_ARTICLE.sub("", session_title(session_dir))
    slug = slugify(title) or slugify(session_dir.name)
    index = re.search(r"\d+", session_dir.name)
    return f"{index.group(0)}-{slug}" if index else slug


def session_heading(session_dir):
    """The heading a session is shown under, `01: The Software Stack`.

    The title of the session README, which is what a reader sees at the top of
    the session page, led by the index of the session so that the order the
    sessions are taken in survives.  The `Session` of `Session 01:` is dropped:
    every entry of the navigation is a session, so the word says nothing.
    """
    title = session_title(session_dir)
    index = re.search(r"\d+", session_dir.name)
    return f"{index.group(0)}: {title}" if index else title


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
                "name": session_name(entry),
                "label": session_title(entry),
                "heading": session_heading(entry),
                "tasks": find_tasks(entry),
            }
        )
    return sessions
