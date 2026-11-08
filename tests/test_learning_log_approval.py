"""第3回宿題: 保存ツールの承認・拒否を検証する。"""

import importlib
import sys

import pytest
from pydantic_ai import DeferredToolRequests, DeferredToolResults
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent


@pytest.fixture
def log_dir(tmp_path, monkeypatch):
    path = tmp_path / "learning_log"
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", path)
    return path


@pytest.mark.parametrize("approved", [False, True])
def test_deferred_approval(log_dir, approved):
    model = TestModel(call_tools=["save_learning_log"])
    first = agent.run_sync("学習記録を保存してください", model=model)

    assert isinstance(first.output, DeferredToolRequests)
    assert len(first.output.approvals) == 1
    assert not list(log_dir.glob("*.md"))

    call = first.output.approvals[0]
    assert call.tool_name == "save_learning_log"

    result = agent.run_sync(
        message_history=first.all_messages(),
        deferred_tool_results=DeferredToolResults(
            approvals={call.tool_call_id: approved}
        ),
        model=model,
    )

    assert not isinstance(result.output, DeferredToolRequests)
    files = list(log_dir.glob("*.md"))
    assert len(files) == int(approved)

    if approved:
        assert "# a" in files[0].read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "answer,expected",
    [("n", 0), ("y", 1)],
)
def test_cli_approval(log_dir, monkeypatch, capsys, answer, expected):
    module = importlib.import_module("app.agent")

    monkeypatch.setattr(
        module,
        "build_model",
        lambda: TestModel(call_tools=["save_learning_log"]),
    )
    monkeypatch.setattr(
        sys, "argv",
        ["app.agent", "学習記録を保存してください"],
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: answer,
    )

    module.main()

    output = capsys.readouterr().out
    assert "[承認待ち] save_learning_log" in output
    assert len(list(log_dir.glob("*.md"))) == expected
