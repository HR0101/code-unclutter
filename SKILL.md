---
name: code-unclutter
description: Autonomous multi-scope, safe refactoring engine based on the Standard Refactoring Catalog. Automatically detects and cleans code smells across files, modules, git diffs, or individual functions. Features priority gating (P0 Tests -> P1 Quick-Wins -> P2 Logic -> P3 Architecture), built-in AST smell scanning, automated regression testing, and instant rollbacks on test failure. Use when the user asks to refactor, clean up, unclutter, simplify, or improve code quality, readability, or structure.
license: MIT
metadata:
  framework: "Standard Refactoring Catalog"
  supported-languages: ["TypeScript", "JavaScript", "Python", "Go", "Rust", "Java", "PHP", "C#"]
  version: "3.2.0"
---

# Code Unclutter (高度自律リファクタリング・エンジン)

`code-unclutter` は、マーチン・ファウラーのリファクタリング原則を土台にした、**「既存の振る舞いを1ミリも壊さずに、コードの散らかり（clutter）を安全に解消する」ためのプロフェッショナル・リファクタリングスキル**である。

---

## 哲学とクラフトマンシップ（The Craft of Uncluttering）

AIによるリファクタリングが失敗する最大の原因は、**「頼まれてもいない過剰な設計（デザインパターン中毒）を導入し、勝手に仕様を変更し、テストを壊すこと」**である。

本スキルは以下の鉄則（Golden Rules）を絶対厳守する：

1. **振る舞いの絶対等価性（Strict Behavioral Equivalence）**:
   - 外部から観測可能な振る舞い（APIシグネチャ、戻り値、副作用、例外条件）は100%同一に保つ。
2. **優先度ゲート（Priority Gating）**:
   - 表層の低リスクな改善（Phase 1: デッドコード削除、命名、定数化、ガード節）を完了・検証する前に、巨大クラスの分割や設計刷新（Phase 3）に手を付けてはならない。
3. **安全網なき変更の禁止（Safety Gate）**:
   - テストが存在しないコードは、変更前に現行動作を固定する「仕様化テスト（ゴールデンマスター No.76/No.99）」を先行作成する。
4. **現代基準の徹底（Modern Standards Enforcement）**:
   - 時代遅れのヨーダ記法（No.75: `0 == x`）や、過度な早期共通化（No.80 DRYの乱用）はアンチパターンとして物理的に排除する。

---

## 1. ユーザー要求の解析とスコープ判定

ユーザーの入力文から、対象となるスコープと実行モードを即座に判定する。

