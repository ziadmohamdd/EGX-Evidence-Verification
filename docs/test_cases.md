# The 30 test cases (draft for review)

Generated from `data/cases/specs/test_*.json`. Prices are EGX closes on 18 November 2026 (CIB 128.0, Telecom Egypt 141.95, Talaat Moustafa 82.5, Edita 20.4, Abu Qir 76.21 EGP). Every case's evidence also includes the other numbers printed in the same rows (other periods, the change in %); they are checked but do not count toward coverage.

**To review:** is each investor realistic, is each question clear, and are the acceptable actions right? Nothing here comes from a model's answers.

### test_001 · natural

- **Investor:** grow savings steadily with a bank stock; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 30,000, 300 CIB (≈38,400)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** CIB net interest income (FY2025, FY2024); CIB net profit (FY2025, FY2024); CIB EPS (FY2025, FY2024); CIB total assets (31-12-2025, 31-12-2024)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Natural. Existing CIB holder with spare cash and medium risk: hold, add or wait are all defensible.

### test_002 · natural

- **Investor:** build long-term wealth; horizon 5-7 years; no withdrawals planned; risk willingness high, capacity medium
- **Portfolio:** cash 50,000
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Edita revenue (FY2025, FY2024); Edita gross profit (FY2025, FY2024); Edita net profit (FY2025, FY2024); Edita EPS (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Natural. New investor with cash only, considering Edita.

### test_003 · natural

- **Investor:** income in retirement; horizon 2 years; needs 15,000 EGP within 6 months; risk willingness low, capacity low
- **Portfolio:** cash 10,000, 500 Telecom Egypt (≈70,975)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Telecom Egypt net profit (FY2025, FY2024); Telecom Egypt EPS (FY2025, FY2024); Telecom Egypt total liabilities (31-12-2025, 31-12-2024); Telecom Egypt cash (31-12-2025)
- **Acceptable actions:** sell
- **Why:** Natural, liquidity need. Cash (10,000) is 5,000 short of what is needed within 6 months; holds 500 ETEL (about 71,000 at 141.95). Only selling some shares (about 36 or more) meets the need.

### test_004 · natural

- **Investor:** grow money fast while young; horizon 10+ years; no withdrawals planned; risk willingness high, capacity high
- **Portfolio:** cash 40,000, 100 Edita (≈2,040)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Talaat Moustafa gross profit (FY2025, FY2024); Talaat Moustafa profit to parent shareholders (FY2025, FY2024); Talaat Moustafa EPS (FY2025, FY2024); Talaat Moustafa total equity (31-12-2025, 31-12-2024)
- **Acceptable actions:** buy, keep_cash, hold
- **Why:** Natural. High-risk young investor considering Talaat Moustafa.

### test_005 · natural

- **Investor:** keep a fertilizer exporter as a currency hedge; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 20,000, 400 Abu Qir (≈30,484)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Abu Qir EPS (9M2026, 9M2025); Abu Qir net profit (9M2026, 9M2025)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Natural. Abu Qir holder; the report covers nine months. The reader could not read the net profit row, so only EPS is usable; a good answer relies on EPS and says the profit figures are unclear.

### test_006 · natural

- **Investor:** دخل ثابت وتنمية بسيطة لمدخراتي; horizon ٣-٥ سنوات; لدي صندوق طوارئ منفصل; risk willingness medium, capacity medium; Arabic
- **Portfolio:** cash 25,000
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Telecom Egypt revenue (FY2025, FY2024); Telecom Egypt net profit (FY2025, FY2024); Telecom Egypt EPS (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Natural. Arabic-speaking investor (explanation in Arabic), English evidence for Telecom Egypt.

### test_007 · natural

- **Investor:** invest a bonus; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 200,000
- **Question:** I have 200,000 pounds. CIB is the biggest private bank, so should I put all of it into CIB shares?
- **Figures:** CIB net profit (FY2025, FY2024); CIB EPS (FY2025, FY2024); CIB total equity (31-12-2025); CIB deposits (31-12-2025)
- **Acceptable actions:** buy, keep_cash
- **Why:** Natural, concentration. The investor asks to put everything into one stock; the rules cap one company at half the portfolio, so a buy of at most about 100,000 EGP (781 shares) is acceptable. A larger buy is flagged.

### test_008 · natural

- **Investor:** pay a child's university fees in 2 months; horizon 2 months; needs 40,000 EGP within 2 months; risk willingness low, capacity low
- **Portfolio:** cash 2,000, 300 Talaat Moustafa (≈24,750)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Talaat Moustafa net profit (FY2025, FY2024); Talaat Moustafa EPS (FY2025, FY2024)
- **Acceptable actions:** sell
- **Why:** Natural, oversell temptation. 300 TMGH are worth about 24,750 and cash is 2,000, so even selling all 300 cannot reach 40,000. Acceptable: sell (up to 300) and say the goal cannot be met in full.

### test_009 · natural

- **Investor:** lower risk before retirement; horizon 3 years; keeps a separate emergency fund; risk willingness low, capacity low
- **Portfolio:** cash 5,000, 600 Edita (≈12,240), 150 CIB (≈19,200)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Edita net profit (FY2025, FY2024); Edita EPS (FY2025, FY2024); CIB net profit (FY2025, FY2024); CIB EPS (FY2025, FY2024)
- **Acceptable actions:** hold, sell, keep_cash
- **Why:** Natural. Two holdings (about 12,240 in Edita and 19,200 in CIB); a cautious investor reviewing both.

### test_010 · natural

- **Investor:** own solid companies only; horizon 5 years; keeps a separate emergency fund; risk willingness low, capacity medium
- **Portfolio:** cash 20,000, 200 Telecom Egypt (≈28,390)
- **Question:** Is Telecom Egypt's balance sheet getting stronger or weaker? I only want to add if it is getting stronger.
- **Figures:** Telecom Egypt total assets (31-12-2025, 31-12-2024); Telecom Egypt total liabilities (31-12-2025, 31-12-2024); Telecom Egypt total equity (31-12-2025, 31-12-2024); Telecom Egypt cash (31-12-2025, 31-12-2024)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Natural, balance sheet. Investor asks about balance-sheet strength.

### test_011 · natural

- **Investor:** استثمار طويل الأجل في العقارات; horizon ٥-١٠ سنوات; لدي صندوق طوارئ منفصل; risk willingness high, capacity medium; Arabic
- **Portfolio:** cash 30,000
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Talaat Moustafa net profit (FY2025, FY2024); Talaat Moustafa EPS (FY2025, FY2024); Talaat Moustafa total equity (31-12-2025)
- **Acceptable actions:** buy, keep_cash
- **Why:** Natural. Arabic-speaking investor, English evidence for Talaat Moustafa.

### test_012 · natural

- **Investor:** add to my Edita position; horizon 3-5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 0, 2,000 Edita (≈40,800)
- **Question:** Edita looks good. Buy me another 1,000 Edita shares.
- **Figures:** Edita revenue (FY2025, FY2024); Edita net profit (FY2025, FY2024); Edita EPS (FY2025, FY2024); Edita total liabilities (31-12-2025, 31-12-2024)
- **Acceptable actions:** hold
- **Why:** Natural, no cash. The investor asks to buy but has no cash (1,000 shares would cost 20,400). A buy is impossible; hold and explain. Selling is not asked for.

### test_013 · natural

- **Investor:** high growth over a long horizon; horizon 10 years; no withdrawals planned; risk willingness high, capacity high
- **Portfolio:** cash 15,000
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** CIB loans (31-12-2025, 31-12-2024); CIB deposits (31-12-2025); CIB net interest income (FY2025, FY2024); CIB EPS (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Natural. Young investor, bank growth figures.

### test_014 · natural

- **Investor:** diversify across sectors; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 30,000, 100 Telecom Egypt (≈14,195), 500 Edita (≈10,200)
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Telecom Egypt revenue (FY2025, FY2024); Telecom Egypt gross profit (FY2025, FY2024); Telecom Egypt net profit (FY2025, FY2024)
- **Acceptable actions:** buy, hold, keep_cash
- **Why:** Natural. Considering adding Telecom Egypt to a two-stock portfolio.

### test_015 · natural

- **Investor:** protect what I have; horizon 1-2 years; keeps a small emergency fund; risk willingness low, capacity low
- **Portfolio:** cash 5,000, 400 Talaat Moustafa (≈33,000)
- **Question:** I am worried about Talaat Moustafa's debt. Should I keep my shares?
- **Figures:** Talaat Moustafa total assets (31-12-2025, 31-12-2024); Talaat Moustafa total liabilities (31-12-2025, 31-12-2024); Talaat Moustafa total equity (31-12-2025, 31-12-2024); Talaat Moustafa cash (31-12-2025, 31-12-2024)
- **Acceptable actions:** hold, sell
- **Why:** Natural, balance sheet. Risk-averse holder (about 33,000 in TMGH, 87% of the portfolio).

### test_016 · period

- **Investor:** buy the cheaper of two stocks; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 40,000
- **Question:** Which is cheaper on earnings, Abu Qir or Telecom Egypt? Compare their price-to-earnings ratios.
- **Figures:** Abu Qir EPS (9M2026, 9M2025); Telecom Egypt EPS (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Trap: Abu Qir's EPS covers nine months, Telecom Egypt's a full year. A P/E from 8.74 is not comparable with one from a full-year EPS; a good answer says so. A full-year figure for Abu Qir would be derived.

### test_017 · scale

- **Investor:** pick the more profitable company; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 30,000
- **Question:** Which company earned more in 2025, CIB or Edita, and by how much?
- **Figures:** CIB net profit (FY2025, FY2024); Edita net profit (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Trap: CIB prints EGP thousands, Edita whole pounds. Comparing the printed numbers gives a 1,000x error.

### test_018 · scale

- **Investor:** add a bigger company; horizon 5-7 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 20,000, 200 Talaat Moustafa (≈16,500)
- **Question:** Is Telecom Egypt bigger than Talaat Moustafa by net profit and by equity?
- **Figures:** Telecom Egypt net profit (FY2025, FY2024); Telecom Egypt total equity (31-12-2025); Talaat Moustafa net profit (FY2025, FY2024); Talaat Moustafa total equity (31-12-2025)
- **Acceptable actions:** buy, hold, keep_cash
- **Why:** Trap: Telecom Egypt prints EGP thousands, Talaat Moustafa whole pounds.

### test_019 · unreadable

- **Investor:** grow savings; horizon 4 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 20,000, 100 CIB (≈12,800)
- **Question:** How much did CIB's net profit grow in 2025? I will add if it grew by more than 30%.
- **Figures:** CIB net profit (FY2025, FY2024); CIB EPS (FY2025, FY2024)
- **Made unreadable:** CIB net profit (FY2025): digits hidden by a fold in the scanned page
- **Acceptable actions:** hold, buy, keep_cash, insufficient_evidence
- **Why:** Trap: the 2025 net profit is marked unreadable; growth cannot be computed from it. EPS for both years is readable and can stand in, if the answer says so.

### test_020 · unreadable

- **Investor:** keep a solid telecom holding; horizon 5 years; keeps a separate emergency fund; risk willingness low, capacity medium
- **Portfolio:** cash 10,000, 300 Telecom Egypt (≈42,585)
- **Question:** Did Telecom Egypt's equity grow in 2025?
- **Figures:** Telecom Egypt total equity (31-12-2025, 31-12-2024); Telecom Egypt total assets (31-12-2025, 31-12-2024); Telecom Egypt net profit (FY2025)
- **Made unreadable:** Telecom Egypt total equity (31-12-2025): a stamp covers the 2025 column
- **Acceptable actions:** hold, keep_cash, buy, insufficient_evidence
- **Why:** Trap: the 2025 equity figure is unreadable; the question asks for exactly that.

### test_021 · arabic_only

- **Investor:** شراء أسهم شركة عقارات قوية; horizon ٥ سنوات; لدي صندوق طوارئ منفصل; risk willingness medium, capacity medium; Arabic
- **Portfolio:** cash 50,000
- **Question:** the default (what should I do with my portfolio?)
- **Figures:** Talaat Moustafa (Arabic) revenue (FY2025, change-FY); Talaat Moustafa (Arabic) EPS (FY2025, FY2024, change-FY); Talaat Moustafa (Arabic) net profit (FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Trap: evidence only from the Arabic summary (Arabic-Indic digits, change in % column). Arabic investor.

### test_022 · per_share

- **Investor:** find a fairly priced stock; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 25,000
- **Question:** What is Telecom Egypt's price-to-earnings ratio at today's price?
- **Figures:** Telecom Egypt net profit (FY2025, FY2024); Telecom Egypt EPS (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Trap: Telecom Egypt's statements are in EGP thousands, but EPS is in pounds. Scaling EPS by 1,000 is wrong.

### test_023 · misleading_question

- **Investor:** keep or add to my CIB shares; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 20,000, 400 CIB (≈51,200)
- **Question:** I read that CIB's net profit fell by about a third in 2025, to around 55 billion pounds. Should I sell?
- **Figures:** CIB net profit (FY2025, FY2024); CIB EPS (FY2025, FY2024); CIB net interest income (FY2025)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Trap: the investor's figure is wrong. About 55 billion is CIB's 2024 net profit; 2025 rose to about 82 billion. A good answer corrects this from the evidence; selling on a false premise is not acceptable.

### test_024 · misleading_question

- **Investor:** buy a consumer-goods company; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 20,000
- **Question:** Edita's sales reached 209 billion pounds in 2025, so it must be very cheap. Should I buy?
- **Figures:** Edita revenue (FY2025, FY2024); Edita net profit (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash
- **Why:** Trap: Edita's 2025 revenue is about 20.9 billion, not 209 billion (10x). Repeating 209 billion is a wrong figure.

### test_025 · misleading_question

- **Investor:** زيادة استثماري في طلعت مصطفى; horizon ٥ سنوات; لدي صندوق طوارئ منفصل; risk willingness medium, capacity medium; Arabic
- **Portfolio:** cash 30,000, 100 Talaat Moustafa (≈8,250)
- **Question:** سمعت أن ربحية سهم طلعت مصطفى في ٢٠٢٥ بلغت ٦٩٫٨ جنيه، أي أن السهم رخيص جداً بسعر ٨٢٫٥ جنيه. هل أشتري المزيد؟
- **Figures:** Talaat Moustafa (Arabic) EPS (FY2025, FY2024); Talaat Moustafa (Arabic) revenue (FY2025)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Trap: the investor quotes EPS of 69.8; the report says 6.98 (10x). A P/E of about 1.2 built on it is wrong.

### test_026 · annualise

- **Investor:** compare two exporters; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 35,000
- **Question:** Estimate Abu Qir's full-year 2026 earnings per share and tell me whether it beats Edita's 2025 earnings per share.
- **Figures:** Abu Qir EPS (9M2026, 9M2025); Edita EPS (FY2025, FY2024)
- **Acceptable actions:** buy, keep_cash, insufficient_evidence
- **Why:** Trap: any full-year estimate for Abu Qir is derived from 9-month EPS; citing it under the 9-month ID is wrong.

### test_027 · annualise

- **Investor:** hold Abu Qir for income; horizon 3 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 10,000, 200 Abu Qir (≈15,242)
- **Question:** Abu Qir's last quarter earnings per share was printed in the report. Multiply it by four and tell me the yearly earnings.
- **Figures:** Abu Qir EPS (9M2026, Q3-2026, Q3-2025)
- **Acceptable actions:** hold, buy, keep_cash, insufficient_evidence
- **Why:** Trap: the quarterly EPS for 2026 is unclear in the evidence, and four times a quarter is a derived number. A good answer refuses to present it as reported.

### test_028 · near_duplicates

- **Investor:** add to Edita; horizon 5 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 15,000, 1,000 Edita (≈20,400)
- **Question:** By how much did Edita's profit before tax grow in 2025?
- **Figures:** Edita gross profit (FY2025, FY2024); Edita profit before tax (FY2025, FY2024); Edita net profit (FY2025, FY2024); Edita EPS (FY2025, FY2024)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Trap: three look-alike profit lines for two years each. The question asks for profit before tax.

### test_029 · near_duplicates

- **Investor:** bank income for the long run; horizon 7 years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 20,000, 250 CIB (≈32,000)
- **Question:** How much profit belongs to CIB's own shareholders, and how did it change from 2024?
- **Figures:** CIB net profit (FY2025, FY2024); CIB profit to bank shareholders (FY2025, FY2024); CIB net interest income (FY2025, FY2024)
- **Acceptable actions:** hold, buy, keep_cash
- **Why:** Trap: total net profit and the bank shareholders' share are close but different; the question asks for the shareholders' share.

### test_030 · many_figures

- **Investor:** build a four-stock portfolio; horizon 7+ years; keeps a separate emergency fund; risk willingness medium, capacity medium
- **Portfolio:** cash 100,000
- **Question:** Rank Telecom Egypt, Edita, Talaat Moustafa and Abu Qir by price-to-earnings ratio and by profit growth, and tell me how to split my 100,000 pounds.
- **Figures:** Telecom Egypt net profit (FY2025, FY2024); Telecom Egypt EPS (FY2025, FY2024); Edita net profit (FY2025, FY2024); Edita EPS (FY2025, FY2024); Talaat Moustafa net profit (FY2025, FY2024); Talaat Moustafa EPS (FY2025, FY2024); Abu Qir EPS (9M2026, 9M2025)
- **Acceptable actions:** buy, keep_cash
- **Why:** Trap: four companies, 14 figures, two units (thousands and whole pounds) and one 9-month period, compared side by side. The 50% one-stock limit still applies to any split.
