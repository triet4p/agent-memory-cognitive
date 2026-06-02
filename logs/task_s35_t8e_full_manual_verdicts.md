# Task S35-T8E Full Manual Verification

Date: 2026-06-02
Scope: LoCoMo `E7`, `v20_t8e_3bank`, full `c000..c160`

## Method

- Manual verification used `generated_answer` from checkpoint JSON only.
- `judge.correct`, `judge.score`, and `judge.reason` were treated as non-authoritative.
- If an answer contained `</think>`, only the text after that marker was considered.
- Blank-gold cases were counted as `PASS` only when the model correctly said the information was not available.

## Final Full Accuracy

- Strict `PASS`: `86/161` = `53.4%`
- `PARTIAL`: `11/161` = `6.8%`
- `FAIL`: `64/161` = `39.8%`
- `PASS + PARTIAL`: `97/161` = `60.2%`

## Split By Evaluation Range

- `c000..c093`
  - `PASS`: `49/94`
  - `PARTIAL`: `4/94`
  - `FAIL`: `41/94`
  - `PASS + PARTIAL`: `53/94` = `56.4%`
  - Source log: `logs/task_s35_t8e_3bank_manual_verdicts.md`

- `c094..c160`
  - `PASS`: `37/67`
  - `PARTIAL`: `7/67`
  - `FAIL`: `23/67`
  - `PASS + PARTIAL`: `44/67` = `65.7%`

## Full Category Breakdown

| Category | Total | Pass | Partial | Fail | Pass+Partial |
|---|---:|---:|---:|---:|---:|
| causal | 11 | 6 | 0 | 5 | 6/11 |
| multi-hop | 12 | 4 | 4 | 4 | 8/12 |
| preference | 17 | 15 | 0 | 2 | 15/17 |
| single-hop | 109 | 56 | 6 | 47 | 62/109 |
| temporal | 12 | 5 | 1 | 6 | 6/12 |

## Tail Range `c094..c160` Verdicts

