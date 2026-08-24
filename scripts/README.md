# Scripts

Two things are generated from the repository tree, and both live here:

* `gen_pages.py` builds the [website](#website)
* `gen_zip.py` builds the [lab archives](#lab-archives) handed to students

Both ask `sessions.py` what a session is and what a task is, so the site and the archives can never disagree about it.

A third script, `check-prerequisites.sh`, generates nothing: it checks that the [tools a session needs](#prerequisites-check) are installed.

## Website

The repository is published as a static website through GitHub Pages.
The site is built with [MkDocs](https://www.mkdocs.org/) and the [Material](https://squidfunk.github.io/mkdocs-material/) theme, and deployed by the `.github/workflows/pages.yml` workflow on every push to `master`.

### Structure

The site mirrors the repository layout, in three levels:

1. the front page lists every session, such as `01-software-stack`
1. a session page renders that session's `README.md`: what the session is about, the learning outcomes, how to get the archive, the setup check, and the task table that lists its tasks
1. a task page renders that task's `README.md`

### Contents

There are no pages stored in this repository.
`gen_pages.py` discovers everything at build time, by walking the directory tree, and hands the pages to MkDocs through the `mkdocs-gen-files` plugin.
The navigation sidebar is generated the same way, as a `SUMMARY.md` read back by the `mkdocs-literate-nav` plugin.

* A session is a top-level `NN-<name>-work/` directory: the student-facing side of the lab.
  Its `NN-<name>-full-contents/` sibling holds the reference material — solutions, and for session 05 the challenge flags and exploits — and is deliberately not a session, so it is never published on the site and never packed into an archive. This is the successor to the old `solutions/` convention. The rule is `SESSION_PATTERN` in `sessions.py` (the legacy `session-NN-*` form is still recognised).
* A task is any directory below a session that contains a `README.md` file.
  Nested tasks, such as `demo-copy-file/malloc`, are listed with their path relative to the session.
* Directories named `solutions` are skipped, together with `.git`, `.github`, `docs`, `scripts` and `site`.
  The list is the `EXCLUDED_DIRS` set in `sessions.py`.
* The title shown next to a task is the first level-one heading of its `README.md`.
  If the file has no heading, the directory name is used instead, and the heading is added to the page.
* A session is shown under its index and the title of its `README.md`, not under its directory name: `01-software-stack-work/`, whose README opens with `# Session 01: The Software Stack`, is listed as `01-software-stack`.
  The index keeps the sessions in the order they are taken in, and the `-work` suffix is plumbing students never need to see.
  A session without a README, or with one that has no heading, falls back to its directory name.
  The rule is `session_name()` in `sessions.py`; the URL of a page is still the directory name.
* Links between READMEs, such as `../demo-puts-write`, are rewritten to point at the generated pages.
  Links to files that have no page of their own, such as `copy_file.c`, are sent to the file on GitHub.

Adding a new session or a new task requires no change to these scripts: create the directory, write its `README.md` and push.
The `README.md` files need no front matter and no other metadata.
A new task appears in the navigation sidebar automatically; to list it on the session page as well, add a row to that session's task table, which is the on-page list of tasks.

The `docs/` directory only exists because MkDocs insists on one; every page is generated.

### Building locally

Install the dependencies, then build the site into `_site/`:

```console
pip install -r requirements.txt
mkdocs build
```

Better, while writing: serve the site at <http://localhost:8000> and rebuild on every change.

```console
mkdocs serve
```

### Enabling GitHub Pages

The workflow deploys the site, but the repository has to allow it first.
In the repository settings, under *Pages*, set *Source* to *GitHub Actions*.
The site is then published at `https://<owner>.github.io/<repository>/`.

## Prerequisites check

`check-prerequisites.sh` checks a machine against the *Prerequisites and required tools* section of the session READMEs, and says what to install for whatever is missing.
Students run it before a session; it is also the quickest way to tell whether a lab machine has been set up.

```console
./scripts/check-prerequisites.sh          # every session
./scripts/check-prerequisites.sh -s 4     # only session 04
./scripts/check-prerequisites.sh -q       # only what is missing
```

The script only looks around, it installs nothing and changes nothing.
It exits 0 when everything the checked sessions need is there, and 1 otherwise, so it can also be used in a setup check on a lab machine.

* Tools needed only by a bonus task are reported apart, and do not fail the run.
* Three checks are not a plain lookup of a command: the machine is x86-64, where session 02 and session 05 need it; `gcc -static` links, which session 01 needs and which not every distribution installs by default; and pwntools imports in the `python3` that will run the session 05 exploits.
* The install command is written for the package manager the machine has, out of `apt-get`, `dnf`, `pacman` and `zypper`.
  The tool-to-package mapping is `package_for()`.

When a session's prerequisites change, the list to update is the `check_session_NN` function of that session, next to the README section it mirrors.

## Lab archives

Every session's `-work/` directory is packed into one zip archive of its tasks, published on the `lab-archives` branch, which holds nothing else.
The archives are what students download, so they contain the tasks and nothing more: the `NN-<name>-full-contents/` reference material — solutions, and the session 05 flags and exploits — is never packed.

The `.github/workflows/lab-archive.yml` workflow rebuilds and republishes them on every push to `master` that touches a session, and can also be run by hand from the *Actions* tab.

### Contents

An archive is named after the session with the `-work` suffix stripped, and unpacks into a single directory of that name:

```text
03-memory-ops.zip
└── 03-memory-ops/
    ├── 01-in-memory-db/
    ├── bonus-in-mem-database/
    └── demo-copy-file/{global-buffer,malloc,mmap}/
```

* A task is the same thing the website calls a task, decided by `sessions.py`: any directory below a session's `-work/` tree that has a `README.md`.
  A file shared by a task and a nested sub-task (such as the vendored `bonus-printf/printf/` tree) is packed exactly once.
* Only files tracked by git are packed, so an object file or a compiled binary left in the working tree is never shipped by accident.
  The archives are the same whether they are built from a clean checkout or from the tree you have been working in.
* Files named `prompt.txt`, the notes the exercises were written from, are left out; several of them describe the solution.
  The list is the `EXCLUDED_FILES` tuple in `gen_zip.py`.
* As a last line of defence, packing aborts outright if any file from a `-full-contents/` tree ever reaches an archive; `gen_zip.py`'s `is_reference()` is the guard.
* Archives are byte-for-byte reproducible: entries are sorted and timestamps are fixed.
  Editing one task therefore changes that one archive, and the workflow commits nothing at all when no content has changed.

### Building locally

```console
python3 scripts/gen_zip.py
```

The archives are written to `archives/`, which is ignored by git.
Nothing has to be installed: the script only needs Python and git.
Check what a student would get with:

```console
unzip -l archives/03-memory-ops.zip
```

### Creating the branch for the first time

The workflow creates the `lab-archives` branch itself, so the simplest way is to open the *Actions* tab, pick *Archive Labs on Commit* and run it on `master`.

To do the same by hand, build the archives and commit them onto a fresh orphan branch.
The commands below use a temporary worktree, so your own working tree is left alone:

```console
python3 scripts/gen_zip.py --output /tmp/lab-archives
git worktree add --detach /tmp/archives-branch
cd /tmp/archives-branch
git checkout --orphan lab-archives
git rm -rq --cached .
cp /tmp/lab-archives/*.zip .
git add -f *.zip
git commit -m "Add the initial lab archives"
git push -u origin lab-archives
```

Then go back and remove the temporary worktree:

```console
cd -
git worktree remove --force /tmp/archives-branch
```

The `-f` on `git add` is needed because the repository ignores `*.zip`, which on this branch is exactly what we want to commit.
From here on the workflow keeps the branch up to date on its own.

### Downloading an archive

A file on a branch is served by GitHub at a URL of this shape:

```text
https://github.com/<owner>/<repository>/raw/lab-archives/03-memory-ops.zip
```
