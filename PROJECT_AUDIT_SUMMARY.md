# Egyptian Investment Guide — Project and Grilling Audit

**Prepared:** 20 November 2026  
**Audience:** Project partners and academic collaborators  
**Purpose:** Consolidate the original idea, the 37-question requirements interview, research findings, approved scope, and outstanding work.  
**Status:** Research scope approved. Experimental protocol and implementation are not yet complete.

> This document records a requirements and research discussion. It is not evidence that the system works, a report of experimental results, a legal assessment, or investment advice.

## 1. Executive summary

The proposed product is a bilingual, multi-agent investment guide for individual investors with basic investment knowledge who want help understanding and managing investments in Egyptian listed companies.

The intended application will combine investor interviewing, stock analysis and prediction, news and macroeconomic analysis, company financial-report analysis, portfolio recommendations, and accessible explanations. Its initial company universe is EGX30, with later expansion to EGX70 and EGX100.

The application's main output is an evidence-backed recommendation: buy, hold, reduce/sell, retain cash, or report insufficient evidence. Financial question answering is also supported, but it is not the sole purpose. Recommendations must account for existing holdings, available funds, investor circumstances, and uncertainty. The application must not recommend selling unowned shares or quantities greater than the investor holds.

The immediate objective is an academic paper, not completion of the entire application. The paper will investigate whether explicit financial-evidence verification improves the reliability of recommendations produced by single-agent and multi-agent configurations. A minimal end-to-end prototype is acceptable for the paper; the complete first product version follows afterward.

Four experimental conditions have been approved: single agent and multiple agents, each with the evidence verifier disabled and enabled. Mandatory portfolio and arithmetic checks remain enabled in all conditions. Actual results must come from running the implemented system; no experimental findings have been generated yet.

TradingAgents is the approved provisional foundation, subject to a bounded compatibility check. New forecasting-model development is deferred from the first paper. Public datasets and existing resources come first; five years of data is no longer a requirement.

## 2. How to interpret this audit

- **Agreed:** Explicitly accepted during the interview or included in the final approved scope.
- **Provisional:** An accepted direction that still requires a compatibility, data, or feasibility check.
- **Proposed:** A suggested detail that has not been locked into an executable protocol.
- **Unresolved:** A choice, external requirement, or factual gap that remains open.
- **Research finding:** Information reported from the cited sources, with the access and verification limitations noted below.

Scope approval did not settle every technical or scientific detail. In particular, it did not approve a specific model, numerical allocation policy, sample size, expenditure, or claim of demonstrated novelty.

## 3. Original idea and full product vision

### 3.1 Intended users and positioning

**Agreed:** The primary audience is individual investors with basic knowledge who need a guide, not a system promising investment profits.

The application should interview users to understand their objectives, expectations, investment horizon, liquidity needs, willingness to accept losses, and financial ability to withstand losses. A desired return is not automatically an achievable or suitable target.

The longer-term ambition may become a startup. The current deliverable is a research prototype. Commercial operation, data rights, privacy, regulatory obligations, and suitability practices have not been assessed or approved.

### 3.2 Market coverage

- **Full application, phase one:** EGX30 companies.
- **Later expansion:** EGX70 and EGX100 companies.
- **First paper:** A documented subset of EGX30 companies is acceptable. A starting range of roughly 5–8 companies was accepted, with expansion if useful and feasible.
- The final subset, membership cutoff, sectors, and document dates remain to be specified.
- A subset study must not be reported as validation across every EGX30 company.

### 3.3 Intended capabilities

The full first application version retains all of the following requirements:

1. Investor interviewing and profile interpretation.
2. Technical/market analysis and a predictive component trained or evaluated using suitable Egyptian-market data.
3. News and external-event analysis, including political developments, macroeconomics, interest rates, sentiment, and investor expectations.
4. Company financial-statement and financial-performance analysis.
5. Portfolio-aware recommendations with proposed investment amounts or changes.
6. Evidence-backed Arabic and English explanations.
7. Accessibility and adaptable conversational wording.
8. Honest uncertainty, risk warnings, and user-directed simulations where appropriate.

These are capability requirements, not an approved final agent topology. The number of agents and responsibility boundaries remain open. Overlap between news, earnings coverage, and financial-statement analysis must be resolved during design.

### 3.4 Recommendations and portfolio boundaries

