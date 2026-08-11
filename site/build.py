#!/usr/bin/env python3
"""Build the static GitHub Pages site for the Operating Systems sessions.

The site mirrors the repository layout:

    /                                      front page, lists every session
    /session-01-software-stack/            lists every task in that session
    /session-01-software-stack/01-.../     renders that task's README.md

READMEs are used exactly as they are stored in the repository: no front
matter, no extra metadata files.  Everything the site needs is derived from
the directory tree at build time.

Usage:

    python3 site/build.py [--output _site]
"""

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = Path(__file__).resolve().parent

SITE_TITLE = "Operating Systems"
SITE_TAGLINE = "Session materials for the Operating Systems class"

# Directory names that never become pages, at any depth.
EXCLUDED_DIRS = {".git", ".github", "site", "solutions"}

# Top-level directories that are treated as sessions.
SESSION_PATTERN = re.compile(r"^session-\d+")

MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "sane_lists", "attr_list", "md_in_html"]

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


def render_markdown(text):
    """Render a Markdown document to HTML."""
    converter = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS)
    return converter.convert(text)


def render_inline(text):
    """Render a short Markdown snippet without the wrapping paragraph."""
    rendered = render_markdown(text).strip()
    if rendered.startswith("<p>") and rendered.endswith("</p>"):
        rendered = rendered[3:-4]
    return rendered


def read_title(readme_path, fallback):
    """Return the first level-one heading of a README, or a fallback."""
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#\s+(.*\S)\s*$", line)
        if match:
            return match.group(1)
    return fallback


def prettify(name):
    """Turn a directory name such as `01-string-functions` into a label."""
    without_prefix = re.sub(r"^(?:session-\d+|\d+|bonus|demo)[-_]", "", name)
    words = re.split(r"[-_]+", without_prefix.strip())
    return " ".join(ACRONYMS.get(word.lower(), word.title()) for word in words if word)


def rewrite_links(html_text):
    """Point in-repository README links at their generated pages."""
    return re.sub(r'href="([^":]*?)README\.md(#[^"]*)?"', r'href="\1\2"', html_text)


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
                "readme": readme,
                "title": read_title(readme, prettify(relative.name)),
            }
        )
    return tasks


def find_sessions(repo_root):
    """Every session directory in the repository, in name order."""
    sessions = []
    for entry in sorted(repo_root.iterdir()):
        if not entry.is_dir() or not SESSION_PATTERN.match(entry.name):
            continue
        sessions.append(
            {
                "slug": entry.name,
                "label": prettify(entry.name),
                "tasks": find_tasks(entry),
            }
        )
    return sessions


def page(title, depth, breadcrumbs, body):
    """Wrap page content in the shared HTML skeleton."""
    root = "../" * depth or "./"
    crumbs = ""
    if breadcrumbs:
        links = " / ".join(
            f'<a href="{href}">{html.escape(text)}</a>' if href else html.escape(text)
            for text, href in breadcrumbs
        )
        crumbs = f'<nav class="breadcrumbs">{links}</nav>\n'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<main>
{crumbs}{body}
</main>
</body>
</html>
"""


def toc(entries):
    """Render a list of links as the shared table of contents markup."""
    items = []
    for name, href, description in entries:
        description_html = f'<span class="toc-note">{description}</span>' if description else ""
        items.append(
            f'<li><a href="{href}"><code>{html.escape(name)}</code>'
            f"{description_html}</a></li>"
        )
    return '<ul class="toc">\n' + "\n".join(items) + "\n</ul>"


def build_front_page(sessions, output_dir):
    # The lead of the repository README -- everything before its first `##`
    # section -- doubles as the introduction of the front page.
    intro = ""
    root_readme = REPO_ROOT / "README.md"
    if root_readme.exists():
        text = root_readme.read_text(encoding="utf-8")
        text = re.sub(r"^#\s+.*\n", "", text, count=1)
        text = re.split(r"^##\s", text, maxsplit=1, flags=re.MULTILINE)[0]
        intro = render_markdown(text.strip())

    entries = [
        (
            session["slug"],
            f"{session['slug']}/",
            f"{html.escape(session['label'])} &middot; "
            f"{len(session['tasks'])} task{'s' if len(session['tasks']) != 1 else ''}",
        )
        for session in sessions
    ]

    body = (
        f"<h1>{html.escape(SITE_TITLE)}</h1>\n"
        f'<p class="tagline">{html.escape(SITE_TAGLINE)}</p>\n'
        f"{intro}\n"
        f"<h2>Sessions</h2>\n{toc(entries)}"
    )
    (output_dir / "index.html").write_text(
        page(SITE_TITLE, 0, [], body), encoding="utf-8"
    )


def build_session_page(session, output_dir):
    entries = [
        (task["slug"], f"{task['slug']}/", render_inline(task["title"]))
        for task in session["tasks"]
    ]
    body = (
        f"<h1><code>{html.escape(session['slug'])}</code></h1>\n"
        f'<p class="tagline">{html.escape(session["label"])}</p>\n'
        f"<h2>Tasks</h2>\n{toc(entries)}"
    )
    breadcrumbs = [(SITE_TITLE, "../"), (session["slug"], None)]
    target = output_dir / session["slug"]
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(
        page(f"{session['slug']} — {SITE_TITLE}", 1, breadcrumbs, body),
        encoding="utf-8",
    )


def build_task_page(session, task, output_dir):
    depth = 1 + len(Path(task["slug"]).parts)
    up = "../" * (depth - 1)
    breadcrumbs = [
        (SITE_TITLE, "../" * depth),
        (session["slug"], up),
        (task["slug"], None),
    ]
    body = rewrite_links(
        render_markdown(task["readme"].read_text(encoding="utf-8"))
    )
    target = output_dir / session["slug"] / task["slug"]
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(
        page(f"{task['slug']} — {session['slug']}", depth, breadcrumbs, body),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=REPO_ROOT / "_site",
        type=Path,
        help="directory to write the generated site into (default: _site)",
    )
    args = parser.parse_args()

    output_dir = args.output.resolve()
    if output_dir == REPO_ROOT:
        sys.exit("refusing to write the site into the repository root")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    sessions = find_sessions(REPO_ROOT)
    if not sessions:
        sys.exit("no session directories found")

    build_front_page(sessions, output_dir)
    task_count = 0
    for session in sessions:
        build_session_page(session, output_dir)
        for task in session["tasks"]:
            build_task_page(session, task, output_dir)
            task_count += 1

    shutil.copy(SITE_DIR / "style.css", output_dir / "style.css")

    print(f"built {len(sessions)} sessions and {task_count} tasks into {output_dir}")


if __name__ == "__main__":
    main()
