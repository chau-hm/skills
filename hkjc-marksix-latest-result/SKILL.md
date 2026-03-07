---
name: hkjc-marksix-latest-result
description: Read the latest HKJC Mark Six draw result from https://bet.hkjc.com/ch/marksix using browser automation. Use when asked to open the HKJC Mark Six page and report the most recent draw numbers, draw date, draw number, and special number.
---

# HKJC Mark Six Latest Result

Open `https://bet.hkjc.com/ch/marksix` with the browser tool and take a page snapshot.

Extract the latest draw from the **上期攪珠** section:
- 攪珠期數
- 攪珠日期
- 攪珠結果（6個正選號碼）
- 特別號碼（`+` 後的號碼）

## Workflow

1. Start browser profile `openclaw` if not running.
2. Open `https://bet.hkjc.com/ch/marksix`.
3. Use `snapshot` (prefer `refs="aria"`) to capture structured content.
4. Find **上期攪珠** and read:
   - `攪珠期數` (example: `26/026`)
   - `攪珠日期` (example: `07/03/2026 (星期六)`)
   - `攪珠結果 :` and the seven balls shown
5. Treat the first six numbers as regular numbers and the last number after `+` as special number.
6. Reply in Traditional Chinese unless user asked otherwise.

## Output Template

- 期數：<draw_no>
- 日期：<draw_date>
- 開出號碼：<n1>、<n2>、<n3>、<n4>、<n5>、<n6>
- 特別號碼：<special>

## Notes

- Prefer values shown in **上期攪珠** as the latest completed result.
- If page layout changes, look for labels containing `上期攪珠` or `攪珠結果`.
- If the site fails to load, report the failure clearly and suggest retrying.