# Operating Systems

Temporary repository to store contents for the Operating Systems class.
Each session has its own directory, comprising items both for lectures and for labs.

## Website

The contents of this repository are published as a website, built with MkDocs from the `README.md` files stored here.
The generator lives in the `scripts/` directory, see [`scripts/README.md`](scripts/README.md) for details.

## Lab archives

Each session is packed into a zip archive of its tasks, without the reference solutions, and published on the `lab-archives` branch.
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
