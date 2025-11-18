from typing import Any

import pytest
from django.core.management import call_command

from cadastral import tasks

def test_run_full_ingest_task_invokes_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the run_full_ingest task invokes the pipeline.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object.
    """
    called_kwargs = {}

    def fake_run_pipeline(**kwargs: Any) -> None:
        """
        Fake run_pipeline function.
        """
        called_kwargs.update(kwargs)

    monkeypatch.setattr(tasks, "run_pipeline", fake_run_pipeline)
    tasks.run_full_ingest.__wrapped__()  # type: ignore[attr-defined]
    assert called_kwargs == {}

def test_run_pipeline_calls_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the run_pipeline task calls the steps.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object.
    """
    sequence: list[str] = []

    def fake_download() -> None:
        """
        Fake download function.
        """
        sequence.append("download")

    def fake_refresh() -> None:
        """
        Fake refresh function.
        """
        sequence.append("refresh")

    def fake_publish() -> None:
        """
        Fake publish function.
        """
        sequence.append("publish")

    monkeypatch.setattr(tasks, "download_and_extract_sources", fake_download)
    monkeypatch.setattr(tasks, "apply_database_refresh", fake_refresh)
    monkeypatch.setattr(tasks, "publish_layers", fake_publish)

    tasks.run_pipeline()
    assert sequence == ["download", "refresh", "publish"]


def test_run_pipeline_respects_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the run_pipeline task respects the flags.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object.
    """
    sequence = []

    def fake_download():
        sequence.append("download")

    def fake_refresh():
        sequence.append("refresh")

    def fake_publish():
        sequence.append("publish")

    monkeypatch.setattr(tasks, "download_and_extract_sources", fake_download)
    monkeypatch.setattr(tasks, "apply_database_refresh", fake_refresh)
    monkeypatch.setattr(tasks, "publish_layers", fake_publish)

    tasks.run_pipeline(perform_downloads=False, publish_to_geoserver=False)
    assert sequence == ["refresh"]

def test_publish_layers_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the publish_layers command calls the publish_layers function.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object.
    """
    called = {"publish": False}

    def fake_publish() -> None:
        """
        Fake publish function.
        """
        called["publish"] = True

    monkeypatch.setattr(
        "cadastral.management.commands.publish_layers.publish_layers",
        fake_publish,
    )
    call_command("publish_layers")
    assert called["publish"] is True

def test_run_ingest_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the run_ingest command calls the run_pipeline function.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch object.
    """
    recorded_kwargs = {}

    def fake_run_pipeline(**kwargs: Any) -> None:
        """
        Fake run_pipeline function.
        """
        recorded_kwargs.update(kwargs)

    monkeypatch.setattr("cadastral.tasks.run_pipeline", fake_run_pipeline)
    call_command("run_ingest", "--skip-download")
    assert recorded_kwargs == {
        "perform_downloads": False,
        "publish_to_geoserver": True,
    }
