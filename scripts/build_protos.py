import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# PROTO_DIR = ROOT / "vendor/protos"
# OUT_DIR = ROOT / "src"

# OUT_DIR.mkdir(parents=True, exist_ok=True)

# protos = list((PROTO_DIR / "gogi").rglob("*.proto")) #list(PROTO_DIR.rglob("*.proto"))

# cmd = [
#     "python",
#     "-m",
#     "grpc_tools.protoc",
#     f"-I={PROTO_DIR}",              # IMPORTANT: root includes gogi/
#     f"--python_out={OUT_DIR}",
#     f"--grpc_python_out={OUT_DIR}",
# ]

PROTO_DIR = ROOT / "vendor/protos"
OUT_DIR = ROOT / "src"

OUT_DIR.mkdir(parents=True, exist_ok=True)

protos = list((PROTO_DIR / "gogi").rglob("*.proto"))

cmd = [
    "python",
    "-m",
    "grpc_tools.protoc",
    f"-I={PROTO_DIR}",
    f"--python_out={OUT_DIR}",
    f"--grpc_python_out={OUT_DIR}",
]

cmd.extend(str(p) for p in protos)

subprocess.run(cmd, check=True)

print("protobufs generated")

# ensure packages exist for imports
for path in [
    OUT_DIR / "gogi",
    OUT_DIR / "gogi" / "v1",
]:
    path.mkdir(parents=True, exist_ok=True)

# ensure __init__.py everywhere under gogi/
for path in (OUT_DIR / "gogi").rglob("*"):
    if path.is_dir():
        (path / "__init__.py").touch(exist_ok=True)