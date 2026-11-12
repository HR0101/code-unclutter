# code-unclutter

多粒度対応 自律型リファクタリング・スキルスイート  
> 対応エージェント: Codex CLI / Claude Code / Gemini CLI / Antigravity

---

## 概要

`code-unclutter` は、「既存の振る舞いを1ミリも変えずに、コードの散らかり（Clutter）を安全に解消する」ためのプロフェッショナル向けリファクタリングエンジンです。

マーチン・ファウラーのリファクタリング原則に基づき、「ファイル単位」「機能モジュール単位」「コミット前のGit差分単位」「特定関数単位」「アーキテクチャ刷新単位」という5つの粒度で安全にコードを改善します。

### AIリファクタリングの「3大事故」を防止する安全機構
1. **仕様破壊の防止**: 外部から観測可能な振る舞い（APIシグネチャ、I/O、戻り値、例外条件）を100%保持。
2. **テスト破壊の防止**: 変更後に自動テストを実行し、1件でも失敗すれば `git checkout` で即座に自動ロールバック。
3. **過剰設計の防止**: 現代の観点で有害・不要とされるヨーダ記法（No.75: `0 == x`）、過度なDRY（No.80）、ネスト三項演算子を厳格に禁止。

---

## インストール方法 (Installation)

環境に合わせて以下のいずれかのディレクトリに配置するだけで、各エージェントが自動認識します。

### 方法1：一括配備スクリプト

リポジトリ直下で以下を実行すると、Codex・Claude・Geminiの全環境へ一括配備されます：

```bash
# リポジトリ直下で実行
./install.sh
```

### 方法2：エージェント別手動配置

#### [1] Codex CLI の場合
```bash
mkdir -p ~/.codex/skills/code-unclutter
cp -r SKILL.md scripts references ~/.codex/skills/code-unclutter/
```

#### [2] Claude Code の場合（グローバルまたはプロジェクト個別）
```bash
# グローバル環境（どのディレクトリからでも利用可能）
mkdir -p ~/.claude/skills/code-unclutter
cp -r SKILL.md scripts references ~/.claude/skills/code-unclutter/

# プロジェクト個別（カレントリポジトリ内のみで利用）
mkdir -p .claude/skills/code-unclutter
cp -r SKILL.md scripts references .claude/skills/code-unclutter/
```

#### [3] Gemini CLI / Antigravity の場合
```bash
mkdir -p ~/.gemini/skills/code-unclutter
cp -r SKILL.md scripts references ~/.gemini/skills/code-unclutter/
```

---

## エージェントへの指示の出し方 (Prompting Guide)

Codex や Claude Code に対し、日常会話の自然言語で指示を出すだけで、エージェントが対象スコープと最適なフェーズを自動判別します。

### シナリオ別指示プロンプト集

#### 1. 単一ファイルを綺麗にしたいとき（File Scope）
- **指示例**:
  - 「`src/services/order.ts` を綺麗にして」
  - 「`order_service.py` を code-unclutter でリファクタリングして」
- **実行動作**: 対象ファイルにスコープを限定。Phase 1（デッドコード・マジックナンバー・ガード節）を適用し、30行を超える肥大関数を分割。

#### 2. 機能・モジュール全体を整理したいとき（Feature Scope）
- **指示例**:
  - 「`src/payment/` の決済モジュール全体を整理して」
  - 「認証機能（`src/auth/`）の設計を改善して」
- **実行動作**: モジュールの外部公開インターフェース（Public API）を保護しながら、内部のヘルパーやユーティリティからボトムアップに整理。

#### 3. PR作成前・コミット前に差分だけ整えたいとき（Boy Scout Rule）
- **指示例**:
  - 「コミット前の差分だけ整えて」
  - 「いま変更したところだけ綺麗にして（ボーイスカウトルールで）」
  - 「PR出す前にコードを軽く掃除して」
- **実行動作**: `git diff` で変更された行の周辺（±20行）のみに限定して改善。触っていない無関係なファイルには一切触れない。

#### 4. 特定の関数だけネストを解消したいとき（Symbol Scope）
- **指示例**:
  - 「`calculateTax` 関数だけネストを浅くして」
  - 「この関数の多重ifをガード節で平坦化して」
- **実行動作**: 指定された関数のみを外科的に修正。周囲のコードは一切触らず、単体テストを追加して完了。

#### 5. コードの臭いや複雑度を調査したいとき（Diagnose / Dry-Run）
- **指示例**:
  - 「このリポジトリのコードの臭いをスキャンして」
  - 「`src/` 配下の認知的複雑度を診断して、まず直すべき箇所をリストアップして」
- **実行動作**: コードは一切変更せず、内蔵スキャナー（`scripts/scanner.py`）を実行して優先度付きの診断レポートを出力。

#### 6. 巨大クラス・神クラスを解体したいとき（Architecture / Mikado Method）
- **指示例**:
  - 「`UserManager` クラスをミカド法で段階的に解体したい」
  - 「グローバル変数を依存性の注入（DI）に置き換えて」
