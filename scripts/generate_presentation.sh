#!/bin/sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_FILE="${SPEC_FILE:-$ROOT_DIR/src/openapi/openapi.yaml}"
OUTPUT_DIR="$ROOT_DIR/src/presentation/main/generated"
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

echo "Generated presentation interface under $OUTPUT_DIR"