**Agreed:**

- Buying and selling are not the only valid outcomes. Holding, retaining cash, and insufficient evidence are also valid.
- Every outcome receives a brief explanation, including why it was selected, supporting evidence, limitations, and portfolio effect.
- The application distinguishes the investor's current portfolio from the portfolio that would result from proposed changes.
- Selling an unowned security is prohibited. Proposed sales cannot exceed available holdings.
- Proposed purchases must reconcile with available funds under the stated cost assumptions.
- Numerical constraints are checked independently of the language model; persuasive prose cannot override invalid arithmetic.
- Version one recommends and simulates; it does not place brokerage orders.

**Unresolved:** Detailed allocation objectives, concentration limits, leverage policy beyond the no-short/no-oversell requirements, transaction-cost assumptions, lot sizes, settlement treatment, and treatment of unavailable price data.

### 3.5 Investor choice versus endorsement

The user initially wanted the application to comply with an investor's requested strategy even when it appeared wrong, provided a warning was given. The interview resolved this through two distinct outputs:

- **Recommended plan:** Consistent with assessed goals and constraints, under stated assumptions.
- **User-directed simulation:** A clearly labelled hypothetical exploration of a requested strategy, including one identified as unsuitable. It is not endorsed as a suitable recommendation.

The system should explain unrealistic expectations and possible changes to goals, timelines, or contributions. It must not manufacture a plausible route to an unsupported target or describe an unsuitable allocation as the investor's best portfolio.

### 3.6 Language and accessibility

**Agreed:** Arabic and English support, understandable financial explanations, and optional adaptation of conversational wording. Facts, figures, uncertainty, and warnings must not change with the user's preferred tone.

Accessibility is a product requirement. WCAG 2.2 AA was suggested as a target, but conformance has not been tested or formally established. Exact interface, assistive-technology coverage, Arabic layout requirements, and accessibility acceptance tests remain open.

## 4. Information sources and document handling

### 4.1 Data strategy

The original idea proposed training on five years of Egyptian-market stock data. This was subsequently relaxed: available suitable datasets may be used, and five years is not mandatory.

**Agreed:**

- Search public datasets and use existing resources before requesting subscriptions.
- Do not assume that public display grants bulk-download, model-training, redistribution, or commercial rights.
- Propose any paid access with a capped budget for approval; no spending has been authorized.
- Official company disclosures are the initial document scope, whether retrieved online or manually supplied.
- General arbitrary user uploads are not a committed first-paper capability.

### 4.2 Formats

**Required:** Scanned-document handling cannot simply be excluded. Searchable PDFs alone are insufficient.

The intended extraction path must handle text-bearing and scanned financial PDFs, preserve table context, and report failures. Source inspection also found relevant XLSX workbooks and HTML announcements. Those are evidence-backed candidate formats, but comprehensive XLSX/HTML support has not been independently finalized as a first-paper commitment.

No blanket promise to support every file type was made. Standalone JPG/PNG disclosures and legacy XLS files were not verified during the source inspection.

### 4.3 Ambiguous figures

The discussion distinguished preserving source information from treating an interpretation as reliable input.

**Final agreement:**

1. Preserve the original source value and its context.
2. Flag ambiguity rather than silently deleting the evidence.
3. Attempt resolution through extraction retries, relevant page/table inspection, another official version where available, and appropriate financial consistency checks.
4. If unresolved, do not silently use the uncertain interpretation in calculations.
5. Explicitly tell the user which figures were not used and which conclusions are affected.
6. If the missing information is essential, leave the conclusion conditional or incomplete rather than asserting confidence.

Relevant ambiguities include digit recognition, negative values, currency, thousands/millions, reporting period, quarterly versus cumulative amounts, entity, and accounting basis. A supported range can be useful; invented bounds are not a substitute for evidence.

### 4.4 Historical and current use

The paper uses frozen, dated information for reproducibility. The later application must also support new investment analysis using sufficiently current sources with clear timestamps.

Historical demonstrations must not be presented as current recommendations. A historical evaluation also does not establish that a contemporary pretrained language model was unaware of later outcomes.

## 5. First-paper scope

### 5.1 Approved direction

**Working title, not final:**

> Evaluating Evidence Verification in Multi-Agent Investment Recommendations Using Arabic and English Egyptian Financial Disclosures

