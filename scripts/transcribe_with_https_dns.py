"""Opt-in, process-local fallback when system DNS cannot resolve the Gemini API.

Run like the forestcensus CLI. Normal DNS is always tried first. Only the Gemini
API hostname can fall back to Google's HTTPS DNS; TLS verification stays enabled.
"""

import json
import socket
import time
import urllib.request

from forestcensus.cli import main


def run() -> None:
    original = socket.getaddrinfo
    cached = []
    expires = 0.0

    def resolve(host, port, *args, **kwargs):
        nonlocal cached, expires
        try:
            return original(host, port, *args, **kwargs)
        except socket.gaierror:
            if host not in ("generativelanguage.googleapis.com", b"generativelanguage.googleapis.com"):
                raise
            if time.monotonic() >= expires:
                url = "https://dns.google/resolve?name=generativelanguage.googleapis.com&type=A"
                with urllib.request.urlopen(url, timeout=15) as response:
                    answers = json.load(response)
                cached = [a["data"] for a in answers.get("Answer", []) if a["type"] == 1]
                if not cached:
                    raise RuntimeError("Google HTTPS DNS returned no API addresses")
                expires = time.monotonic() + 240
            return [entry for address in cached for entry in original(address, port, *args, **kwargs)]

    socket.getaddrinfo = resolve
    try:
        main()
    finally:
        socket.getaddrinfo = original


if __name__ == "__main__":
    run()
