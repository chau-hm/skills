---
name: hkjc-marksix-latest-result
description: Read the latest HKJC Mark Six draw result from https://bet.hkjc.com/ch/marksix using browser automation, then read bets from assets/bets.md and evaluate whether each bet wins based on Prize Qualification.
---

# HKJC Mark Six Latest Result

Open `https://bet.hkjc.com/ch/marksix` with the browser tool and take a page snapshot.

Extract the latest draw from the **上期攪珠** section:

- 攪珠期數
- 攪珠日期
- 攪珠結果（6個正選號碼）
- 特別號碼（`+` 後的號碼）

Then read bet lines from `assets/bets.md` and evaluate each line against the draw result.

## Workflow

1. Start browser profile `openclaw` if not running.
2. Open `https://bet.hkjc.com/ch/marksix`.
3. Use `snapshot` (prefer `refs="aria"`) to capture structured content.
4. Find **上期攪珠** and read:
   - `攪珠期數` (example: `26/026`)
   - `攪珠日期` (example: `07/03/2026 (星期六)`)
   - `攪珠結果 :` and the seven balls shown
5. Treat the first six numbers as regular numbers and the last number after `+` as special number.
6. Read `assets/bets.md`.
7. Parse each non-empty line as one bet:
   - Accept separators: `,` `，` spaces.
   - Convert to integers and keep unique numbers only.
   - A valid bet must contain at least 6 unique numbers (ignore invalid lines but report them).
8. For each valid bet, calculate:
   - `regular_hits`: count of numbers that match the 6 regular draw numbers.
   - `special_hit`: whether the bet contains the special number.
9. Determine prize by priority order (high to low):
   - 頭獎: `regular_hits = 6`
   - 二獎: `regular_hits = 5` and `special_hit = true`
   - 三獎: `regular_hits = 5`
   - 四獎: `regular_hits = 4` and `special_hit = true`
   - 五獎: `regular_hits = 4`
   - 六獎: `regular_hits = 3` and `special_hit = true`
   - 七獎: `regular_hits = 3`
   - Otherwise: 未中獎
10. Reply in Traditional Chinese unless user asked otherwise.

## Output Template

- 期數：<draw_no>
- 日期：<draw_date>
- 開出號碼：<n1>、<n2>、<n3>、<n4>、<n5>、<n6>
- 特別號碼：<special>

- 投注結果：
  - 第1注：<bet_numbers>｜中<regular_hits>個正選<+特別號碼(如有)>｜<獎項或未中獎>
  - 第2注：<bet_numbers>｜中<regular_hits>個正選<+特別號碼(如有)>｜<獎項或未中獎>

- 無效投注（如有）：
  - 第<line_no>行：<原始內容>（原因：少於6個有效且不重複號碼 / 含非法值）

## Notes

- Prefer values shown in **上期攪珠** as the latest completed result.
- If page layout changes, look for labels containing `上期攪珠` or `攪珠結果`.
- If the site fails to load, report the failure clearly and suggest retrying.
- 每行投注視為一注獨立判斷；如某注多於6個號碼，按該行所有號碼直接計算命中數（不展開複式組合）。

## Prize Qualification

| 獎項 | 中獎條件                           | 獎金                                                                    |
| ---- | ---------------------------------- | ----------------------------------------------------------------------- |
| 頭獎 | 選中6個「攪出號碼」                | 獎金會因應該期獲中頭獎注數而有所不同，每期頭獎獎金基金不少於港幣800萬元 |
| 二獎 | 選中5個「攪出號碼」 + 「特別號碼」 | 獎金會因應該期獲中二獎注數而有所不同                                    |
| 三獎 | 選中5個「攪出號碼」                | 獎金會因應該期獲中三獎注數而有所不同                                    |
| 四獎 | 選中4個「攪出號碼」 + 「特別號碼」 | 固定獎金港幣9,600元                                                     |
| 五獎 | 選中4個「攪出號碼」                | 固定獎金港幣640元                                                       |
| 六獎 | 選中3個「攪出號碼」 + 「特別號碼」 | 固定獎金港幣320元                                                       |
| 七獎 | 選中3個「攪出號碼」                | 固定獎金港幣40元                                                        |