**Primary research question:**

> Does explicit evidence verification reduce incorrect financial claims and unsupported reasoning in otherwise comparable single-agent and multi-agent investment-recommendation systems?

The paper should evaluate actual outputs of the implemented system. It is not limited to a standalone question-answering demo: its minimal workflow ends with a portfolio-aware recommendation and explanation.

### 5.2 Minimal end-to-end workflow

1. Obtain an investor profile and a controlled portfolio/cash scenario.
2. Analyze real, dated company information.
3. Extract and interpret financial evidence, including scanned material within the supported scope.
4. Produce a proposed action, amount or portfolio change, and rationale.
5. Apply mandatory numerical and holdings checks.
6. Explain the result in Arabic or English, including evidence, uncertainty, and unused information.

The exact recommendation policy, prompts, agent topology, model, and document corpus remain to be specified. This workflow does not imply that every future news or forecasting feature is already implemented.

### 5.3 Explicitly deferred

- Building the complete first application before submitting the paper.
- Developing a newly trained forecasting model for this paper.
- Claiming a new forecasting method or demonstrated improvements in investment returns.
- Brokerage execution.
- Full EGX70/EGX100 coverage.
- Production or startup readiness.

If a forecasting baseline is used, it must be documented and held comparable across experimental configurations. A rule-based method must not be misrepresented as a trained prediction.

### 5.4 Candidate contribution and claim limits

The potential contribution is an evaluated evidence-verification method, a carefully checked Egyptian disclosure evaluation set, and an analysis of errors and downstream recommendation reasoning.

This is still a **candidate contribution**, not established originality. Existing research already covers financial multi-agent systems, Arabic financial NLP, numerical financial reasoning, and Egyptian stock forecasting.

The following claims are not justified merely by implementation:

- First-ever multi-agent financial assistant.
- Novelty solely because data comes from Egypt.
- Novelty solely because the interface or documents are Arabic.
- Optimal or profitable recommendations because explanations are factually correct.
- Validated financial suitability because arithmetic and portfolio constraints pass.
- Broad investor benefit based on a small usability pilot.

Negative findings must be reported honestly. If multiple agents do not improve results, that is a legitimate outcome.

## 6. Experimental design

### 6.1 Approved comparison

| Condition | Agent configuration | Optional evidence verifier | Mandatory holdings/arithmetic checks |
|---|---|---|---|
| A | Genuine single agent | Off | On |
| B | Genuine single agent | On | On |
| C | Multiple agents | Off | On |
| D | Multiple agents | On | On |

The evidence verifier is the experimental intervention. Basic portfolio validity must not be disabled to create an apparently stronger treatment effect.

### 6.2 Approved controls

- Use comparable source information, investor scenarios, model setup, tools, forecasting inputs if any, and portfolio rules.
- Develop instructions and evaluation rules using development examples, then freeze them before final testing.
- Do not independently tune each condition until it produces attractive results.
- Run the baselines within this study rather than substitute scores copied from prior papers. This does not require locally hosted models; local versus approved API-based inference remains open.
- Isolate cross-run memory so experimental conditions do not learn from one another.
- Preserve failures, unresolved inputs, and unfavorable outputs.
- Distinguish hypothetical investor inputs from real market evidence and measured system outputs.

### 6.3 Agreed evaluation areas; exact metrics still open

| Area | What the experiment should examine | What it does not prove |
|---|---|---|
| Financial correctness | Figures, units, periods, entity/basis, and calculations | That an issuer's disclosure is itself true |
| Evidence support | Whether the cited source supports each relevant claim | That the investment will perform well |
| Coverage and abstention | What is answered, omitted, unresolved, or correctly withheld | That refusal alone makes a system useful |
| Portfolio validity | No unowned sales, no overselling, cash reconciliation, valid arithmetic | Comprehensive real-world suitability |
| Recommendation reasoning | Whether stated reasoning uses supported evidence and discloses exclusions | A unique economically correct buy/sell action |
| Resource use | Cost and latency under documented conditions | Production scalability |
| User experience | Understanding of output, warnings, and evidence | Representative investor outcomes |

Primary endpoints, denominators, numerical tolerances, sample size, repeat runs, uncertainty estimates, annotation rubric, and pass/fail thresholds are not locked yet. Accuracy and coverage must be reported together to avoid rewarding a system that improves apparent precision by withholding almost everything.

