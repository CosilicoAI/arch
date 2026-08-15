# Contributing

Use short-lived branches off `main` and open a pull request back to `main`.
Keep PRs focused, describe the checks you ran, and wait for CI before merging.

## Push branches to this repository, not a fork

Organization members already have write access here (the org default
permission is `write`), so there is no reason to fork. Do not open PRs from a
fork: the `test` job reads the ingest-signature public key from the
organization Actions variable `AXIOM_CORPUS_INGEST_PUBLIC_KEY`, and
`pull_request` runs whose head lives in a fork do not receive it. Two
authentication-gate tests in `tests/test_state_snap_manual_queue.py` then
fail on purpose (`AXIOM_CORPUS_INGEST_PUBLIC_KEY is required in CI`) and drag
coverage under the threshold. That failure is by design and cannot be fixed by
re-running the job or granting permissions. If a fork PR is already open, a
maintainer mirrors its head SHA to a same-repo branch and re-opens the PR from
there (precedent: #600 → #606); do not weaken the tests or embed key material.

## Pull request flow

1. Create a branch from an up-to-date `main` in this repository (not a fork).
2. Make the smallest coherent change and include tests for behavior changes.
3. Add a Towncrier fragment under `changelog.d/` unless the PR is docs,
   tests-only, or otherwise has no user-visible release note.
4. Open the PR to `main` and complete the PR template.
5. Merge after review approval and green CI.

Towncrier fragment categories are `breaking`, `added`, `changed`, `fixed`, and
`removed`. Name fragments descriptively, for example
`changelog.d/historical-versioning.fixed.md`.

## Local checks

CI runs the changelog draft, Ruff, mypy, tests with coverage, and a PostgreSQL
smoke check. Run the relevant subset locally before opening the PR:

```bash
uv sync --extra dev
uv pip install pytest-cov pytest-timeout
uv run towncrier build --draft --version 0.0.0
uv run ruff check .
uv run mypy src/axiom_corpus/corpus --ignore-missing-imports
uv run pytest -v --cov=axiom_corpus --cov-report=term-missing --cov-config=pyproject.toml --timeout=60
```

## Repo notes

- Generated `data/` and `sources/` files are local artifacts; do not commit them
  unless the PR explicitly adds a fixture or catalog source.
- Integration tests and live-source fetches should be isolated from the default
  offline test path.
- Keep storage, fetcher, and API changes covered by focused tests because they
  affect downstream encode and app workflows.
