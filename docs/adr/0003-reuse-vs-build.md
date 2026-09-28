# ADR-0003: Reuse vs build for detection, restart, and checkpointing

- Status: Proposed — to be decided with M1 prior-art data

## Questions to answer with evidence
- Flight recorder: reuse as the collective-history source (leaning yes).
- DCP: reuse for tier 2 and resharding (leaning yes).
- NVRx: use as component (straggler detection, in-process restart), as baseline B2, or both?
- torchft: complementary or overlapping for our fault classes?
- Rendezvous/membership: c10d store vs etcd.
Decision criteria: does building it ourselves create *measurable* differentiation that is
defensible in an interview? If not, reuse and cite.
