#!/bin/sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_FILE="${SPEC_FILE:-$ROOT_DIR/src/openapi/openapi.yaml}"
OUTPUT_DIR="$ROOT_DIR/src/presentation/main/generated"
export OUTPUT_DIR
GENERATOR="${GENERATOR:-python-fastapi}"
DOCKER_IMAGE="${DOCKER_IMAGE:-openapitools/openapi-generator-cli:v7.6.0}"
GLOBAL_PROPERTIES="${GLOBAL_PROPERTIES:-models}"
GENERATED_PACKAGE="${GENERATED_PACKAGE:-presentation_api}"
STRIP_TESTS="${STRIP_TESTS:-true}"

if command -v openapi-generator-cli >/dev/null 2>&1; then
  RUNNER="native"
elif command -v docker >/dev/null 2>&1; then
  RUNNER="docker"
else
  echo "Neither openapi-generator-cli nor docker is available. Install one of them to continue." >&2
  exit 1
fi

if [ -d "$OUTPUT_DIR" ]; then
  echo "Removing existing generated artifacts under $OUTPUT_DIR"
  rm -rf "$OUTPUT_DIR"
fi
mkdir -p "$OUTPUT_DIR"

if [ "$RUNNER" = "native" ]; then
  openapi-generator-cli generate \
    -i "$SPEC_FILE" \
    -g "$GENERATOR" \
    -o "$OUTPUT_DIR" \
    --additional-properties=packageName="$GENERATED_PACKAGE" \
    --global-property="$GLOBAL_PROPERTIES"
else
  case "$SPEC_FILE" in
    "$ROOT_DIR"/*) SPEC_IN_CONTAINER="/local${SPEC_FILE#$ROOT_DIR}" ;;
    *) echo "SPEC_FILE must be inside the repository when using docker." >&2; exit 1 ;;
  esac
  case "$OUTPUT_DIR" in
    "$ROOT_DIR"/*) OUTPUT_IN_CONTAINER="/local${OUTPUT_DIR#$ROOT_DIR}" ;;
    *) echo "OUTPUT_DIR must be inside the repository when using docker." >&2; exit 1 ;;
  esac
  docker run --rm \
    -v "$ROOT_DIR":/local \
    "$DOCKER_IMAGE" generate \
    -i "$SPEC_IN_CONTAINER" \
    -g "$GENERATOR" \
    -o "$OUTPUT_IN_CONTAINER" \
    --additional-properties=packageName="$GENERATED_PACKAGE" \
    --global-property="$GLOBAL_PROPERTIES"
fi

# Flatten package output residing under src/
PACKAGE_SRC_DIR="$OUTPUT_DIR/src/$GENERATED_PACKAGE"
if [ -d "$PACKAGE_SRC_DIR" ]; then
  echo "Flattening generated package structure inside src/"
  mkdir -p "$OUTPUT_DIR/src"
  cp -R "$PACKAGE_SRC_DIR"/. "$OUTPUT_DIR/src"/
  rm -rf "$PACKAGE_SRC_DIR"
fi

if [ "$STRIP_TESTS" = "true" ]; then
  for BASE in "$OUTPUT_DIR" "$OUTPUT_DIR/src"; do
    for TEST_DIR in test tests; do
      TARGET="$BASE/$TEST_DIR"
      if [ -d "$TARGET" ]; then
        echo "Removing generated tests from $TARGET"
        rm -rf "$TARGET"
      fi
    done
  done
fi

python3 <<'PY'
import os
from pathlib import Path

base = Path(os.environ["OUTPUT_DIR"])
src_dir = base / "src"
models_dir = src_dir / "models"
models_dir.mkdir(parents=True, exist_ok=True)

model_files = sorted(
    p.stem for p in models_dir.glob("*.py") if p.suffix == ".py" and p.name != "__init__.py"
)

def to_class_name(stem: str) -> str:
    return "".join(part.capitalize() for part in stem.split("_") if part)

generated_path = base / "__init__.py"
src_init_path = src_dir / "__init__.py"
models_init_path = models_dir / "__init__.py"

if model_files:
    class_names = [to_class_name(name) for name in model_files]
    import_lines = ", ".join(class_names)
    all_list = ", ".join(f'"{name}"' for name in class_names)
    generated_path.write_text(
        "\"\"\"Auto-generated models from OpenAPI specifications.\"\"\"\n\n"
        f"from .src.models import {import_lines}\n\n"
        f"__all__ = [{all_list}]\n",
        encoding="utf-8",
    )
    body = "\n".join(
        f"from .{module} import {cls}" for module, cls in zip(model_files, class_names)
    )
    models_init_path.write_text(
        "\"\"\"Exports for generated models.\"\"\"\n\n"
        f"{body}\n"
        f"__all__ = [{all_list}]\n",
        encoding="utf-8",
    )
else:
    generated_path.write_text(
        "\"\"\"Auto-generated models from OpenAPI specifications.\"\"\"\n\n"
        "__all__ = []\n",
        encoding="utf-8",
    )
    models_init_path.write_text(
        "\"\"\"Exports for generated models.\"\"\"\n\n__all__ = []\n", encoding="utf-8"
    )

src_init_path.write_text("\"\"\"Generated source package.\"\"\"\n", encoding="utf-8")
PY

echo "Generated presentation interface under $OUTPUT_DIR"