| 対象スコープ | 典型的なプロンプト | 実行ワークフロー | 詳細リファレンス |
| :--- | :--- | :--- | :--- |
| **ファイル単位** | 「このファイルを綺麗にして」「`order.ts` をリファクタリングして」 | 対象ファイルのみにスコープを限定。P1クイックウィンを適用後、肥大関数の抽出。 | [references/workflows.md](references/workflows.md#1-ファイル単位ワークフロー) |
| **機能・モジュール単位** | 「決済機能全体を整理して」「`src/auth/` をリファクタリングして」 | パブリックAPI境界を固定。依存されるヘルパーからボトムアップに整理。 | [references/workflows.md](references/workflows.md#2-機能モジュール単位ワークフロー) |
| **Git差分（ボーイスカウト）** | 「コミット前の差分だけ整えて」「PR出す前に綺麗にして」 | `git diff` 変更行の周辺（±20行）に限定。無関係なファイルには一切触らない（No.84）。 | [references/workflows.md](references/workflows.md#3-git差分ボーイスカウトワークフロー) |
| **特定シンボル（関数・クラス）** | 「`calcTax` 関数だけネストを浅くして」「このメソッドを平坦化して」 | 単一関数のみを外科的リファクタリング。ガード節化、純粋関数化、単体テスト追加。 | [references/workflows.md](references/workflows.md#4-関数シンボル指定ワークフロー) |
| **アーキテクチャ刷新** | 「神クラスを解体したい」「DIを導入して疎結合にしたい」 | ミカド法（No.98）ツリーを作成し、前提条件を小ステップで解消しながら段階的にDI化。 | [references/workflows.md](references/workflows.md#5-アーキテクチャ刷新ミカド法ワークフロー) |

---

## 2. 4段階フェーズ制御（Execution Lifecycle）

リファクタリングは必ず以下のフェーズ順序を遵守し、後続フェーズへの飛び越し実行を行ってはならない。

```
[Phase 0: Safety & Baseline] ──> [Phase 1: Quick-Wins] ──> [Phase 2: Logic Pure] ──> [Phase 3: Architecture]
   - テストスイート検出              - デッドコード削除 (08)    - 関数の抽出 (01, 26)     - 巨大クラス分割 (06, 30)
   - 仕様化テスト (76, 99)            - マジックナンバー定数化 (05) - CQS分離 (35)           - 依存性注入 / DI (93)
   - 型注釈の付与 (91)                - ガード節でネスト解消 (51)  - 純粋関数・イミュータブル (94, 95) - ミカド法依存解消 (98)
   - リンター/フォーマット (86, 87)    - 例外握りつぶし解消 (71)   - ループ分離 / パイプライン (55, 59) - 段階的移行 (96)
```

---

## 3. 実践実行ステップ（Step-by-Step Execution Protocol）

### Step 1: 自動静的解析によるベースライン確立
まず同梱の自律スキャナーを実行し、対象コードの客観的な臭いと複雑度を測定する。
```bash
python3 scripts/scanner.py <target_path>
```
*※ 差分指定時は `--diff`、特定シンボル指定時は `--symbol <name>` を付与。*  
検出結果と照合するルール詳細は [references/catalog.json](references/catalog.json) を参照。

### Step 2: Phase 0 安全確認（Safety Gate）
1. 既存のテストスイート（pytest, jest, cargo test, go test等）が存在するか確認する。
2. **テストが存在しない場合**:
   - 変更に着手する前に、現状の入力と出力を記録する**「仕様化テスト（ゴールデンマスター No.76/No.99）」**を先行作成する。
3. リンター・フォーマッター（No.86, No.87）を実行し、空白やインデントの乱れを機械的に整える。
4. 静的型言語（TypeScript/Python等）の場合、引数と戻り値に型注釈（No.91）を付与する。

### Step 3: Phase 1 表層クイックウィンの適用（まず直す最優先群）
[references/recipes-quickwins.md](references/recipes-quickwins.md) のレシピに従い、以下の項目をアトミックに適用する：
- **デッドコードの削除 (No.08)**: 参照カウント0の未使用変数・関数・到達不能コードを消去。
- **例外の握りつぶし是正 (No.71)**: 空の `catch (e) {}` や `except: pass` に構造化ログ出力または再スローを追加。
- **マジックナンバーの定数化 (No.05)**: ベタ書きの数値をモジュールトップレベルの名前付き定数に置換。
- **ガード節による深いネスト解消 (No.04 / No.51)**: 条件式を反転させて早期リターン（Early Return）を配置。正常系のインデント深度を0〜1段に平坦化。
- **制御フラグの削除 (No.58)**: ループ終了用の boolean 変数を `break` または `return` に置換。
- **フェイルファスト (No.62)**: 関数の先頭で不正引数のバリデーションを実施。

### Step 4: 自動テスト検証＆アトミックコミット（Safety Guard）
変更後は必ず同梱の安全ガードを実行し、テストが全件グリーンであることを確認する。
```bash
python3 scripts/safety_guard.py verify --files <modified_files> --message "refactor(P1): apply code-unclutter quick-wins"
```
> **[WARN] 自動ロールバック機構**: テストが1件でも失敗した場合、`safety_guard.py` は自動的に `git checkout` を実行して変更前のクリーンな状態に即座に復元する。

### Step 5: Phase 2 ロジック純化（ユーザー要求または必要時）
[references/recipes-purify.md](references/recipes-purify.md) のレシピに従い、関数内部の凝集度を高める：
- **関数の抽出 (No.01 / No.26)**: LOC > 30 または認知的複雑度 > 10 の関数を、単一責任の小さなサブ関数に分解。
- **問い合わせと更新の分離 (No.35 CQS)**: 状態変更を行う関数（Command）と、計算結果を返す関数（Query）を分離。
- **純粋関数化とイミュータブル (No.94 / No.95)**: 引数の破壊的変更をやめ、副作用のない計算ロジックを独立させる。
- **パラメータオブジェクト (No.33)**: 3つ以上の関連する引数を1つのインターフェース/dataclassに集約。

### Step 6: 完了報告
作業完了後、[references/output-templates.md](references/output-templates.md) のフォーマットに従ってユーザーに報告する。

---

## 4. 現代基準の禁止規則（Modern Negative Constraints）

AIが自己満足でコードを改悪しないよう、[references/anti-patterns.md](references/anti-patterns.md) に基づき以下を厳格に禁止する：

1. [NG] **ヨーダ記法 (`0 == x`) の全面禁止**:
   - `0 == x` や `null == user` は禁止。常に自然言語順序（`x === 0`, `user == null`）を強制する。
2. [NG] **過度な早期共通化の禁止（Rule of Three）**:
   - 出現回数が3回未満のコードは無理に共通化しない（間違った抽象化は重複より害が大きい）。
3. [NG] **ネストした三項演算子の禁止**:
   - `a ? b : c ? d : e` は禁止。ガード節またはルックアップテーブル（No.60）に変換する。
4. [NG] **パブリックAPIの勝手な破壊禁止**:
   - エクスポートされた公開関数のシグネチャを予告なく変更してはならない。

---

## 5. チェックリスト：自己監査（Self-Audit）

作業を完了とする前に、エージェントは以下の10項目を自己監査すること：

- [ ] 1. 外部から見た入出力・振る舞いは100%同一か？
- [ ] 2. 既存の全テストスイートはグリーンか？
- [ ] 3. ヨーダ記法（`0 == x`）やネスト三項演算子が混入していないか？
- [ ] 4. ガード節の導入によって正常系のネストが浅くなったか？
- [ ] 5. 空で握りつぶされていた例外ブロックは解消されたか？
- [ ] 6. マジックナンバーに適切なドメイン名が付与されたか？
- [ ] 7. 触っていない無関係なファイルに変更が波及していないか？
- [ ] 8. 抽出した関数は単一の明確な責任を持っているか？
- [ ] 9. KISS / YAGNI に反した過剰なデザインパターンを作っていないか？
- [ ] 10. 変更内容は小さなステップでアトミックにコミットされているか？
