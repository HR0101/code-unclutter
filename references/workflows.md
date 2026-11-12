# Code Unclutter: Execution Workflows & Scope Guides

本リファレンスは、エージェントがユーザーの多種多様なリファクタリング要求に応じるための**スコープ別・シナリオ別実行ワークフロー**を規定する。

---

## 1. ファイル単位ワークフロー (`--file <path>`)
> **利用シナリオ**: 「このファイルが読みにくいので綺麗にして」「`order_service.py` をリファクタリングして」

1. **診断スキャン**:
   ```bash
   python3 scripts/scanner.py <path>
   ```
2. **Phase 0 (安全確認)**:
   - ファイルに対応するテストが存在するか確認。
   - なければ、Phase 1以降の着手前に重要関数の引数・戻り値を記録する仕様化テストを作成。
3. **Phase 1 (表層クイックウィン)**:
   - デッドコード削除 (`R-008`)
   - マジックナンバーのモジュール定数化 (`R-005`)
   - ガード節化による3段以上ネストの平坦化 (`R-051`)
   - 空catchブロックのログ出力化 (`R-071`)
4. **自動テスト & コミット**:
   ```bash
   python3 scripts/safety_guard.py verify --files <path> --message "refactor(P1): quick-wins for <path>"
   ```
5. **Phase 2 (関数抽出・CQS)**:
   - 30行を超える関数を意味のあるサブ関数に抽出。
   - 再度テスト検証して完了。

---

## 2. 機能・モジュール単位ワークフロー (`--feature <dir>`)
> **利用シナリオ**: 「`src/payment/` の設計を改善して」「認証モジュール全体を整理して」

1. **モジュール横断スキャン**:
   ```bash
   python3 scripts/scanner.py <dir> --json > /tmp/feature_smells.json
   ```
2. **依存関係の境界画定**:
   - モジュールのパブリックAPI（`index.ts` や `__init__.py` で公開されている関数・クラス）を特定。
   - **不変原則**: 外部公開インターフェースは一切変更しない（または非推奨ラッパーを残す）。
3. **ボトムアップ実行**:
   - Step A: 依存される側のユーティリティやヘルパーから順に Phase 1 を適用。
   - Step B: データクラスや構造体の整理（パラメータオブジェクト No.33）。
   - Step C: メインサービスクラスの巨大化解消（クラスの抽出 No.30）。
4. **回帰テスト全件実行**:
   ```bash
   python3 scripts/safety_guard.py verify --message "refactor(feature): unclutter <dir> module"
   ```

---

## 3. Git差分・ボーイスカウト・ワークフロー (`--diff` / `--staged`)
> **利用シナリオ**: 「今いじった差分をコミット前に整えて」「PR出す前にコードを綺麗にして」

1. **差分ファイル検出**:
   ```bash
   python3 scripts/scanner.py --diff
   ```
2. **スコープの極小化 (ボーイスカウト原則 No.84)**:
   - **禁止**: 自分が触っていない行や別ファイルを勝手に大幅リファクタリングしない。
   - **適用範囲**: 差分で追加・変更された行の周辺（±20行）に限定。
   - 適用項目:
     - 追加した関数のガード節化
     - 変数名のタイポ・ドメイン命名の統一
     - コミット忘れのデッドコードやデバッグ用 print / console.log の削除
3. **リンター・フォーマッター自動実行 (No.86, 87)**

---

## 4. 関数・シンボル指定ワークフロー (`--symbol <name>`)
> **利用シナリオ**: 「`calculate_total` 関数だけネストを浅くして」「この複雑な関数を分割して」

1. **シンボル局所スキャン**:
   ```bash
   python3 scripts/scanner.py <file> --symbol <name>
   ```
2. **関数の純粋関数化チェック (No.94)**:
   - その関数が外部のグローバル変数やインスタンス変数を破壊的に変更していないか確認。
   - 引数ですべての値を受け取り、計算結果を返す「純粋関数」への変換を優先検討。
3. **ガード節適用 (No.51)**:
   - 条件式の反転と早期リターン。
4. **単体テストの追記 (No.85)**:
   - 抽出された関数、またはリファクタリングした関数に対して、境界値テストを追加。

---

## 5. アーキテクチャ刷新・ミカド法ワークフロー (`--mode architect`)
> **利用シナリオ**: 「神クラス `UserManager` を解体したい」「グローバル変数をDI化したい」

1. **ミカド・ゴール設定 (No.98)**:
   ```bash
   python3 scripts/mikado.py goal "Decompose God Class UserManager into Auth, Profile, and Billing"
   ```
2. **依存関係の分解と前提条件の追加**:
   - `task_1`: "Extract Billing operations into BillingService"
   - `task_2`: "Inject BillingService into UserManager constructor"
   - `task_3`: "Redirect callers to BillingService"
3. **1タスクごとの試行とロールバック**:
   - 変更を試行 -> テスト実行 -> 失敗したら `git checkout` で即戻し、阻害要因を新しい前提タスクとして `mikado.py add` に登録。
   - すべての前提がクリアされた時点で最終ゴールを達成。
