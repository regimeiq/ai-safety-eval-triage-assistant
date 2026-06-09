from __future__ import annotations

from pathlib import Path

import pytest

import ai_safety_eval_triage.reports as reports
from scripts.run_demo import ROOT, main


def test_demo_artifacts_are_anchored_to_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    captured: dict[str, Path] = {}

    def _capture(run, docs_dir, out_dir, outputs_dir) -> None:
        captured["docs"] = Path(docs_dir)
        captured["out"] = Path(out_dir)
        captured["outputs"] = Path(outputs_dir)

    monkeypatch.setattr(reports, "write_reports", _capture)
    monkeypatch.chdir(tmp_path)  # simulate invoking the demo from an unrelated directory
    main()

    assert captured["docs"] == ROOT / "docs"
    assert captured["out"] == ROOT / "out"
    assert captured["outputs"] == ROOT / "outputs"
    assert not (tmp_path / "outputs").exists()
    assert "Generated demo artifacts" in capsys.readouterr().out
