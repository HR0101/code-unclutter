---
schema_version: "3.0.0"
spec_type: "advanced_skill_suite_specification"
skill_name: "code-unclutter"
target_agents:
  - name: "claude-code"
    config_path: ".claude/skills/code-unclutter/SKILL.md"
  - name: "codex-cli"
    config_path: ".gemini/skills/code-unclutter/SKILL.md"
source_reference: "リファクタリング "
---

# `code-unclutter`: 高度リファクタリング・スキルスイート仕様書

本ドキュメントは、**Claude Code および Codex / Gemini CLI 向けの多機能・多粒度リファクタリングスキル `code-unclutter` の完全設計書**である。

単一のプロンプト定義にとどまらず、**「ファイル単位」「機能/モジュール単位」「Git差分/PR単位」「シンボル/関数単位」「大規模アーキテクチャ刷新（ミカド法）」**といった複雑な開発現場の要求に自律対応できるスクリプト群とプロトコルを備えている。

---

## 1. スキルスイートの全体アーキテクチャ

```
code-unclutter/
├── SKILL.md                          # エージェント向け統合オーケストレーター
├── scripts/                          # 自動診断・安全検証・追跡CLIスクリプト
│   ├── unclutter                     # 統合CLIエントリーポイント (実行ランナー)
│   ├── scanner.py                    # 検出・メトリクス測定 (AST/Regex)
│   ├── safety_guard.py               # テスト自動実行・アトミックコミット・自動ロールバック
│   └── mikado.py                     # ミカド法 (No.98) 依存関係ツリー管理
├── references/                       # エージェントがオンデマンド参照する構造化データ
│   ├── catalog_100.json              # 全100項目の完全定義 (ID, Phase, Risk, Recipe)
│   └── workflows.md                  # 粒度別 (ファイル/機能/差分/シンボル) 実行プロトコル
└── templates/                        # 仕様化テスト・ゴールデンマスター生成用雛形
```

---

## 2. 粒度別の対応スコープ (Granular Target Scopes)

エージェントはユーザーのプロンプトの指示内容から対象スコープを自律判定し、適切なワークフローを選択する。

| スコープ | 指定フラグ / 発動プロンプト例 | 実行プロトコル | 重点項目|
| :--- | :--- | :--- | :--- |
| **単一ファイル** | `--file <path>`<br>「このファイルを綺麗にして」 | 対象ファイルのみにスコープを限定。P1クイックウィンを適用後、30行超の関数を抽出。 | 04, 05, 08, 26, 51, 71 |
| **機能・モジュール** | `--feature <dir>`<br>「決済モジュール全体を整理して」 | モジュールのPublic API境界を固定。依存されるヘルパーから順にボトムアップで整理。 | 06, 09, 10, 30, 33, 79, 83 |
| **Git差分 (PR前)** | `--diff`<br>「コミット前の差分だけ整えて」 | `git diff` 変更行の周辺（±20行）に限定。余計なファイルは一切触らない（ボーイスカウト原則）。 | 84, 86, 87, 91, 97 |
| **特定シンボル** | `--symbol <name>`<br>「`calcTax` 関数だけネストを解消して」 | 単一関数・メソッドのみを外科的リファクタリング。ガード節化、純粋関数化、単体テスト追加。 | 51, 58, 62, 94 |
| **アーキテクチャ刷新** | `--mode architect`<br>「神クラスを解体したい」 | ミカド法（No.98）ツリーを作成し、前提条件を小ステップで解消しながら段階的にDI導入。 | 12, 16, 54, 93, 96, 98 |

---

## 3. 4段階フェーズ制御 (Safety Lifecycle)

エージェントは以下のフェーズゲートを遵守し、テストの裏付けがないまま上位フェーズへ進んではならない。

```
[Phase 0: Safety & Baseline] ──> [Phase 1: Quick-Wins] ──> [Phase 2: Logic Pure] ──> [Phase 3: Architecture]
   - テストスイート存在確認            - デッドコード削除 (08)    - 関数の抽出 (01, 26)     - 巨大クラス分割 (06, 30)
   - 仕様化テスト (76, 99)            - マジックナンバー定数化 (05) - CQS分離 (35)           - 依存性注入 / DI (93)
   - 型注釈の先行付与 (91)            - ガード節でネスト解消 (51)  - 純粋関数・イミュータブル (94, 95) - ミカド法依存解消 (98)
   - リンター/フォーマット (86, 87)    - 例外握りつぶし解消 (71)   - ループ分離 / パイプライン (55, 59) - 段階的移行 (96)
```

---

## 4. 組み込みツールとCLIインターフェース

### ① 静的解析・臭いスキャナー (`scripts/scanner.py`)
Python標準ライブラリのみで動作し、主要な臭いをAST/正規表現で自動検出する。
```bash
# ファイル単体スキャン
python3 scripts/scanner.py src/auth.ts

# Git差分のみスキャン
python3 scripts/scanner.py --diff

# 特定関数のみスキャン
python3 scripts/scanner.py src/calc.py --symbol calculateTax

# 機械可読JSON出力
python3 scripts/scanner.py src/ --json
```

### ② 安全ガード＆自動ロールバック (`scripts/safety_guard.py`)
テストフレームワーク（pytest, jest, cargo test, go test, make test）を自動検出し、テスト成否に応じてアトミックコミットまたは自動ロールバックを行う。
```bash
# テスト実行・成功時のみコミット（失敗時は git checkout で即復旧）
python3 scripts/safety_guard.py verify --files src/auth.ts --message "refactor(P1): apply guard clauses"
```

### ③ ミカド法・依存関係追跡 (`scripts/mikado.py`)
大規模リファクタリング時のゴールと前提条件のツリー管理を行う。
```bash
# ゴール設定
python3 scripts/mikado.py goal "Decompose UserManager into Auth and Profile services"

# 前提タスクの追加
python3 scripts/mikado.py add root "Extract PasswordHasher into separate utility"

# 進捗ステータス確認
python3 scripts/mikado.py status
```

---

## 5. 現代のモダン開発標準オーバーライド（禁止規則）

現代の言語仕様・コンパイラ・静的解析の観点から盲目的な適用を禁じる項目：

1. **ヨーダ記法（No. 75: `0 == x`）の全面禁止**:
   - 現代の静的解析（ESLint, Ruff, Clang）は代入ミスを100%自動検知するため、可読性を下げるヨーダ記法は使用せず、`x === 0` の自然な順序を強制する。
2. **早すぎるDRY（No. 80）の禁止（Rule of Three）**:
   - 出現回数が3回未満のコードは安易に共通化しない（間違った抽象化は偶発的な重複よりも害が大きい）。
3. **ネストした三項演算子（No. 63）の禁止**:
   - `a ? b : c ? d : e` のようなネストは禁止。ガード節またはルックアップテーブル（No. 60）に変換する。

---

## 6. スキル配信用スクリプト

プロジェクトルートから以下を実行することで、全スクリプト・リファレンスを含めて Claude Code および Codex に即時同期できる。

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Sync to Claude Code
mkdir -p .claude/skills/code-unclutter
cp -r scripts references .claude/skills/code-unclutter/

# 2. Sync to Codex / Gemini CLI
mkdir -p "$HOME/.gemini/skills/code-unclutter"
cp -r scripts references "$HOME/.gemini/skills/code-unclutter/"

echo "[OK] code-unclutter skill suite fully deployed to Claude and Codex!"
```
