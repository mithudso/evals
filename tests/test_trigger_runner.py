"""trigger_runner embedding path: model pinned, [] on failure, cosine semantics preserved."""

import json
import math
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
import trigger_runner as t

SEEN: list[dict] = []


class Fake(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append({"path": self.path, **body})
        if self.path == "/api/embed":
            inputs = body["input"] if isinstance(body["input"], list) else [body["input"]]
            out = {"embeddings": [[3.0, 4.0, float(len(x))] for x in inputs]}
        elif self.path == "/api/embeddings":
            out = {"embedding": [3.0, 4.0, float(len(body["prompt"]))]}
        else:
            self.send_error(404)
            return
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


@pytest.fixture()
def host():
    SEEN.clear()
    srv = HTTPServer(("127.0.0.1", 0), Fake)
    thread = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{srv.server_port}"
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join()


def test_default_model_is_pinned_qwen3(host):
    assert t.get_embedding("hello", host=host) == [3.0, 4.0, 5.0]
    assert SEEN[0]["model"] == "qwen3-embedding:4b"


def test_model_override_respected(host):
    t.get_embedding("hello", host=host, model="other")
    assert SEEN[0]["model"] == "other"


def test_unreachable_returns_empty_list_fast():
    assert t.get_embedding("x", host="http://127.0.0.1:1") == []


def test_cosine_semantics():
    assert t.cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert t.cosine_similarity([1, 0], [0, 1]) == 0.0
    assert t.cosine_similarity([], [1]) == 0.0
    assert t.cosine_similarity([1, 2], [1]) == 0.0
    assert t.cosine_similarity([0, 0], [1, 1]) == 0.0
    assert t.cosine_similarity([1, 1], [2, 2]) == pytest.approx(1.0)
    assert t.cosine_similarity([1, 2, 3], [4, 5, 6]) == pytest.approx(
        32 / (math.sqrt(14) * math.sqrt(77))
    )


@pytest.mark.parametrize("query_vector, expected", [([0.0, 1.0], 0.125), ([-1.0, 0.0], 0.0)])
def test_valid_nonpositive_cosine_keeps_hybrid_weights(monkeypatch, query_vector, expected):
    monkeypatch.setattr(t, "get_embedding", lambda text: query_vector)
    profile = {"token_bag": {"apple"}, "triggers": [], "skips": []}
    score, evidence = t.score_query_match("apple banana", profile, [1.0, 0.0])
    assert score == pytest.approx(expected)
    assert "mode=hybrid" in evidence


@pytest.mark.parametrize(
    "lexical_only, mode", [(True, "lexical-only"), (False, "lexical-fallback")]
)
def test_stopword_only_query_reports_the_selected_lexical_mode(lexical_only, mode):
    profile = {"token_bag": {"apple"}, "triggers": [], "skips": []}
    score, evidence = t.score_query_match("a the", profile, [1.0, 0.0], lexical_only=lexical_only)
    assert score == 0.0
    assert f"mode={mode}" in evidence


@pytest.mark.parametrize("vector", [[float("nan"), 1.0], [True, 1.0], [1.0]])
def test_incompatible_embeddings_use_explicit_lexical_fallback(monkeypatch, vector):
    monkeypatch.setattr(t, "get_embedding", lambda text: vector)
    profile = {"token_bag": {"apple"}, "triggers": [], "skips": []}
    score, evidence = t.score_query_match("apple banana", profile, [1.0, 0.0])
    assert score == pytest.approx(0.3)
    assert "mode=lexical" in evidence


@pytest.mark.parametrize(
    "data",
    [
        [],
        [{"query": "apple", "should_trigger": True}],
        [{"query": "apple", "should_trigger": True}, {"query": "", "should_trigger": False}],
        [
            {"query": "apple", "should_trigger": True},
            {"query": "banana", "should_trigger": "false"},
        ],
        {"query": "apple", "should_trigger": True},
    ],
)
def test_invalid_trigger_suites_are_rejected_before_embedding(tmp_path, monkeypatch, data):
    suite = tmp_path / "trigger.json"
    suite.write_text(json.dumps(data))
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: fruit\ndescription: 'TRIGGER: apple. SKIP: banana.'\n---\n")
    calls = []
    monkeypatch.setattr(t, "get_embedding", lambda text: calls.append(text) or [])
    with pytest.raises(ValueError):
        t.evaluate_triggers(str(suite), str(skill))
    assert calls == []


def test_oversized_integer_threshold_is_a_validation_error(tmp_path):
    suite = tmp_path / "trigger.json"
    suite.write_text("[]")
    with pytest.raises(ValueError, match="Threshold"):
        t.evaluate_triggers(str(suite), threshold=10**400, lexical_only=True)


@pytest.mark.parametrize(
    "frontmatter",
    [
        "- hi",
        "name: [broken",
        "name: fruit\ndescription: 7",
        "name: fruit",
        "name: ''\ndescription: apple",
    ],
)
def test_invalid_skill_frontmatter_has_clear_validation_error(tmp_path, frontmatter):
    skill = tmp_path / "SKILL.md"
    skill.write_text(f"---\n{frontmatter}\n---\n")
    with pytest.raises(ValueError):
        t.extract_skill_profile(str(skill))


def test_lexical_only_evaluation_never_requests_embeddings(tmp_path, monkeypatch):
    suite = tmp_path / "trigger.json"
    suite.write_text(
        json.dumps(
            [
                {"query": "apple", "should_trigger": True},
                {"query": "unrelated", "should_trigger": False},
            ]
        )
    )
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: fruit\ndescription: 'TRIGGER: apple. SKIP: banana.'\n---\n")

    def forbidden_embedding(text):
        pytest.fail("lexical-only mode attempted embedding")

    monkeypatch.setattr(t, "get_embedding", forbidden_embedding)
    result = t.evaluate_triggers(str(suite), str(skill), lexical_only=True)
    assert result["verdict"] == "PASSED"
    assert result["scoring_mode"] == "lexical-only"


def test_embedding_fallback_warning_does_not_expose_input_or_error(monkeypatch, caplog):
    class BrokenClient:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("secret-credential")

    monkeypatch.setattr(t, "OllamaClient", BrokenClient)
    with caplog.at_level("WARNING"):
        assert t.get_embedding("private-input") == []
    assert "embedding" in caplog.text.lower()
    assert "private-input" not in caplog.text
    assert "secret-credential" not in caplog.text


def test_server_fixture_closes_listening_socket(monkeypatch):
    servers = []
    server_type = HTTPServer

    def capture_server(*args, **kwargs):
        server = server_type(*args, **kwargs)
        servers.append(server)
        return server

    monkeypatch.setattr(sys.modules[__name__], "HTTPServer", capture_server)
    fixture = host.__wrapped__()
    next(fixture)
    try:
        with pytest.raises(StopIteration):
            next(fixture)
        assert servers[0].socket.fileno() == -1
    finally:
        servers[0].server_close()


def test_lexical_cli_supports_offline_runs(tmp_path):
    suite = tmp_path / "trigger.json"
    suite.write_text(
        json.dumps(
            [
                {"query": "apple", "should_trigger": True},
                {"query": "unrelated", "should_trigger": False},
            ]
        )
    )
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: fruit\ndescription: 'TRIGGER: apple. SKIP: banana.'\n---\n")
    result = subprocess.run(
        [
            sys.executable,
            str(Path(t.__file__)),
            str(suite),
            "--skill-path",
            str(skill),
            "--lexical-only",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert "lexical-only" in result.stdout


def test_deeply_nested_trigger_json_is_a_clean_cli_error(tmp_path):
    path = tmp_path / "deep-trigger.json"
    path.write_text("[" * 2000 + '"private-marker"' + "]" * 2000)
    result = subprocess.run(
        [sys.executable, str(Path(t.__file__)), str(path), "--lexical-only"],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "Error:" in result.stderr
    assert "suite" in result.stderr.lower()
    assert "private-marker" not in result.stderr
    assert "Traceback" not in result.stderr
