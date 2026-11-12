# Phase 2: Logic Purification & Structuring Recipe Guide (ロジック純化レシピ集)

本リファレンスは、関数内部の複雑度（循環的複雑度 No.88 / 認知的複雑度 No.89）を低減し、テスト容易性を劇的に向上させる「Phase 2」の具体的変換レシピ集である。

---

## 1. 関数の抽出 (No.01 長すぎる関数 / No.26 関数の抽出)

### 抽出の目安
- 関数の行数（LOC）が30行を超えている。
- 1つの関数の中に「入力検証」「データ取得」「複雑な計算」「ログ・通知」など複数の責務が同居している。
- コードの一部に「何をしようとしているのか」を説明するインラインコメントが付いている。

### 処方箋
コメントが説明しようとしている処理ブロックを、そのコメント内容を関数名として独立した関数に切り出す。

```typescript
// [NG] Before: 1つの関数で全部やる
function printOwing(invoice: Invoice) {
  let outstanding = 0;

  console.log("***********************");
  console.log("**** Customer Owes ****");
  console.log("***********************");

  // calculate outstanding
  for (const o of invoice.orders) {
    outstanding += o.amount;
  }

  // record due date
  const today = new Date();
  invoice.dueDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 30);

  // print details
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
  console.log(`due: ${invoice.dueDate.toLocaleDateString()}`);
}

// [OK] After: 単一責任の関数に分割
function printOwing(invoice: Invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  recordDueDate(invoice);
  printDetails(invoice, outstanding);
}

function printBanner(): void {
  console.log("***********************");
  console.log("**** Customer Owes ****");
  console.log("***********************");
}

function calculateOutstanding(invoice: Invoice): number {
  return invoice.orders.reduce((sum, order) => sum + order.amount, 0);
}

function recordDueDate(invoice: Invoice): void {
  const today = new Date();
  invoice.dueDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 30);
}

function printDetails(invoice: Invoice, outstanding: number): void {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
  console.log(`due: ${invoice.dueDate.toLocaleDateString()}`);
}
```

---

## 2. 問い合わせと更新の分離 (No.35 CQS原則)

### 悪手
値を計算して呼び出し元に返しつつ、裏で内部状態やデータベースを変更している。呼び出し側は副作用があることに気づきにくい。

### 処方箋
- **Query（問い合わせ）**: 値を返す。副作用（状態変更）は一切持たない（冪等）。
- **Command（更新）**: 状態を変更する。値は返さない（`void`）。

```python
# [NG] Before: 不審者を検知してアラートを鳴らしつつ名前を返す（副作用と取得の混在）
def check_security(people: list[str]) -> str:
    for p in people:
        if p in BLACKLIST:
            send_security_alert(p)  # 副作用！
            return p
    return ""

# [OK] After: 検出処理とアラート処理を分離
def find_miscreant(people: list[str]) -> str | None:
    """純粋な問い合わせ関数（Query）"""
    for p in people:
        if p in BLACKLIST:
            return p
    return None

def alert_for_miscreant(people: list[str]) -> None:
    """副作用を起こすコマンド関数（Command）"""
    miscreant = find_miscreant(people)
    if miscreant:
        send_security_alert(miscreant)
```

---

## 3. パラメータオブジェクトの導入 (No.07 長い引数 / No.14 データの群れ / No.33)

### 悪手
関数の引数が4個以上あり、同じ引数の組み合わせ（例：`startDate, endDate` や `x, y, width, height`）が複数の関数で繰り返し登場する。

### 処方箋
関連する引数のグループを1つの型（TypeScriptのinterfaceやPythonのdataclass）にまとめる。

```typescript
// [NG] Before
function searchEntries(keyword: string, startDate: Date, endDate: Date, category: string, limit: number) { ... }
function exportEntries(startDate: Date, endDate: Date, format: string) { ... }

// [OK] After
interface DateRange {
  startDate: Date;
  endDate: Date;
}

interface SearchCriteria {
  keyword: string;
  range: DateRange;
  category: string;
  limit?: number;
}

function searchEntries(criteria: SearchCriteria) { ... }
function exportEntries(range: DateRange, format: string) { ... }
```

---

## 4. 純粋関数化とイミュータブル (No.94 純粋関数 / No.95 イミュータブル)

### 悪手
引数で渡された配列やオブジェクトを直接変更（インプレース破壊）する。外部スコープに予測不能なバグをもたらす。

### 処方箋
引数を変更せず、新しいオブジェクトや配列を生成して返す。

```typescript
// [NG] Before: 引数の配列を直接ソート・破壊
function getTopScores(scores: number[]): number[] {
  return scores.sort((a, b) => b - a).slice(0, 3);
}

// [OK] After: 新しい配列を作成（イミュータブル）
function getTopScores(scores: readonly number[]): number[] {
  return [...scores].sort((a, b) => b - a).slice(0, 3);
}
```