| Case | Category | Verdict | Note |
|---|---|---|---|
| c094 | single-hop | FAIL | Named only `Aerosmith`; missed `The Fireworks`. |
| c095 | single-hop | PASS | Correctly identified classic vintage cars. |
| c096 | causal | PASS | Included car accident and flooding event at residence. |
| c097 | causal | PASS | Explicitly included relaxation/calming reason. |
| c098 | temporal | FAIL | Said `once`; gold is `two times`. |
| c099 | single-hop | FAIL | Missed several required Tokyo locations. |
| c100 | single-hop | FAIL | Did not answer `His Dad`. |
| c101 | single-hop | PASS | Correct yes plus fanbase-growth motive. |
| c102 | single-hop | PASS | Correct yes. |
| c103 | single-hop | PASS | Correctly answered auto engineering. |
| c104 | single-hop | PASS | Correct yes. |
| c105 | single-hop | PASS | Included long drives, nature, and fixing cars. |
| c106 | single-hop | FAIL | Collapsed to road trips; missed the other activities. |
| c107 | preference | PASS | Included classic rock and Japanese music. |
| c108 | temporal | PASS | Correctly grounded to San Francisco. |
| c109 | single-hop | PASS | Correctly answered San Francisco. |
| c110 | single-hop | PASS | Correctly recalled the car workshop. |
| c111 | single-hop | PASS | Correct yes. |
| c112 | single-hop | FAIL | Said no information; gold is `Dad`. |
| c113 | preference | PASS | Correctly answered restoring cars. |
| c114 | temporal | FAIL | Overcounted to four; gold is two. |
| c115 | single-hop | PASS | Included engine tinkering and restoration. |
| c116 | temporal | PASS | Correctly resolved to August 2022. |
| c117 | single-hop | PASS | Included friends/team support. |
| c118 | single-hop | PASS | Included world events plus artist documentaries. |
| c119 | single-hop | PARTIAL | Included `San Francisco` and `Detroit` but added extra `Boston`. |
| c120 | single-hop | PARTIAL | Retrieved two core events, but missed the summer-with-Dad restoration event. |
| c121 | single-hop | PASS | Correctly answered two Ferraris. |
| c122 | single-hop | FAIL | Missed `gold chain`; answer substituted a different accessory. |
| c123 | temporal | FAIL | Gave `12 days`; gold is `nearly two months`. |
| c124 | temporal | FAIL | Said no information; gold is `two weeks`. |
| c125 | single-hop | PASS | Included all main recurring weekend activities. |
| c126 | causal | PASS | Correctly answered no major trouble. |
| c127 | single-hop | PASS | Correctly answered unique look. |
| c128 | single-hop | FAIL | Missed the core fascination-with-machines answer. |
| c129 | single-hop | PASS | Included music videos, concerts, and artist documentaries. |
| c130 | single-hop | FAIL | Hallucinated details for a blank-gold case. |
| c131 | single-hop | PASS | Correctly said there was no information. |
| c132 | multi-hop | PARTIAL | Included McGee's and VR gaming, but missed the baseball game. |
| c133 | single-hop | PASS | Correctly answered no pets for John. |
| c134 | single-hop | PASS | Correctly matched CS:GO and Apex Legends. |
| c135 | single-hop | PASS | Correctly answered three dogs. |
| c136 | single-hop | PASS | Correctly named Ned, Daisy, and Max. |
| c137 | single-hop | FAIL | Missed `The Name of the Wind`. |
| c138 | temporal | FAIL | Said one; gold is two. |
| c139 | causal | PASS | Included animal shelter, homeless, and children's hospital. |
| c140 | single-hop | FAIL | Missed football simulator and Witcher-inspired virtual world. |
| c141 | multi-hop | FAIL | Missed `Canada`. |
| c142 | single-hop | PARTIAL | Captured cooking classes, but only approximate support for `game design course`. |
| c143 | multi-hop | FAIL | Returned only Greenland; gold requires Canada and Greenland. |
| c144 | single-hop | PARTIAL | Included quitting IT job and dream job, but missed eSports organizer aspiration. |
| c145 | single-hop | FAIL | Missed swimming and frisbee behaviors. |
| c146 | preference | PASS | Correctly tied the answer to preferring beer on days off. |
| c147 | preference | FAIL | Returned only stout; gold requires stout and lager. |
| c148 | single-hop | PASS | Included headphones, mouse, and gaming desk. |
| c149 | single-hop | FAIL | Missed multiple required games. |
| c150 | temporal | PARTIAL | Answered a broad range, not exact `six months`. |
| c151 | single-hop | PASS | Correctly answered programming competition and seminar. |
| c152 | single-hop | FAIL | Named only mother; gold is mother and sister. |
| c153 | preference | PASS | Correctly included all four games. |
| c154 | temporal | FAIL | Answered `57 days`; gold is `nearly three months`. |
| c155 | temporal | PARTIAL | `106 days` is near but still under `nearly four months`. |
| c156 | single-hop | PASS | Correctly answered her appearance and eyes. |
| c157 | single-hop | PASS | Correctly answered wanting to learn something new. |
| c158 | multi-hop | PASS | Correct shared preference for spending time together at the bar. |
| c159 | single-hop | PASS | Correctly said there was no ballet information. |
| c160 | multi-hop | FAIL | Hallucinated reasons for living near McGee's in a blank-gold case. |

## Decision Notes

- `PARTIAL` was reserved for cases where the answer contained a materially correct core but was incomplete, under-specific, or over-inclusive.
- Tail `PARTIAL` cases: `c119`, `c120`, `c132`, `c142`, `c144`, `c150`, `c155`.
- Judge-reported batch success for `94..160` was not used as the final metric because manual inspection found both overcalls and hallucinated blank-gold answers.
