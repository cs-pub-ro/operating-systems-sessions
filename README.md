# Operating Systems

Temporary repository to store contents for the Operating Systems class.
Each session has its own directory, comprising items both for lectures and for labs.

[`LEARNER.md`](LEARNER.md) is the guide for students: how a session is put together, how to work through a task, and what is expected of them.

## Website

The contents of this repository are published as a website, built with MkDocs from the `README.md` files stored here.
The generator lives in the `scripts/` directory, see [`scripts/README.md`](scripts/README.md) for details.

### Building the website locally

The site needs Python 3 and the packages listed in [`requirements.txt`](requirements.txt).
Install them into a virtual environment, so nothing lands in the system Python:

```console
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Debian and Ubuntu, `python3 -m venv` needs the `python3-venv` package.

With the environment active, serve the site and open <http://localhost:8000>:

```console
mkdocs serve
```

Every page is generated from the `README.md` files at build time, so editing one and saving it rebuilds the page and reloads the browser.
Adding a session or a task means creating the directory and writing its `README.md`; nothing has to be registered anywhere.

To build the site instead of serving it, into the git-ignored `_site/` directory:

```console
mkdocs build
```

This is the command the `.github/workflows/pages.yml` workflow runs to publish the site on every push to `master`.
Add `--strict` to it to turn warnings, such as a link that points nowhere, into a failed build.
Leave the environment with `deactivate`; on later sessions, `source .venv/bin/activate` is enough.

## Prerequisites

Every session README lists the tools that session needs.
[`scripts/check-prerequisites.sh`](scripts/check-prerequisites.sh) checks a machine against those lists and prints the command that installs whatever is missing:

```console
./scripts/check-prerequisites.sh          # every session
```

It installs nothing and changes nothing, and exits non-zero when something needed is missing.
See the *Prerequisites check* section of [`scripts/README.md`](scripts/README.md) for what it checks and how to extend it.

## Lab archives

Each session is packed into a zip archive of its exercises, without the reference solutions, and published on the `lab-archives` branch.
The `.github/workflows/lab-archive.yml` workflow rebuilds them on every push to `master` that touches a session.
Build them locally with `python3 scripts/gen_zip.py`; see [`scripts/README.md`](scripts/README.md) for what goes in and how to create the branch the first time.

## Linting

The `.github/workflows/lint.yml` workflow checks style on every push and every pull request.

* Markdown is checked with [markdownlint](https://github.com/DavidAnson/markdownlint-cli2), configured in `.markdownlint-cli2.jsonc` to follow [`content-rules.md`](content-rules.md).
* Shell scripts are checked with [ShellCheck](https://www.shellcheck.net/).
* C sources are checked with the Linux kernel's `checkpatch.pl`.
  Only the lines a push or a pull request changes have to be clean.
  The findings for the rest of the tree are listed in the run summary, to be worked through a session at a time.

To run the first two locally:

```console
npx markdownlint-cli2 "**/*.md"
git ls-files -z '*.sh' | xargs -0 shellcheck
```

`markdownlint-cli2 --fix <file>` repairs what can be repaired automatically.
