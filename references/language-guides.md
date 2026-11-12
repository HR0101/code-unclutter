# Modern Language Refactoring Guides (主要言語別イディオム指針)

各プログラミング言語の現代的なベストプラクティス・言語機能に即したリファクタリング指針。

---

## 1. TypeScript / Modern JavaScript
- **ガード節 & Optional Chaining (No.65)**:
  `user && user.address && user.address.zip` -> `user?.address?.zip`
- **Null合体演算子 (No.66)**:
  `const limit = options.limit || 10` （※0が偽値判定されるバグ） -> `const limit = options.limit ?? 10`
- **Discriminated Union と Exhaustive Check (No.54 / No.69)**:
  無理にクラス継承やポリモーフィズムを作らず、`type Action = { type: 'A' } | { type: 'B' }` と `never` 型アサーションで網羅性検査を行う。
- **Readonly によるイミュータブル化 (No.95)**:
  関数の引数に `readonly string[]` や `Readonly<User>` を指定し、破壊的変更をコンパイラレベルでブロック。

---

## 2. Python (3.10+)
- **型ヒントの完全適用 (No.91)**:
  `def process(data):` -> `def process(data: dict[str, Any]) -> ProcessResult:`
- **構造的パターンマッチング (No.69)**:
  長い `if/elif` 連鎖を `match / case` 構文に置き換えて平坦化。
- **Dataclass の活用 (No.14 / No.33)**:
  辞書（dict）でデータを受け渡す「基本データ型への執着 (No.15)」をやめ、`@dataclass(frozen=True)` による値オブジェクト化。
- **例外握りつぶしの撲滅 (No.71)**:
  `except Exception:` の裸の捕捉をやめ、特定の例外型（`KeyError`, `ValueError`）に限定し、`logging.exception()` を使用。

---

## 3. Go
- **早すぎる抽象化の徹底排除 (KISS No.81 / YAGNI No.82)**:
  実装が1つしかないインターフェースは作らない。構造体を直接返す（"Accept interfaces, return structs"）。
- **Early Return のイディオム (No.51)**:
  `if err != nil { return nil, err }` の後続処理は else を使わずインデント0で書く。
- **テーブル駆動テスト (No.74 / No.85)**:
  デシジョンテーブルを用いてスライスで入力と期待値を定義し、テストケースを網羅。

---

## 4. Java / C#
- **Record 型の活用 (No.14 / No.33 / No.95)**:
  getter/setterだらけの冗長なボイラープレートクラスを `record`（Java 16+ / C# 9+）に置き換えてイミュータブル化。
- **Stream API パイプライン (No.59)**:
  複雑な入れ子forループを `stream().filter().map().toList()` で宣言的に書き直す。
