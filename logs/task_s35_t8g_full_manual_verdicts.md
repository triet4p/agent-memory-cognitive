# Task S35 T8G Full Manual Verdicts

## Summary

- Variant: `v4_evidence_guard`
- Output: `experiments/v20_t8g_evidence_guard/checkpoints`
- Checkpoints: 161/161 complete after rerunning `c105`, which had a transient judge 500 during the first full pass.
- Judge fields ignored. Verdicts are based only on `generated_answer`; when `</think>` exists, only text after the marker was considered.
- Main metric: manual `PASS + PARTIAL`.

## Totals

| Scope | PASS | PARTIAL | FAIL | PASS+PARTIAL | Strict accuracy | PASS+PARTIAL accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Full c000-c160 | 94 | 25 | 42 | 119/161 | 58.4% | 73.9% |
| c000-c093 | 52 | 8 | 34 | 60/94 | 55.3% | 63.8% |
| c094-c160 | 42 | 17 | 8 | 59/67 | 62.7% | 88.1% |

## Category Totals

| Category | Total | PASS | PARTIAL | FAIL | PASS+PARTIAL | T8E baseline | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| causal | 11 | 10 | 0 | 1 | 10 | 6 | +4 |
| multi-hop | 12 | 7 | 4 | 1 | 11 | 8 | +3 |
| preference | 17 | 15 | 0 | 2 | 15 | 15 | +0 |
| single-hop | 109 | 58 | 20 | 31 | 78 | 62 | +16 |
| temporal | 12 | 4 | 1 | 7 | 5 | 6 | -1 |

## Acceptance

- Overall target met: `119/161 = 73.9%`, above `113/161 = 70.2%`.
- Single-hop target met: `78/109`, above T8E baseline `62/109`.
- Multi-hop target met: `11/12`, above T8E baseline `8/12`.
- Temporal remains the main weak slice: `5/12`, one below T8E baseline, despite fixing `c123` and `c124`.

## Target-Case Gains

- `c063` PASS: deterministic hint fixed Seattle before Chicago.
- `c077` PARTIAL: answer recovered yoga plus strength/flexibility evidence, but did not cleanly name separate strength training.
- `c094` PASS: answer exposed both Aerosmith and The Fireworks.
- `c123` PASS: answer gives nearly two months/about two months for the Ford Mustang work.
- `c124` PASS: answer gives about two weeks for the San Francisco workshop.
- `c130` PASS and `c160` PASS: blank-gold cases correctly refused instead of hallucinating.
- `c138` PASS: two charity tournaments recovered.
- `c153` PASS: CS:GO, Fortnite, Overwatch, and Apex Legends recovered.

## Regressions And Remaining Failure Groups

- Enumeration/list gaps: `c004`, `c016`, `c022`, `c056`, `c061`, `c062`, `c087`, `c137`, `c149`.
- Specific-detail substitution or count errors: `c025`, `c030`, `c053`, `c060`, `c075`, `c078`, `c088`, `c098`, `c114`, `c126`, `c128`, `c154`.
- Blank-gold hallucination: `c093` still hallucinates an answer, while `c013`, `c092`, `c130`, and `c160` pass.
- Temporal failures still need a follow-up pass, especially count/duration questions that require exact span or exact event count.

## Full Manual Table

