#!/usr/bin/env python3
"""Generate the MkDocs pages for the Operating Systems sessions.

The plugin `mkdocs-gen-files` runs this script on every `mkdocs build` and on
every reload of `mkdocs serve`.  Pages are written into the virtual docs tree,
so nothing appears on disk and the repository stays as it is.

The site mirrors the repository layout, in three levels:

    index.md                                 front page, lists every session
    session-01-software-stack/index.md       lists every task in that session
    session-01-software-stack/01-.../index.md  that task's README.md

READMEs are used exactly as they are stored in the repository: no front
matter, no extra metadata files.  Everything the site needs is derived from
the directory tree at build time.
"""

import re
import sys
from pathlib import Path

import mkdocs_gen_files
from mkdocs.structure.files import InclusionLevel

# The plugin runs this script from the repository root, so the directory it
# lives in is not on the path yet.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sessions import (  # noqa: E402  (the path has to be set up first)
    EXCLUDED_DIRS,
    REPO_ROOT,
    SESSION_PATTERN,
    find_sessions,
)

SITE_TITLE = "Operating Systems"
SITE_TAGLINE = "Session materials for the Operating Systems class"

# The navigation tree, as the `nav_file` of the mkdocs-literate-nav plugin.
NAV_FILE = "SUMMARY.md"

# Where links to files that are not pages -- source code, headers, Makefiles --
# are sent instead.
REPO_BLOB_URL = "https://github.com/cs-pub-ro/operating-systems-sessions/blob/master"

# A Markdown link target: the `](target)` part, with an optional title.
LINK_PATTERN = re.compile(r"(?<=\]\()([^)\s]+)(?=(?:\s+\"[^\"]*\")?\))")

# A fenced code block, kept out of the link rewriting below.
FENCE_PATTERN = re.compile(r"(^```[\s\S]*?^```[^\n]*$)", re.MULTILINE)

# A URL scheme, a page anchor, or a site-absolute path: left alone.
EXTERNAL_PATTERN = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|#|/|<)", re.IGNORECASE)


def is_page(path):
    """Whether a directory of the repository is published as a task page."""
    if not path.is_dir() or not (path / "README.md").is_file():
        return False
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError:
        return False
    parts = relative.parts
    return bool(parts) and SESSION_PATTERN.match(parts[0]) and not (
        set(parts) & EXCLUDED_DIRS
    )


def rewrite_target(target, readme_dir):
    """Point one Markdown link at the page, or the file, it means.

    Links between READMEs are written the way the directory tree looks, such as
    `../demo-puts-write`.  On the site those directories are pages, generated as
    `index.md`, so the link has to name the file MkDocs knows about.  Links to
    anything else in the repository -- a `.c` file, a Makefile -- have no page,
    and are sent to GitHub instead.
    """
    if EXTERNAL_PATTERN.match(target):
        return target

    path_part, separator, fragment = target.partition("#")
    if not path_part:
        return target

    resolved = (readme_dir / path_part).resolve()
    if REPO_ROOT not in resolved.parents:
        return target

    if is_page(resolved):
        return f"{path_part.rstrip('/')}/index.md{separator}{fragment}"

    if resolved.name == "README.md" and is_page(resolved.parent):
        return f"{path_part[: -len('README.md')]}index.md{separator}{fragment}"

    if resolved.is_file():
        relative = resolved.relative_to(REPO_ROOT).as_posix()
        return f"{REPO_BLOB_URL}/{relative}{separator}{fragment}"

    return target


def rewrite_links(text, readme_dir):
    """Rewrite every Markdown link of a README, outside of code blocks."""
    parts = FENCE_PATTERN.split(text)
    return "".join(
        part
        if part.startswith("```")
        else LINK_PATTERN.sub(lambda m: rewrite_target(m.group(0), readme_dir), part)
        for part in parts
    )


def write(path, text):
    with mkdocs_gen_files.open(path, "w") as page:
        page.write(text)


def build_front_page(sessions):
    # The lead of the repository README -- everything before its first `##`
    # section -- doubles as the introduction of the front page.
    intro = ""
    root_readme = REPO_ROOT / "README.md"
    if root_readme.exists():
        text = root_readme.read_text(encoding="utf-8")
        text = re.sub(r"^#\s+.*\n", "", text, count=1)
        text = re.split(r"^##\s", text, maxsplit=1, flags=re.MULTILINE)[0]
        intro = rewrite_links(text.strip(), REPO_ROOT)

    lines = [f"# {SITE_TITLE}", "", SITE_TAGLINE, "", intro, "", "## Sessions", ""]
    for session in sessions:
        count = len(session["tasks"])
        lines.append(
            f"* [`{session['slug']}`]({session['slug']}/index.md)"
            f" — {session['label']}, {count} task{'' if count == 1 else 's'}"
        )
    write("index.md", "\n".join(lines) + "\n")


def build_session_page(session):
    lines = [
        f"# `{session['slug']}`",
        "",
        session["label"],
        "",
        "## Tasks",
        "",
    ]
    for task in session["tasks"]:
        lines.append(f"* [`{task['slug']}`]({task['slug']}/index.md) — {task['title']}")
    write(f"{session['slug']}/index.md", "\n".join(lines) + "\n")


def build_task_page(session, task):
    text = task["readme"].read_text(encoding="utf-8")
    body = rewrite_links(text, task["readme"].parent)
    # A README without a heading of its own still needs one on the page.
    if not re.search(r"^#\s+\S", text, re.MULTILINE):
        body = f"# {task['title']}\n\n{body}"
    write(f"{session['slug']}/{task['slug']}/index.md", body)


def build_nav(sessions):
    """The navigation tree, read back by the mkdocs-literate-nav plugin."""
    lines = [f"* [{SITE_TITLE}](index.md)"]
    for session in sessions:
        lines.append(f"* [{session['slug']}]({session['slug']}/index.md)")
        for task in session["tasks"]:
            lines.append(
                f"    * [{task['slug']}]({session['slug']}/{task['slug']}/index.md)"
            )
    write(NAV_FILE, "\n".join(lines) + "\n")

    # The navigation is read from this file, it is not a page of the site.
    files = mkdocs_gen_files.FilesEditor.current().files
    files.get_file_from_path(NAV_FILE).inclusion = InclusionLevel.EXCLUDED


def main():
    sessions = find_sessions()
    if not sessions:
        raise SystemExit("no session directories found")

    build_front_page(sessions)
    for session in sessions:
        build_session_page(session)
        for task in session["tasks"]:
            build_task_page(session, task)
    build_nav(sessions)


main()
