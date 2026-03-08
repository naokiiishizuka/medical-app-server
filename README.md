# medical-app-server

本リポジトリは、DDD（Domain-Driven Design）とクリーンアーキテクチャの原則で構築された Python 製 Web API サーバーの雛形です。ディレクトリ構成のみを用意しているため、アーキテクチャ境界を崩さずに機能を追加できます。

```
src/
├── application/         # アプリケーション層（ユースケース）
│   ├── main/            # 本番コード
│   │   ├── dto/         # 入出力 DTO
│   │   ├── interfaces/  # 外部層とのポート
│   │   └── use_cases/   # ユースケース実装
│   └── test/            # レイヤ固有テスト
├── domain/              # ドメイン層
│   ├── main/
│   │   ├── entities/
│   │   ├── events/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── value_objects/
│   └── test/
├── infrastructure/      # インフラ層（DB, メッセージングなど）
│   ├── main/
│   │   ├── db/
│   │   ├── http/
│   │   ├── messaging/
│   │   └── repositories/
│   └── test/
├── presentation/        # プレゼンテーション層（Web API）
│   ├── main/
│   │   ├── api/
│   │   ├── controllers/
│   │   ├── dependencies/
│   │   └── generated/   # OpenAPI から生成されたコード
│   └── test/
├── openapi/             # API 契約
│   └── openapi.yaml
├── shared/              # 横断関心事（設定・ユーティリティ）
│   ├── main/
│   │   ├── config/
│   │   └── utils/
│   └── test/
└── main.py              # エントリーポイント
```

> 各レイヤに新しいモジュールを追加する際は、1 つ下位のレイヤにのみ依存してください（presentation → application → domain）。インフラ層はアプリケーション層のポート実装を提供します。レイヤ固有テストは `src/<layer>/test`、クロスレイヤ・E2E テストは `tests/` を使用します。

## OpenAPI との連携

1. API 契約は `src/openapi/openapi.yaml` を正とします。
2. `./scripts/generate_presentation.sh` を実行すると、OpenAPI に基づいたモデルを再生成します。ローカルに `openapi-generator-cli` があればそれを使い、無ければ Docker (`openapitools/openapi-generator-cli`) にフォールバックします。Docker イメージは `DOCKER_IMAGE` で上書き可能です。
3. スクリプトは既存の生成物を削除した後、`--global-property models` でモデルのみを生成し、`src/presentation/main/generated/src/models/` に配置します（`GENERATED_PACKAGE` で変更可）。テストコードはデフォルトで削除されます（`STRIP_TESTS=true`）。必要に応じ `GLOBAL_PROPERTIES` を書き換えて `apis` などを追加し、生成コードを `src/presentation/main/api` へ取り込みます。

## ローカル開発手順

1. `.env.example` を `.env` にコピーし、少なくとも `DATABASE_URL` を環境に合わせて設定します（未設定だと起動に失敗します）。
2. 仮想環境を用意（例: `python -m venv .venv && source .venv/bin/activate`）。
3. 依存をインストール: `pip install -e .[dev]`
4. PostgreSQL を起動します。手軽なのは `docker compose up db -d` で `docker-compose.yml` の DB コンテナを立ち上げる方法です。
5. マイグレーション適用: `./scripts/migrate.sh`（内部で `alembic upgrade head` + `.env` 読み込みを実行）。
6. 必要に応じてシード: `./scripts/seed.sh default`（本番/共通初期データ）、`./scripts/seed.sh test`（テスト向けデータ）。
7. API 起動: `uvicorn src.main:create_app --factory --host 0.0.0.0 --port 8000 --reload`
8. Swagger UI: `http://localhost:8000/docs`

`APP_HOST` / `APP_PORT` / `DATABASE_URL` など環境依存の設定は `.env` にまとめ、FastAPI と Docker Compose が共通で参照します。

Lint: `ruff check .`（自動整形は `ruff format .`）

## データベース & マイグレーション

- デフォルト接続文字列: `postgresql+asyncpg://postgres:postgres@localhost:5432/medical_app`（`DATABASE_URL` で上書き可）
- マイグレーション適用: `./scripts/migrate.sh` もしくは `alembic upgrade head`
- マイグレーション作成: `alembic revision -m "add patients table"`
- Docker 内で実行する場合: `docker compose run --rm api alembic upgrade head`（`.env` は自動で読み込まれます）

## シードデータ

- テンプレ生成: `python scripts/create_seeder.py <target> <name>` を実行すると `src/infrastructure/main/db/seeders/<target>/<name>.py` が作成されます。`target` は `default`（本番共通）または `test`（テスト/ローカル）を想定。テンプレ内の `run(session)` に処理を実装してください。
- 実行: `./scripts/seed.sh <target>`（例: `default`, `test`）。該当ディレクトリ内の `.py` がファイル名順に実行されます。
- Docker で実行する場合は `docker compose run --rm api ./scripts/seed.sh default` のように API コンテナ上で呼び出してください。

## Docker

本番と近い環境で動かすには Docker Compose を利用します。事前に `.env` を用意し（`.env.example` をコピー）、Compose から読み込ませます。その後 FastAPI と Postgres を同時に起動します。

```bash
docker compose up --build
```

ホストの 8000 番ポートがコンテナにマッピングされます。手動でビルド・実行する場合は次の通りです。

```bash
docker build -t medical-app-server .
docker run --rm -p 8000:8000 medical-app-server
```