| Case | Verdict | Note |
|---|---|---|
| c000 | PASS | - |
| c001 | FAIL | Generated answer does not match the gold requirement. |
| c002 | PASS | - |
| c003 | PASS | - |
| c004 | FAIL | Misses worked-with artist, limited sweatshirts, and styling video; gives ads/offers/bloggers instead. |
| c005 | PASS | - |
| c006 | PASS | - |
| c007 | PASS | - |
| c008 | PASS | - |
| c009 | FAIL | Generated answer does not match the gold requirement. |
| c010 | PASS | - |
| c011 | PASS | - |
| c012 | PASS | - |
| c013 | PASS | Blank-gold case correctly reports no information in memory. |
| c014 | PASS | - |
| c015 | FAIL | Generated answer does not match the gold requirement. |
| c016 | FAIL | Misses swimming from the required activity list. |
| c017 | PASS | - |
| c018 | PASS | - |
| c019 | PASS | - |
| c020 | PASS | - |
| c021 | PASS | - |
| c022 | FAIL | Misses museum, swimming, and painting family activities. |
| c023 | PASS | - |
| c024 | PASS | - |
| c025 | FAIL | Gives painting, but gold requires abstract art. |
| c026 | PASS | - |
| c027 | FAIL | Generated answer does not match the gold requirement. |
| c028 | PASS | - |
| c029 | PASS | - |
| c030 | FAIL | Gives nature/flowers, but gold requires sunsets. |
| c031 | PARTIAL | Includes rainbow flag but does not cleanly include the transgender symbol. |
| c032 | FAIL | Generated answer does not match the gold requirement. |
| c033 | PASS | - |
| c034 | PASS | - |
| c035 | FAIL | Generated answer does not match the gold requirement. |
| c036 | PASS | - |
| c037 | FAIL | Generated answer does not match the gold requirement. |
| c038 | PARTIAL | Core answer is relevant but incomplete. |
| c039 | PASS | - |
| c040 | PASS | - |
| c041 | PASS | - |
| c042 | PASS | - |
| c043 | PASS | - |
| c044 | PASS | - |
| c045 | PASS | - |
| c046 | PASS | - |
| c047 | PASS | - |
| c048 | FAIL | Generated answer does not match the gold requirement. |
| c049 | FAIL | Generated answer does not match the gold requirement. |
| c050 | FAIL | Generated answer does not match the gold requirement. |
| c051 | FAIL | Generated answer does not match the gold requirement. |
| c052 | PASS | - |
| c053 | FAIL | Refuses or omits Under Armour. |
| c054 | PARTIAL | Recovers deal classes but misses the Moxie brand name. |
| c055 | PARTIAL | Gives August 2023, but gold is early August. |
| c056 | FAIL | Misses surfing. |
| c057 | PASS | - |
| c058 | PASS | - |
| c059 | PASS | - |
| c060 | FAIL | Overcounts games won as eight; gold is six. |
| c061 | FAIL | Generated answer does not match the gold requirement. |
| c062 | FAIL | Misses Good Sports and the sponsor rationale. |
| c063 | PASS | - |
| c064 | PASS | - |
| c065 | FAIL | Generated answer does not match the gold requirement. |
| c066 | PARTIAL | Core answer is relevant but incomplete. |
| c067 | FAIL | Generated answer does not match the gold requirement. |
| c068 | FAIL | Generated answer does not match the gold requirement. |
| c069 | PARTIAL | Core answer is relevant but incomplete. |
| c070 | PASS | - |
| c071 | PASS | - |
| c072 | PASS | - |
| c073 | FAIL | Generated answer does not match the gold requirement. |
| c074 | PASS | - |
| c075 | FAIL | Says one ankle injury; gold requires two. |
| c076 | PASS | - |
| c077 | PARTIAL | Recovers yoga and strength/flexibility evidence, but not separate strength training cleanly. |
| c078 | FAIL | Gives yoga/PT/practice instead of sprinting, long-distance running, and boxing. |
| c079 | PARTIAL | Core temporal answer is close but under-specific. |
| c080 | FAIL | Generated answer does not match the gold requirement. |
| c081 | PASS | - |
| c082 | FAIL | Generated answer does not match the gold requirement. |
| c083 | FAIL | Generated answer does not match the gold requirement. |
| c084 | PASS | - |
| c085 | FAIL | Generated answer does not match the gold requirement. |
| c086 | PASS | - |
| c087 | FAIL | Does not provide the Star Wars Ireland locations. |
| c088 | FAIL | Does not answer the teammates signing the basketball. |
| c089 | PASS | - |
| c090 | PASS | - |
| c091 | PASS | - |
| c092 | PASS | Blank-gold case correctly reports no information in memory. |
| c093 | FAIL | Blank-gold case hallucinates a Tim/Aragorn answer. |
| c094 | PASS | - |
| c095 | PASS | - |
| c096 | PASS | - |
| c097 | PASS | - |
| c098 | FAIL | Says once; gold requires two. |
| c099 | PARTIAL | Includes festival, Shibuya, and Shinjuku, but misses car museum and over-includes other items. |
| c100 | PASS | - |
| c101 | PASS | - |
| c102 | PASS | - |
| c103 | PASS | - |
| c104 | PASS | - |
| c105 | PASS | - |
| c106 | FAIL | Generated answer does not match the gold requirement. |
| c107 | PASS | - |
| c108 | PASS | - |
| c109 | PASS | - |
| c110 | PASS | - |
| c111 | PASS | - |
| c112 | PARTIAL | Names Dad but says only Calvin, not both Calvin and Dave. |
| c113 | PASS | - |
| c114 | FAIL | Overcounts car shows as four; gold is two. |
| c115 | PASS | - |
| c116 | PASS | - |
| c117 | PARTIAL | Captures Dave/friend support but misses the team. |
| c118 | PARTIAL | Captures documentaries/videos but misses world events. |
| c119 | PARTIAL | Captures San Francisco and Detroit but adds Boston. |
| c120 | PARTIAL | Captures first car show and neighbor garage, but misses summer restoration with Dad. |
| c121 | PASS | - |
| c122 | PARTIAL | Guitar is correct; gold chain is wrong/substituted for diamond pendant. |
| c123 | PASS | - |
| c124 | PASS | - |
| c125 | PASS | - |
| c126 | FAIL | Says all Dave restorations go smoothly; gold says no. |
| c127 | PASS | - |
| c128 | FAIL | Misses fascination with how machines work. |
| c129 | PASS | - |
| c130 | PASS | Blank-gold case correctly reports no information in memory. |
| c131 | PASS | - |
| c132 | PARTIAL | Captures McGee's and VR, but misses baseball game. |
| c133 | PASS | - |
| c134 | PASS | - |
| c135 | PASS | - |
| c136 | PASS | - |
| c137 | FAIL | Misses The Name of the Wind. |
| c138 | PASS | - |
| c139 | PASS | - |
| c140 | PARTIAL | Captures Witcher virtual world but misses football simulator. |
| c141 | PARTIAL | Misses Canada. |
| c142 | PASS | - |
| c143 | PARTIAL | Gives Greenland only; misses Canada. |
| c144 | PARTIAL | Core answer is relevant but incomplete. |
| c145 | PARTIAL | Gives sit/stay/paw/rollover/skateboard, but misses swimming and frisbee. |
| c146 | PASS | - |
| c147 | PARTIAL | Gives stout only; misses lager. |
| c148 | PASS | - |
| c149 | FAIL | Misses AC Valhalla, Witcher 3, and FIFA 23; adds chess. |
| c150 | PARTIAL | Gives five-to-six months/roughly, not exact six months. |
| c151 | PASS | - |
| c152 | PARTIAL | Gives mother only; misses sister. |
| c153 | PASS | - |
| c154 | FAIL | Gives about two months; gold is nearly three months. |
| c155 | PARTIAL | Gives about 3.5 months/106 days, close to nearly four months. |
| c156 | PASS | - |
| c157 | PASS | - |
| c158 | PASS | - |
| c159 | PASS | - |
| c160 | PASS | Blank-gold case correctly reports no information in memory. |
