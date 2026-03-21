---
name: prescription-to-obsidian
description: Extract medication names, strengths, dosage instructions, and prescription date from one or more prescription photos, explain pharmacology and cautions in Traditional Chinese, redact all personal identifiers, and save structured notes to <obsidian vault>/medical records/<YYYY-MM-DD>.md. Use when a user asks to parse doctor prescription images and log medical records into Obsidian.
---

# Prescription to Obsidian（繁體中文）

接到用戶提供藥單／藥袋相片時，執行以下流程。

## 1) 輸入與日期規則
- 接受單張或多張相片。
- 支援批次處理：同一批上傳中，先逐張辨識再合併。
- 優先從相片辨識「處方日期」。
- 若看不到日期，使用當前日期（Asia/Hong_Kong）作為處方日期。
- 若多張相片對應同一日期：合併寫入同一檔案（同一 `<處方日期>.md`）。
- 若多張相片出現不同日期：按日期分拆為多個檔案，各自寫入。

## 2) 私隱與資料最小化（必做）
- 嚴禁記錄任何可識別個人身份資訊（PII），包括但不限於：姓名、身份證號、電話、地址、病歷號、保單號、出生日期、診所條碼/ID。
- 即使相片中可見，也只可用「已移除個人資料」概括，不可抄錄原文。

## 3) 藥物辨識輸出要求
對每個藥物盡量提取：
- 完整藥名（商品名 + 學名，如可辨識）
- 劑型（tablet/capsule/ER 等）
- 強度/分量（如 250mg、600mg）
- 用法用量（每日幾次、每次幾粒、飯前/飯後）
- 配發數量（如可辨識）

若不確定：
- 明確標示「未能清晰辨識」，不得臆測。

## 4) 醫療解釋內容（繁體中文）
每種藥物提供簡明說明：
- 藥理作用（主要機制）
- 常見用途（以處方情境解讀）
- 服用禁忌與注意事項
- 常見副作用與需要盡快求醫的警號

語氣要求：
- 清楚、務實、避免過度承諾
- 不取代醫生診斷；必要時建議覆診/求醫

## 5) Obsidian 記錄路徑與格式
- 檔案路徑：`<obsidian vault>/medical records/<處方日期>.md`
- 多張相片合併規則（同一日期）：
  - 以「藥物名稱 + 強度 + 劑型」作去重鍵，避免重複列出同一藥。
  - 同一藥若不同相片提供互補資訊（例如一張見到劑量、另一張見到用法），應合併成完整一筆。
  - 若資訊衝突，保留「待覆核」標記，並在回覆中提示用戶。
- 若同日已有檔案：以新辨識結果更新內容，保留既有非個資臨床段落；不得回填任何個資。
- 內容標題建議：`# 醫療紀錄 — <處方日期>`
- 建議段落：
  1. 私隱聲明
  2. 已辨識藥物與分量
  3. 藥理作用
  4. 服用禁忌與注意事項
  5. 建議追蹤

## 6) 回覆用戶
回覆需包含：
- 已完成辨識與記錄
- 使用的處方日期
- 儲存路徑
- 是否有任何「未能清晰辨識」項目

## 7) 安全邊界
- 不提供危險劑量調整建議。
- 不鼓勵自行停藥或改藥。
- 如有急症警號（呼吸困難、嚴重過敏、急性視力惡化等），直接建議即時求醫。
