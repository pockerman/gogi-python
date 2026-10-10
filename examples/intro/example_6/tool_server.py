"""A small HTTP service that plays a clinic's scheduling and billing systems for example_6.py.

The Gogi tools service calls the tools registered in example_6.py here: it POSTs each call's
arguments as JSON to the tool's endpoint and returns the JSON response as the result.

- POST /availability: the free slots of a clinic on a date
- POST /bookings: books a slot. It requires the API key the platform injects from the
  credential store, as ``Authorization: Bearer <key>``
- POST /coverage: verifies insurance coverage; slow, to show asynchronous execution

Run it with:

    python examples/intro/example_6/tool_server.py

It listens on port 8765 (GOGI_EXAMPLE_TOOL_SERVER_PORT) and expects the API key
``example-api-key`` (GOGI_EXAMPLE_TOOL_API_KEY).
"""

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("GOGI_EXAMPLE_TOOL_SERVER_PORT", "8765"))
API_KEY = os.environ.get("GOGI_EXAMPLE_TOOL_API_KEY", "example-api-key")


def availability(arguments: dict) -> dict:
    return {
        "clinic_id": arguments["clinic_id"],
        "date": arguments["date"],
        "slots": [f"{arguments['date']}T09:00", f"{arguments['date']}T11:30", f"{arguments['date']}T15:00"],
    }


def book(arguments: dict) -> dict:
    booking_id = f"bk-{uuid.uuid4().hex[:8]}"
    return {"booking_id": booking_id, "patient_id": arguments["patient_id"], "slot": arguments["slot"]}


def coverage(arguments: dict) -> dict:
    # insurers are slow
    time.sleep(3)
    return {"patient_id": arguments["patient_id"], "procedure": arguments["procedure_code"], "covered_percent": 80}


class ToolHandler(BaseHTTPRequestHandler):
    routes = {"/availability": (availability, False), "/bookings": (book, True), "/coverage": (coverage, False)}

    def do_POST(self) -> None:  # noqa: N802 (the name is set by BaseHTTPRequestHandler)
        route = self.routes.get(self.path)
        if route is None:
            self.respond(404, {"error": "not found"})
            return

        tool, needs_key = route
        if needs_key and self.headers.get("Authorization") != f"Bearer {API_KEY}":
            self.respond(401, {"error": "invalid API key"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        arguments = json.loads(self.rfile.read(length) or b"{}")
        # the platform says which tool, version and session the call is for
        tool_name = f"{self.headers.get('X-Gogi-Tool')}@{self.headers.get('X-Gogi-Tool-Version')}"
        print(f"{tool_name} session={self.headers.get('X-Gogi-Session-Id', '-')} {arguments}", flush=True)
        self.respond(200, tool(arguments))

    def respond(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass


if __name__ == "__main__":
    print(f"Tool server listening on port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), ToolHandler).serve_forever()
