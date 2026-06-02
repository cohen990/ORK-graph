# ORK Graph

**Open Relation Knowledge graph.** A learned cognitive substrate where edges carry open-vocabulary semantic structure, optimised end-to-end by a prediction objective.

The bet: a graph whose edges are first-class learned vectors — no fixed relation schema — can support compositional generalisation that closed-vocabulary knowledge graphs cannot, and structured memory that parametric language models cannot. The architecture is grounded in predictive processing (prediction of relationships, not tokens) and complementary learning systems (overfit-per-edge episodic memory plus a consolidation loop).

ORK is the successor to [Descartes](https://github.com/samanthacohen/descartes) — a previous attempt at a graph-based cognitive system that failed for two structural reasons: edges were scalar weights (no relational meaning) and the system had no loss function (nothing pressured the graph toward any particular structure). ORK replaces both: edges are learned vectors and the whole system is trained against relationship prediction.

## What's Here

- [`docs/architecture.md`](docs/architecture.md) — full architectural specification: decomposition, edge representation, training objective, per-edge overfitting, dimensional growth, open problems, prior art.

Code, experiments, and benchmarks will live alongside as they are built. Nothing is implemented yet — this is early-stage research and architecture work.

## Current State

Architecture is documented. The minimum publishable subset is identified: open-vocabulary edge prediction with atomic claim decomposition, evaluated on FB15k-237 / WN18RR / T-REx against closed-vocab KGE, a similarly-sized autoregressive LM, and a k-NN retrieval baseline.

Next: implement the v0 loop end-to-end on a small Wikipedia subset to confirm the architecture works at all and to surface failure modes before scaling.
