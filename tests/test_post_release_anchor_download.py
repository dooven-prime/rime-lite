"""Check the bounded Zenodo file-download fallback for release anchors."""

from __future__ import annotations

import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.release.post_release_anchor import zenodo_file_digest


RECORD = {"id": 24156272}
ITEM = {
    "key": "paper44_arxiv.pdf",
    "size": 7,
    "checksum": "md5:example",
    "links": {"content": "https://zenodo.org/api/records/24156272/files/paper44_arxiv.pdf/content"},
}
BUCKET = "620d78d4-4160-4b58-818b-58e0f6043b28"


def blocked_primary(_request: str | Request, *, timeout: int) -> BytesIO:
    raise HTTPError(ITEM["links"]["content"], 403, "blocked", None, None)


def test_bounded_fallback() -> None:
    payload = b"PDFdata"
    metadata = {"key": ITEM["key"], "size": len(payload),
                "checksum": ITEM["checksum"], "bucket_id": BUCKET}
    calls = []

    def fetch(request: str | Request, *, timeout: int) -> BytesIO:
        calls.append(request)
        if len(calls) == 1:
            return blocked_primary(request, timeout=timeout)
        if len(calls) == 2:
            assert request == "https://zenodo.org/api/records/24156272/files/paper44_arxiv.pdf"
            return BytesIO(json.dumps(metadata).encode())
        assert isinstance(request, Request)
        assert request.full_url == f"https://zenodo.org/api/files/{BUCKET}/paper44_arxiv.pdf"
        assert request.get_header("Range") == "bytes=0-6"
        return BytesIO(payload)

    with patch("tools.release.post_release_anchor.urlopen", side_effect=fetch):
        digest, size = zenodo_file_digest(RECORD, ITEM)
    assert (digest, size) == (hashlib.sha256(payload).hexdigest(), len(payload))
    assert len(calls) == 3


def test_rejects_mismatched_file_metadata() -> None:
    metadata = {"key": ITEM["key"], "size": ITEM["size"] + 1,
                "checksum": ITEM["checksum"], "bucket_id": BUCKET}

    def fetch(request: str | Request, *, timeout: int) -> BytesIO:
        if request == ITEM["links"]["content"]:
            return blocked_primary(request, timeout=timeout)
        return BytesIO(json.dumps(metadata).encode())

    with patch("tools.release.post_release_anchor.urlopen", side_effect=fetch):
        try:
            zenodo_file_digest(RECORD, ITEM)
        except ValueError as error:
            assert "metadata differs" in str(error)
        else:
            raise AssertionError("accepted mismatched Zenodo file metadata")


if __name__ == "__main__":
    test_bounded_fallback()
    test_rejects_mismatched_file_metadata()
    print("test_post_release_anchor_download.py: OK")
