from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _anchor_cwd_to_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests reference fixtures with repo-root-relative paths; anchor the CWD so the suite passes regardless of where pytest is invoked from."""
    monkeypatch.chdir(REPO_ROOT)
