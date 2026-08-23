# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Teaching material for an Operating Systems class (2nd year, 1st semester, 4-year technical bachelor programme), 12 lab sessions of 100 minutes each; the first 5 are here.
The practical part is C on Linux, aimed at the lower layers of the software stack: the C library, system calls, memory, linking, debugging.
There is no application to build — the deliverables are exercise directories (source + `Makefile` + `README.md`) and the website and lab archives generated from them.

AI use is discouraged *for students during the lab*; the point is that they write and build the programs by hand.
Content written here has to leave them something to do.

## Session layout

Each session lives in two sibling top-level directories:

* `NN-<session-name>-work/` — what students get during the live session: skeletons with `TODO` markers, task descriptions, hints. Never a complete solution.
* `NN-<session-name>-full-contents/` — reference solutions, full explanations, reference command output, and the `prompt.txt` notes the exercises were generated from. Used by students after the session and by assistants before it.

Inside a session, the directory-name prefix is the task type, and it is load-bearing (the site and the archives key off it, and so do the README conventions below):

* `demo-<name>/` — solved together with the teaching assistant at the start of the session.
* `NN-<name>/` — core exercise, solved individually or in teams, in numeric order.
* `bonus-<name>/` — optional; for students who finish early, or as homework.

Every task directory is freestanding: no symlinks, no shared Makefile fragments, so it survives being unzipped on its own.
Per-exercise `.gitignore` lists only the binaries that task builds — object files and the like are already covered by the top-level `.gitignore`.

Per task, up to four Markdown files, with a strict division of labour:

| File | `-work/` | `-full-contents/` |
| --- | --- | --- |
| `README.md` | the task | the tutorial |
| `FURTHER.md` | optional extensions, questions, discussion points | same, with answers |
| `INSTRUCTOR.md` | never | notes for whoever runs the session |
| `prompt.txt` | never | the note the exercise was written from (excluded from student archives) |

## README conventions

Session-level `README.md` (both directories): learning objectives, prerequisites and required tools, and a task-order table (order, task, type, objective).

Exercise `README.md` in `-work/`:

```text
# <Exercise|Bonus>: <Title>

**Tools:** GCC, GDB, Valgrind

## Goal            (1-3 sentences: what you will be able to do afterwards)
## Background      (only what is needed; link out for more)
## Your Task       (numbered, checkable)
## Build & Run
## Check Your Work
```

Demo `README.md` in `-work/` is deliberately minimal: a short paragraph on the aim, and a note that the work is done together with the teaching assistant on the files in the directory.

Exercise `README.md` in `-full-contents/` is a tutorial: Goal, Background, Build & Run, Results and Explanations, Going Further, References.
Sections may be dropped where they do not apply.

Rules that are easy to violate, all of them deliberate:

* Keep a `-work/` exercise README under ~80 lines. Reading time is time not spent working. Go over only when it earns it.
* **No expected output** in *Check Your Work*. Describe what the output should look like and what to reason about, so students interpret it and take it to the teaching assistant instead of pattern-matching.
* **No *Going Further* section** in a `-work/` README — that content belongs in `FURTHER.md`.
* **Do not link to `FURTHER.md`** from a `-work/` README either; students should not feel obliged to open it.
* **No time budgets** anywhere in student-facing files, and no "After the session" section. Groups and assistants move at different paces. Time estimates and pacing advice go in `INSTRUCTOR.md`.
* Anything addressed to the teaching assistant — pacing, which demo to pick, what students get wrong — goes in `INSTRUCTOR.md`, not in a `README.md`.

## Markdown style

`content-rules.md` is the source of truth and `.markdownlint-cli2.jsonc` enforces most of it. The two that a linter cannot catch and that matter most:

* **One sentence per line.** A four-sentence paragraph is four lines, each starting at column zero (indented to match, inside a list item). This keeps diffs readable.
* Shell commands use ```` ```console ````, not ```` ```bash ````; `bash` is only for actual shell scripts. Every fenced block gets a language; use `text` when nothing fits.

