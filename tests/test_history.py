from binary_cli.core import history
from binary_cli.providers.base import Message


def test_history_save_and_retrieve(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "data_directory", lambda: tmp_path)

    msg1 = Message(role="user", content="What is binary?")
    msg2 = Message(role="assistant", content="Binary is base 2.")

    history.save_message("conv-1", msg1)
    history.save_message("conv-1", msg2)

    rows = history.recent_messages(limit=10)
    assert len(rows) == 2
    assert rows[0][0] == "conv-1"
    assert rows[0][1] == "user"
    assert rows[0][2] == "What is binary?"
    assert rows[1][1] == "assistant"
    assert rows[1][2] == "Binary is base 2."


def test_history_clear(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "data_directory", lambda: tmp_path)

    history.save_message("conv-1", Message(role="user", content="Hello"))
    assert len(history.recent_messages()) == 1

    deleted = history.clear_history()
    assert deleted == 1
    assert len(history.recent_messages()) == 0