### 6.4 Reference answers

The partners agreed to prepare and cross-check source-linked reference answers. One author prepares them; the other checks them without seeing system outputs. Disagreements are resolved and the final evaluation set is frozen before testing.

Existing benchmark references can reduce the work, but translations, generated answers, and language-model judges are not automatically reliable ground truth. Technical qualifications do not independently establish expert financial-advice judgment. Dean or finance-reviewer involvement remains potential support, not assumed capacity.

### 6.5 Real-user pilot

The user wants real participants to observe authentic interaction and experience, while acknowledging that a small sample is not representative. The paper may evaluate the minimal implemented workflow; the full product experience is a later objective.

The proposed pilot uses real participants with hypothetical portfolios and no brokerage execution. It is supplementary to the controlled system experiments. Recruitment, participant count, measures, consent, privacy procedures, and university ethics-review requirements remain unresolved. No participants have been recruited.

## 7. Reusable framework assessment

### 7.1 Provisional choice: TradingAgents

**Agreed:** Use a version-pinned subset of TradingAgents as the provisional foundation, subject to a bounded compatibility check.

Read-only source inspection was reported on **19 November 2026**, at commit `9fa1196fffbcfd9de5146d2dd2869df84ab99838`:

- [Portfolio context](https://github.com/TauricResearch/TradingAgents/blob/9fa1196fffbcfd9de5146d2dd2869df84ab99838/tradingagents/portfolio.py) accepts cash, currency, and positions.
- [Data routing](https://github.com/TauricResearch/TradingAgents/blob/9fa1196fffbcfd9de5146d2dd2869df84ab99838/tradingagents/dataflows/router.py) offers a possible extension seam for EGX data adapters.
- [Graph setup](https://github.com/TauricResearch/TradingAgents/blob/9fa1196fffbcfd9de5146d2dd2869df84ab99838/tradingagents/graph/setup.py) exposes workflow nodes and edges.

Important gaps:

- Its holdings context is not a deterministic no-short/no-oversell enforcement mechanism.
- Its portfolio representation permits short positions.
- Its inspected decision schemas do not provide the required validated quantity constraints.
- Generic Arabic output instructions do not establish Arabic OCR/table reliability.
- Selecting one analyst does not remove the remaining researchers, managers, trader, and risk agents; it is not a genuine single-agent baseline.
- Cross-run memory requires explicit experimental isolation.

No compatibility test or executable run has been performed in this project.

### 7.2 FinRobot alternative

Read-only inspection was reported at commit `63e1884a42ea7b729551a5424b4bd6a65af636e0`. Its [repository](https://github.com/AI4Finance-Foundation/FinRobot/tree/63e1884a42ea7b729551a5424b4bd6a65af636e0) contains materially different V0, V1, and V2 paths. The installed package and current desktop/backend architecture should not be conflated.

FinRobot provides useful document/retrieval and single/multi-agent components, but the inspected paths did not establish a simpler complete solution for this user's portfolio constraints and Egyptian bilingual evidence requirements.

Both inspected code licenses were Apache-2.0; notices and modification obligations require attention. Code licenses do not grant permission to use or redistribute financial-provider data. No complete legal or dependency-license audit has been performed.

## 8. Research and data findings

These are targeted source checks, not a systematic literature review or a completed dataset audit. Prior papers' results are not this project's results.

### 8.1 Relevant literature

| Source | Why it matters | Limitation for this project |
|---|---|---|
| [TradingAgents: Multi-Agents LLM Financial Trading Framework](https://arxiv.org/abs/2412.20138), 2024 preprint, revised 2025 | Existing specialist analysts, debate, decision and risk workflows | Rules out claiming multi-agent finance architecture alone as novelty; not an Egyptian reliability validation |
| [FinRobot: An Open-Source AI Agent Platform for Financial Applications using Large Language Models](https://arxiv.org/abs/2405.14767), 2024 | Existing financial agents, orchestration and document-analysis concepts | Paper architecture and current repository capabilities are not interchangeable |
| [AraFinNews: Arabic Financial Summarisation with Domain-Adapted LLMs](https://arxiv.org/abs/2511.01265), 2025 | Arabic financial-language resources and domain adaptation | Summarization references are not financial arithmetic ground truth |
| [A Hybrid Model Combining Discrete Wavelet Transform and Nonlinear Autoregressive Neural Network for Stock Price Prediction: An Application in the Egyptian Exchange](https://www.iieta.org/journals/ria/paper/10.18280/ria.370103), 2023 | Studies 24 individual EGX30 stocks using weekly 2016–2020 prices; discusses preprocessing leakage | Price forecasting, not Arabic evidence verification |
| [Assess deep learning models for Egyptian exchange prediction using nonlinear artificial neural networks](https://doi.org/10.1007/s00521-020-05374-9), 2021, online 2020 | Egyptian index forecasting and a linked author-published dataset | Six index series rather than individual stock histories; full methods were not reviewed in the accessible inspection |
| [Hybrid Model "ARIMA -ANN" Using for forecasting Stock Index EGX30](https://doi.org/10.21608/caf.2023.319866), 2023 | Egyptian statistical/neural forecasting reading lead | Bibliographic metadata verified; abstract, data period and results not verified |
| [FinQA](https://aclanthology.org/2021.emnlp-main.300/), 2021 | Evidence-linked financial questions and executable numerical reasoning | English, non-Egyptian; corrected releases should be used |
| [TAT-QA](https://aclanthology.org/2021.acl-long.254/), 2021 | Table/text reasoning, derivations and answer scales | English, pre-extracted contexts rather than an Arabic PDF-ingestion test |
| [SAHM](https://arxiv.org/abs/2604.19098), 2026 | Arabic financial reasoning and evaluation resources | Not a verified Egyptian company-report PDF benchmark; licensing statements differ across releases |
| [Assessing Look-Ahead Bias in Stock Return Predictions Generated By GPT Sentiment Analysis](https://arxiv.org/abs/2309.17322), 2023 | Relevant warning about historical LLM evaluation | Restricting retrieved documents to a date does not remove knowledge already in model weights |

### 8.2 Public benchmark candidates

| Dataset | Useful content | Licensing/access finding and caveat |
|---|---|---|
| [SAHM Arabic financial QA](https://huggingface.co/datasets/SahmBenchmark/arabic-financial-qa_eval) | Arabic text, questions and reference answers | Public evaluation data; cards list Apache-2.0 while paper describes CC BY-NC annotations. Clarify commercial use. Not source PDFs with page-level evidence. |
| [FinQA](https://github.com/czyssrs/FinQA/tree/main/dataset) | Tables, text, supporting facts, answers and calculation programs | Official site lists dataset CC BY 4.0; software licensing is separate. Checked release does not bundle source PDFs. |
| [TAT-QA](https://github.com/NExTplusplus/TAT-QA) | Financial table/text questions, derivations and scales | Current official README explicitly lists CC BY 4.0. This corrects an earlier discussion warning based on the paper's older non-commercial wording. |
| [TAT-DQA](https://nextplusplus.github.io/TAT-DQA/) | Selected PDF pages, text/OCR coordinates and evidence mappings | Project states CC BY 4.0. Sample QA and download listing checked; full archive not audited. Substantial overlap with TAT-QA prevents treating them as independent evidence. |
| [AraFinNews](https://github.com/ArabicNLP-UK/AraFinNews) | Arabic financial articles and headlines | CC BY-NC 4.0; auxiliary research corpus, not numerical-QA gold. Git LFS matters when retrieving files. |

No inspected public dataset directly established the complete Egyptian Arabic scanned-report verification task. A small Egyptian holdout is therefore proposed, but has not been created or validated.

### 8.3 Egyptian price-data availability

- [EGX official index history](https://www.egx.com.eg/en/indexdata.aspx?nav=1&type=1): a public EGX30 benchmark-history interface exists. An index series is not the set of company histories needed for stock selection.
- [EGX CIB company history](https://www.egx.com.eg/en/StocksData.aspx?ISIN=EGS60121C018): company prices/statistics were inspected in the browser, with period selections up to three years. This does not establish bulk-export access for the whole universe.
- [Mendeley Egyptian Stock Exchange dataset, version 2](https://data.mendeley.com/datasets/7chdr568x7/2): author-published in 2020, six index series, stated CC BY 4.0. Not recent company-level coverage; full file-quality audit not performed.
- [Kaggle EGX Stock Data](https://www.kaggle.com/datasets/eyadshaban/egx-stock-data): potential individual-company histories, but the inspected card lists an unknown license and warns of possible errors. Not yet an approved research foundation.
- [EGID](https://egidegypt.com/): official information-provider route to investigate if necessary.
- [ICE EGX offering](https://developer.ice.com/fixed-income-data-services/catalog/egyptian-exchange-egx): explicitly advertises historical and end-of-day data. Exact coverage, permissions, entitlement and price require confirmation.

No complete research-ready company-price dataset has been acquired for this project. No subscription is currently required or authorized.

### 8.4 Official disclosure-format evidence

| Issuer | Official source | What was observed |
|---|---|---|
| CIB | [Financial-statements library](https://www.cibeg.com/en/investor-relations/ir-library/financial-statements) | Arabic/English text-bearing PDFs; Arabic reading-order problems. Excel-generated PDF metadata does not mean downloadable XLSX data exists. |
| Telecom Egypt | [2025 quarterly archive](https://ir.te.eg/en/FinancialInformation/QuarterlyResults/2025) | Earnings PDFs, actual XLSX Fact Books, and separate HTML announcements. Statements and management summaries must remain distinct. |
| Talaat Moustafa | [Investor relations](https://talaatmoustafa.com/investor-relations) | Text-bearing statements and image-bearing results summaries. |
| Abu Qir Fertilizers | [Financial statements](https://abuqir.net/investor-relations/financial-statements) | An Arabic full-report PDF composed of raster images without detected font objects, and mixed-content documents. Fiscal periods require care. |
| Edita | [Results centre](https://ir.edita.com.eg/en/results-center) | Image-based signed statements with copier metadata. Statutory statements, management accounts and accounting bases must not be conflated. |

These findings concern inspected examples, not every report page, year, or EGX30 issuer. Membership at the study cutoff must be confirmed before final selection.

## 9. Conference audit

### 9.1 What the supplied poster says

- **Event:** The 16th international conference on ICT in Our Lives.
- **Theme:** ICT and Digital Innovation in Academia.
- **Host:** Faculty of Business, Alexandria University.
- **Organizer:** Information Systems and Computers Department.
- **Event dates:** 19–21 December 2026.
- **Format:** Faculty of Business and online through MS Teams.
- **Working languages:** English, Arabic and French.
- **ISSN shown:** 2314-8942.
- **Contacts shown:** ictinourlives@gmail.com and ictinourlives@alexu.edu.eg.
- **Facebook shown:** https://www.facebook.com/ICTinOurLives.

### 9.2 What remains unverified

A check on 19 November 2026 did not find an accessible current call for papers establishing:

- Abstract or full-paper deadline.
- Submission mechanism.
- Template, page limit or anonymity requirements.
- Review procedure.
- Detailed 2026 tracks and scope.
- Publisher, proceedings or indexing arrangements.
- AI-use/disclosure policy.

The [conference website](http://ictinourlives.alexu.edu.eg/) identifies the series, but current author instructions were not retrievable. Available university materials concerned older editions and cannot establish 2026 rules. An ISSN does not independently establish peer review, IEEE publication, Scopus, or Web of Science indexing.

The proposed topic may fit the series, but fit with this year's academia-focused theme is not confirmed. The paper must not be artificially presented as an academic-teaching study if that is not what is evaluated.

The initial two-week ambition was a planning target, not a verified submission deadline. Event dates are not submission dates. No organizers were contacted, and no registration or submission was made.

## 10. People, resources and feasibility

- Two contributors are available; the user states that both are qualified for the work.
- Exact weekly hours and role allocation are not fixed.
- The dean has offered help if resources can be provided. This is not a commitment to subscriptions, annotation time, financial review or ethical approval.
- Public resources come first. Existing university access can be checked before requesting purchases.
- No paid services, model provider, budget, computing configuration or deployment platform have been selected.
- A minimal paper prototype may be feasible, but no completion or publication guarantee is justified before the protocol, resources and venue requirements are checked.

## 11. Full grilling decision log

The table records final interpretations, including where later answers revised earlier ones. It is a decision audit, not a verbatim transcript.

| Question | Subject | Answer and final disposition |
|---|---|---|
| Q1 | Audience | Individual investors with basic knowledge; the application acts as a guide. |
| Q2 | Purpose | Research prototype and paper first; possible startup later. |
| Q3 | Product responsibility | Recommend companies/stocks and amounts; accessible, honest and adaptable explanations. |
| Q4 | Investment horizon | Discover needs through interviewing; no single product-wide horizon selected. Supported/evaluated horizons remain to be specified. |
| Q5 | Training and testing | Initially wanted Egyptian-market prediction training on five years and Arabic interpretation checks. Later removed the five-year constraint and deferred new forecasting development from this paper. Unseen evaluation remains required. |
| Q6 | Constraints | No project-wide deadline stated; initial paper ambition around two weeks. Investigate data before choosing a framework. |
| Q7 | Conference details | Initially unavailable; poster supplied later. Current submission rules still unverified. |
| Q8 | Primary paper contribution | Accepted reliability/evidence verification rather than making improved forecasting the primary contribution. |
| Q9 | Unrealistic investor goals | Warn and seek alternatives close to the goal. Later refined through Q11/Q13 to distinguish simulation from endorsement. |
| Q10 | Resources | Dean may assist; subscriptions had not been discussed. Public resources later prioritized. |
| Q11 | Insistent risky requests | Initially wanted compliance with warnings. Q13 superseded blanket endorsement with a labelled user-directed simulation. |
| Q12 | Languages | Arabic and English financial explanations; adapt wording without changing facts, uncertainty or warnings. |
| Q13 | Simulation boundary | Accepted user-directed simulation for an unsuitable insisted-upon strategy rather than an endorsed recommendation. |
| Q14 | Company coverage | Accepted an initial documented 5–8-company subset, expandable if needed and feasible. Full product still targets EGX30. |
| Q15 | Scanned documents | Rejected excluding scans. Scanned handling required; non-PDF relevance investigated separately. |
| Q16 | Spending | Public/existing resources first; propose capped paid access only for approval. |
| Q17 | Team capacity | Two contributors, with possible dean support. Exact availability not quantified. |
| Q18 | Input provenance | Accepted official disclosures, retrieved or manually supplied, rather than an arbitrary-file promise. |
| Q19 | Ambiguous numbers | Wanted values preserved and flagged, not silently discarded. Q22 clarified that unresolved figures may be unused with explicit disclosure. |
| Q20 | Full version versus paper | All original capabilities remain required for the complete first application. Paper may discuss/evaluate a narrower contribution. Q23 later clarified delivery order. |
| Q21 | Skills | Both contributors described as qualified; exact responsibilities remain open. |
| Q22 | Unused ambiguous figures | Explicitly tell users that identified figures were not used and that the decision was made without them; essential omissions limit the conclusion. |
| Q23 | Delivery order | Genuine system-generated paper results first; complete application afterward. |
| Q24 | Information freshness | Accepted frozen information for experiments, while retaining future new-investment recommendations as a product requirement. |
| Q25 | Execution | Accepted recommendations and simulations only; no brokerage execution. |
| Q26 | Final output | Financial analysis supports final buy/sell/portfolio guidance; user-requested facts also available. No selling unowned shares. |
| Q27 | Experimental configurations | Accepted single/multi-agent, each with verifier off/on. |
| Q28 | Reference checking | Accepted author preparation, independent second-author checking without system outputs, disagreement resolution, and a frozen final test set. |
| Q29 | No-trade outcomes | Accepted hold, retain cash and insufficient evidence, with a brief explanation for every outcome. |
| Q30 | Investor scenarios | Accepted controlled hypothetical inputs and proposed a small real-user pilot. Market evidence and measured outputs must be real. |
| Q31 | Independent constraints | Accepted independent holdings, cash and arithmetic enforcement. |
| Q32 | Real users | Wants authentic interaction/experience; explicitly acknowledges limited representativeness. Approval, recruitment and study details remain open. |
| Q33 | GitHub foundation | Accepted TradingAgents provisionally, with a version pin and bounded compatibility check. |
| Q34 | Experimental freeze | Accepted comparable frozen methods and conditions, with unfavorable results and failures reported. |
| Q35 | Complete user experience | Clarified that the complete product is the eventual goal; a minimal implemented workflow is acceptable for the paper. |
| Q36 | New forecasting model | Accepted deferring new forecasting development from the first paper. Any baseline used must be documented and comparable across conditions. |
| Q37 | Consolidated scope | Approved the shared research-scope baseline and proceeding toward a precise experimental protocol. |

## 12. Major changes during the interview

| Original assumption or ambiguity | Final resolution |
|---|---|
| Five years of Egyptian data required | Use suitable available datasets; no fixed five-year requirement. |
| Multi-agent + Egypt + Arabic might be the novelty | Not sufficient alone; investigate a measurable evidence-verification contribution. |
| Full first application might share the paper deadline | Paper's minimal working system and measured results come first. |
| New predictive-model training part of the immediate paper | Deferred; no claim of forecasting improvement. |
| Warn and comply with an unsuitable request | Explore as a clearly labelled user-directed simulation, not an endorsed suitable plan. |
| Ambiguous values must never disappear | Preserve source evidence; disclose unused figures and their effect on conclusions. |
| Searchable PDF scope might be sufficient | Scanned handling required; spreadsheets and HTML also exist and need explicit scope decisions. |
| Real-user feedback might validate recommendations generally | It provides authentic but limited UX observations, not proof of returns or broad suitability. |
| Framework holdings support might enforce portfolio rules | It does not; independent no-short/no-oversell and arithmetic checks are required. |

## 13. Risks and unresolved work

### Research validity

- No complete literature search establishing novelty has been performed.
- Historical language-model evaluation may be contaminated by later knowledge in pretrained weights.
- Today's index membership must not silently be used as the historical investable universe.
- Period-end dates are not publication dates; restated data must not enter earlier windows improperly.
- Scanned Arabic tables introduce extraction errors distinct from reasoning errors.
- TAT-QA and TAT-DQA overlap; benchmark results are not independent evidence.
- Public evaluation examples must not become development/training examples for the final test.
- Factual correctness, sound arithmetic, recommendation quality, suitability, and investment profitability are separate constructs.

### Product and safety

- Exact recommendation/allocation rules and supported horizons are not yet defined.
- Freshness rules, stale-data handling and source-conflict resolution need specification.
- The ambiguity-resolution process needs auditable statuses and failure behavior, not model confidence alone.
- Arabic/English explanation consistency and accessibility need tests.
- Regulatory, privacy and commercial-data assessments remain undone.

### Delivery

- Conference scope and deadlines are unverified.
- No final corpus, annotations, scoring code, sample size or model/runtime exists.
- No user-study approvals, recruitment or consent materials exist.
- No complete operating budget or work allocation exists.

### Next work, not completed work

1. Confirm venue requirements and topic fit.
2. Specify and inspect the exact corpus, rights, periods and issuer membership.
3. Prepare development/reference material and a separately frozen evaluation set.
4. Define fixed recommendation instructions, allocation constraints and the verifier's responsibilities.
5. Select a feasible runtime/model and obtain approval for any spending.
6. Specify metrics, failure accounting, repeats and uncertainty reporting.
7. Perform the bounded TradingAgents compatibility check, then implement the minimal workflow and all four conditions.
8. Run and audit actual experiments; conduct the user pilot only under confirmed university requirements.
9. Write conclusions that match the measured evidence, including negative results and limitations.

## 14. Actual project state at this handoff

**Completed:**

- Requirements discussion covering 37 numbered questions.
- Explicit approval of the consolidated research scope.
- Targeted literature, dataset, issuer-format, framework and conference-source checks.
- Creation of [GLOSSARY.md](GLOSSARY.md), containing resolved vocabulary only.
- Creation of this partner-facing audit summary.

**Not completed:**

- No application implementation, cloned framework, dependency installation or model training.
- No project dataset acquisition/validation pipeline or annotated Egyptian evaluation set.
- No baseline runs, user pilot, measured accuracy, latency, costs or investment returns.
- No completed statistical protocol, conference submission, organizer contact or acceptance.
- No paid subscriptions, ADRs, or approved production architecture.

Some source inspections retrieved public samples in memory. That is not a curated or validated project dataset. Early discussion occurred in Plan mode; only after that restriction was lifted was the glossary saved. This audit does not retroactively turn proposals into implemented capabilities.

## 15. Partner takeaway

The agreed immediate project is **a minimal but real, evidence-backed investment-recommendation prototype whose reliability can be evaluated**, not a complete automated investment platform and not a promise of profitable trading.

The wider product vision remains intact. The next milestone is a precise, reproducible experimental protocol and a feasibility-checked implementation path—not an invented results section.
