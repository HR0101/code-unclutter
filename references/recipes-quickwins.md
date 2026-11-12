# Phase 1: High-Priority Quick-Wins Recipe Guide (まず直す最優先レシピ集)

本リファレンスは、低リスク・高効果で既存の振る舞いを100%保持しながら即座にコードの可読性を引き上げる「Phase 1」の具体的変換レシピ集である。

---

## 1. ガード節による多重ネストの解消 (No.04 深いネスト / No.51 ガード節)

### 悪手（ネスト地獄 / アローヘッドアンチパターン）
正常系ロジックが多重のifブロックの深部に埋もれ、視線移動が激しく理解が困難。

### 処方箋（ガード節 / Early Return）
異常系・境界条件を先頭で判定し、即座に `return` または例外送出する。正常系をインデント深度0〜1段で一直線に書く。

#### TypeScript / JavaScript
```typescript
// [NG] Before
function processPayment(user: User, order: Order): PaymentResult {
  if (user != null) {
    if (user.isActive) {
      if (order != null && order.items.length > 0) {
        if (order.totalAmount > 0) {
          return executeTransaction(user, order);
        } else {
          throw new Error("Invalid total amount");
        }
      } else {
        throw new Error("Order has no items");
      }
    } else {
      throw new Error("User account is suspended");
    }
  } else {
    throw new Error("User not found");
  }
}

// [OK] After (Flattened with Guard Clauses)
function processPayment(user: User, order: Order): PaymentResult {
  if (!user) throw new Error("User not found");
  if (!user.isActive) throw new Error("User account is suspended");
  if (!order || order.items.length === 0) throw new Error("Order has no items");
  if (order.totalAmount <= 0) throw new Error("Invalid total amount");

  // 正常系が一直線に読める
  return executeTransaction(user, order);
}
```

#### Python
```python
# [NG] Before
def register_member(email: str, age: int, terms_agreed: bool) -> Member:
    if email and "@" in email:
        if age >= 18:
            if terms_agreed:
                member = Member.create(email=email, age=age)
                send_welcome_email(member)
                return member
            else:
                raise ValueError("Must agree to terms")
        else:
            raise ValueError("Must be at least 18 years old")
    else:
        raise ValueError("Invalid email address")

# [OK] After
def register_member(email: str, age: int, terms_agreed: bool) -> Member:
    if not email or "@" not in email:
        raise ValueError("Invalid email address")
    if age < 18:
        raise ValueError("Must be at least 18 years old")
    if not terms_agreed:
        raise ValueError("Must agree to terms")

    member = Member.create(email=email, age=age)
    send_welcome_email(member)
    return member
```

---

## 2. 制御フラグの削除 (No.58 制御フラグの削除)

### 悪手
ループや分岐を制御するためだけに boolean 変数を引き回し、スコープ全体で状態追跡が必要になる。

### 処方箋
`break` または即時 `return` に置き換えてフラグ変数そのものを宣言から削除する。

```javascript
// [NG] Before
let found = false;
for (const user of users) {
  if (!found) {
    if (user.id === targetId) {
      sendAlert(user);
      found = true;
    }
  }
}

// [OK] After
for (const user of users) {
  if (user.id === targetId) {
    sendAlert(user);
    break;
  }
}
```

---

## 3. 例外の握りつぶし是正 (No.71 例外の握りつぶし)

### 悪手
`catch (e) {}` や `except: pass`。障害発生時に完全に無言でエラーが消え去り、システムの不透明性を生む。

### 処方箋
最低限構造化ログを出力し、回復不能な場合はドメイン例外として再送出する。

```python
# [NG] Before
try:
    cache_client.set(key, val)
except Exception:
    pass

# [OK] After
try:
    cache_client.set(key, val)
except Exception as e:
    logger.warning("Cache write failed, proceeding with fallback", extra={"key": key, "error": str(e)})
```

---

## 4. マジックナンバーの名前付き定数化 (No.05 マジックナンバー)

### 悪手
`86400`, `0.1`, `3` 等の数値が式の中にベタ書きされており、意図が伝わらない。

### 処方箋
モジュールトップレベルまたはクラス定数（`SCREAMING_SNAKE_CASE`）として宣言し、再利用と意味付けを行う。

```typescript
// [NG] Before
const expiration = Date.now() + 86400 * 1000 * 7;
const price = rawAmount * 1.1;

// [OK] After
const SECONDS_PER_DAY = 86_400;
const SESSION_TTL_DAYS = 7;
const EXPIRATION_OFFSET_MS = SESSION_TTL_DAYS * SECONDS_PER_DAY * 1_000;
const CONSUMPTION_TAX_RATE = 0.10;

const expiration = Date.now() + EXPIRATION_OFFSET_MS;
const price = rawAmount * (1 + CONSUMPTION_TAX_RATE);
```

---

## 5. デッドコード・不要な拡張の削除 (No.08 デッドコード / No.20 疑わしき一般化)

### 悪手
- コメントアウトされた古いコード
- どこからも参照されていないプライベート関数・内部ヘルパー
- 将来使うかもしれないと作られた未使用の引数や抽象インターフェース

### 処方箋
Gitが存在するため、不要コードは1行も残さず即座に削除する。
