import subprocess
from pathlib import Path

PROTO_DIR = Path("vendor/protos/proto")
OUT_DIR = Path("src")

subprocess.run([
    "python",
    "-m",
    "grpc_tools.protoc",
    f"-I={PROTO_DIR}",
    f"--python_out={OUT_DIR}",
    f"--grpc_python_out={OUT_DIR}",
    str(PROTO_DIR / "genai/v1/chat.proto"),
], check=True)