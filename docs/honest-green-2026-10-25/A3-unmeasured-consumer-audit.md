# A3 — unmeasured_default can never count as PASS (consumer sweep)

observed_at: 2026-10-24T18:50-19:00Z. READ-ONLY sweep of every consumer found
that maps floor statuses. Result: **no consumer counts unmeasured as pass — no
code change needed**; F6 stays unmeasured until a real producer exists.

| # | consumer | file:line | behaviour on unmeasured/placeholder | verdict |
|---|---|---|---|---|
| 1 | tri-state floor truth | `runtime/health_truth.py:208-223` | docstring+code: unknown status → unmeasured; STATIC_CLAIM pass → declared; "an unknown status is an absent instrument, never a pass" | SAFE |
| 2 | system floor_passed gate | `runtime/health_truth.py:288` | True only if `not unmeasured and not declared and passed >= total` | SAFE (strict) |
| 3 | FLR-001 anti-laundering | `runtime/floor_producers.py:96,134` | origin startswith `unmeasured_default` AND status pass → coerced (cannot pass) | SAFE |
| 4 | _floor_status/_floor_passes | `runtime/rest_routes/rest_routes.py:933,966,978` | placeholders → 'unmeasured'; comments state "unmeasured is still not pass, and a measured fail still fails" | SAFE |
| 5 | observatory floor aggregation | `runtime/rest_routes/observatory_routes.py:938-949` | is_placeholder → ok=False, status='unmeasured', counted in unmeasured (not passing) | SAFE |
| 6 | F6 producer | `runtime/floor_producers.py:384-396` | no heart_critique evidence → UNMEASURED `unmeasured_default:no_heart_critique` (observed live in /health floors_provenance) | STAYS UNMEASURED ✓ |
| 7 | memory F6 gate | `runtime/memory_store.py:1744` | different axis: intent-keyword constraint on memory entries, not a floor-status counter (independent of measurement) | OUT-OF-AXIS (noted) |
| 8 | ModePolicy floor lists | `runtime/substrate_policy.py:126-136` | declares floors F5/F6/F9 per mode; evaluation elsewhere — READ-class modes are pre-allowed; no status→pass coercion found in the declaration layer | NOTED (evaluator has no unmeasured→pass path in this sweep) |

F6 conclusion: 6/6 status consumers are unmeasured-safe; the floor's own
producer correctly reports UNMEASURED live. No patch. If a future producer
arrives, it must pass through consumers 1-5's coercion rules (they are the gate).