- **実行動作**: ミカド法（No.98）のゴール・依存ツリーを作成し、前提条件を小ステップで解消しながら安全にクラスを分割。

---

## CLIスクリプト単体での使い方 (Direct CLI)

スキルとしてエージェント経由で呼び出すだけでなく、開発者がターミナルから直接スクリプトを実行することも可能です。

### 統合ランナー (`scripts/unclutter`)
```bash
# ファイル単体のクイックウィン実行
./scripts/unclutter --file src/auth.ts --mode quick-win

# 機能モジュールの診断スキャン
./scripts/unclutter --feature src/billing/ --mode scan

# Git差分（PR前）のボーイスカウトスキャン
./scripts/unclutter --diff

# 特定関数の診断
./scripts/unclutter --file src/tax.py --symbol calculateTax
```

### 自律AST臭いスキャナー (`scripts/scanner.py`)
Python標準ライブラリのみで動作し、検出します：
```bash
python3 scripts/scanner.py src/
# JSON形式で出力
python3 scripts/scanner.py src/ --json
```

### 安全ガード＆自動ロールバック (`scripts/safety_guard.py`)
テストフレームワーク（pytest, jest, cargo test, go test等）を自動判定して実行：
```bash
# テスト実行・成功時のみコミット（失敗時は自動で git checkout ロールバック）
python3 scripts/safety_guard.py verify --files src/auth.ts --message "refactor: apply guard clauses"
```

### ミカド法・依存ツリー管理 (`scripts/mikado.py`)
```bash
# ゴール設定
python3 scripts/mikado.py goal "Decompose God Class UserManager"

# 前提タスク追加
python3 scripts/mikado.py add root "Extract PasswordHasher utility"

# ツリー確認
python3 scripts/mikado.py status
```

---

## 4段階フェーズと安全優先順位

リファクタリングは必ず以下のフェーズ順序を遵守します。

```
[Phase 0: Safety & Baseline] ──> [Phase 1: Quick-Wins] ──> [Phase 2: Logic Pure] ──> [Phase 3: Architecture]
   - テストスイート検出              - デッドコード削除 (08)    - 関数の抽出 (01, 26)     - 巨大クラス分割 (06, 30)
   - 仕様化テスト (76, 99)            - マジックナンバー定数化 (05) - CQS分離 (35)           - 依存性注入 / DI (93)
   - 型注釈の付与 (91)                - ガード節でネスト解消 (51)  - 純粋関数・イミュータブル (94, 95) - ミカド法依存解消 (98)
   - リンター/フォーマット (86, 87)    - 例外握りつぶし解消 (71)   - ループ分離 / パイプライン (55, 59) - 段階的移行 (96)
```

| Phase | フェーズ名 | リスク | 主な内容 |
| :---: | :--- | :---: | :--- |
| **P0** | **Safety & Baseline** | ゼロ | 既存テスト確認、仕様化テスト先行作成、型注釈付与、自動フォーマット |
| **P1** | **Quick-Wins（まず直す）** | 極小 | デッドコード削除、マジックナンバー定数化、ガード節導入、空catch解消 |
| **P2** | **Logic Purification** | 低〜中 | 30行超関数の抽出、問い合わせと更新の分離 (CQS)、純粋関数化 |
| **P3** | **Architecture & Migration** | 中〜高 | 巨大クラス解体、DI導入、ミカド法による段階的移行 |

---

## 現代基準の禁止ルール (Modern Guardrails)

本スキルでは、AIが勝手に行いがちな以下の悪手を禁止しています：

- [禁止] **ヨーダ記法 (`0 == x`)**: 現代のコンパイラ・リンター環境では可読性を下げるだけのアンチパターン。自然順序（`x === 0`）を強制。
- [禁止] **早すぎるDRY（Rule of Three）**: 出現回数が3回未満のコードは安易に共通化しない（間違った抽象化は重複より害が大きい）。
- [禁止] **ネストした三項演算子**: `a ? b : c ? d : e` は禁止。ガード節またはルックアップテーブルに変換。
- [禁止] **パブリックAPIの勝手な破壊**: 外部公開関数のシグネチャを予告なく変更しない。

---

## 同梱リファレンス一覧 (References)

| ファイル名 | 内容 |
| :--- | :--- |
| [catalog_100.json](references/catalog_100.json) | 全100項目の完全定義辞書 |
| [workflows.md](references/workflows.md) | ファイル/機能/差分/シンボル/移行の粒度別実行手順書 |
| [recipes-quickwins.md](references/recipes-quickwins.md) | Phase 1（まず直す）の言語別Before/After実例集 |
| [recipes-purify.md](references/recipes-purify.md) | Phase 2（ロジック純化）のBefore/After実例集 |
| [anti-patterns.md](references/anti-patterns.md) | AIがやりがちなリファクタリング悪手集と禁止事項 |
| [language-guides.md](references/language-guides.md) | TypeScript, Python, Go, Java の言語別イディオム指針 |
| [output-templates.md](references/output-templates.md) | 診断レポート・計画書・完了サマリーの標準出力テンプレート |

---

## ライセンス (License)

MIT License.  
