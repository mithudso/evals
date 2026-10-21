"""trigger_runner embedding path: model pinned, [] on failure, cosine semantics preserved."""
import json
import math
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


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

