# Website

The repository is published as a static website through GitHub Pages.
The site is built with [MkDocs](https://www.mkdocs.org/) and the [Material](https://squidfunk.github.io/mkdocs-material/) theme, and deployed by the `.github/workflows/pages.yml` workflow on every push to `master`.

## Structure

The site mirrors the repository layout, in three levels:

1. the front page lists every session directory, such as `session-01-software-stack`
1. a session page lists every task in that session, such as `01-string-functions`
1. a task page renders that task's `README.md`

## Contents

There are no pages stored in this repository.
`gen_pages.py` discovers everything at build time, by walking the directory tree, and hands the pages to MkDocs through the `mkdocs-gen-files` plugin.
The navigation sidebar is generated the same way, as a `SUMMARY.md` read back by the `mkdocs-literate-nav` plugin.

* A session is any top-level directory whose name starts with `session-` followed by a number.
* A task is any directory below a session that contains a `README.md` file.
  Nested tasks, such as `demo-copy-file/malloc`, are listed with their path relative to the session.
* Directories named `solutions` are skipped, together with `.git`, `.github`, `docs`, `scripts` and `site`.
  The list is the `EXCLUDED_DIRS` set in `gen_pages.py`.
* The title shown next to a task is the first level-one heading of its `README.md`.
  If the file has no heading, the directory name is used instead, and the heading is added to the page.
* Links between READMEs, such as `../demo-puts-write`, are rewritten to point at the generated pages.
  Links to files that have no page of their own, such as `copy_file.c`, are sent to the file on GitHub.

Adding a new session or a new task requires no change here: create the directory, write its `README.md` and push.
The `README.md` files need no front matter and no other metadata.

The `docs/` directory only exists because MkDocs insists on one; every page is generated.

## Building locally

Install the dependencies, then build the site into `_site/`:

```console
pip install -r requirements.txt
mkdocs build
```

Better, while writing: serve the site at <http://localhost:8000> and rebuild on every change.

```console
mkdocs serve
```

## Enabling GitHub Pages

The workflow deploys the site, but the repository has to allow it first.
In the repository settings, under *Pages*, set *Source* to *GitHub Actions*.
The site is then published at `https://<owner>.github.io/<repository>/`.