Also: `*` for unordered lists, `1.` for *every* ordered item, blank line around lists and fences, no trailing whitespace.

## Commands

```console
npx --yes markdownlint-cli2@0.23.2 "**/*.md"    # add --fix <file> to repair one file
git ls-files -z '*.sh' '*.bash' | xargs -0 shellcheck
```

Never pass `--fix` without naming files: the config deliberately has no `globs` key, but a bare glob would rewrite the whole tree.

Building an exercise is `make` inside its directory; most also have `make test`, `make bench`, `make run` or similar — read the `Makefile`, they differ per task.

Site and archives:

```console
pip install -r requirements.txt
mkdocs serve                      # http://localhost:8000, rebuilds on change
mkdocs build                      # into _site/
python3 scripts/gen_zip.py        # student archives into archives/ (git-ignored)
```

C style is the Linux kernel's `checkpatch.pl`, fetched by `.github/workflows/lint.yml`; only lines a push or PR changes must be clean, the rest of the tree is reported in the run summary.

## Generation pipeline

`scripts/sessions.py` defines what a session is and what a task is; `gen_pages.py` (website, via `mkdocs-gen-files` + `mkdocs-literate-nav`) and `gen_zip.py` (student archives, published to the `lab-archives` branch) both ask it, so the two can never disagree.
Nothing is stored: pages and navigation are discovered by walking the tree at build time, so adding a session or task means creating the directory and writing its `README.md`, nothing else.
`gen_zip.py` packs only git-tracked files and drops `prompt.txt` / `*-prompt.txt`, so a stray `.o` or a solution note never reaches students.
See `scripts/README.md` for the details.

## State of the migration

The repository is mid-restructure, from the old `session-NN-<name>/` + `solutions/` layout to the `-work/` + `-full-contents/` pair described above.
`restructure-sessions.txt`, `restructure-sessions-2.txt` and `extra-prompt-restructure.md` are the specifications for it, and they are the authority when this file is ambiguous.

* Sessions 01, 02, 03 — migrated; use `01-software-stack-*` as the model for everything.
* Session 04 (`04-memory-debugging-*`) — migrated; `-full-contents/` has full `FURTHER.md`/`INSTRUCTOR.md`, the session README has no time column, and `prompt.txt` files live in their task dirs.
* Session 05 (`05-memory-security-*`) — migrated. This is a CTF session: `-work/` holds the public challenge files (`chall.c`, `chall`, task README), and `-full-contents/<task>/` holds the write-up plus the whole `build`/`publish`/`deploy`/`solve` Docker pipeline, the `flag`, and the reference `exploit.py`.

Two consequences worth knowing before touching the tooling — the first is now a safety issue, not just cosmetics:

* `SESSION_PATTERN` in `scripts/sessions.py` is `^session-\d+`, so the renamed directories are invisible to it — the website and the lab archives now see *no* session at all, since the last `session-*` directory (session 05) has been renamed away.
  When you fix this, student archives must pack from `*-work/` only and exclude every `*-full-contents/`.
  This is now a safety issue: `05-memory-security-full-contents/` contains session 05's **flags and exploits**, and `gen_zip.py` only name-excludes directories literally called `solutions`, which no longer exist anywhere in the tree.
  A naive `SESSION_PATTERN` widening would ship the flags to students — see `05-memory-security-full-contents/INSTRUCTOR.md`.
* The `VENDORED` path in `.github/workflows/lint.yml` still points at `session-02-os-interface/printf`; the vendored printf now lives at `02-os-interface-work/bonus-printf/printf`.

## Third-party content

`02-os-interface-work/bonus-printf/printf/` is imported as-is and is not ours to reformat; it is excluded from markdownlint and (once the path is fixed) from checkpatch.
The rule, from `questions.md`: small files students are expected to read and modify get reformatted to our style; large files they only use, and anything tracking an upstream that is periodically re-synced, stay as they are.
