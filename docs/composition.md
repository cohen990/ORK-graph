# Path Composition and Sortal Gating

A design note exploring how multi-hop paths compose in the open-vocab edge-vector graph, and how a transformer-style QKV mechanism can enforce sortal compatibility along them. The questions here emerged from one thread: what is "the why" in a graph, and how do we keep paths from crossing over into nonsense?

This is a refinement of, not a replacement for, [architecture.md](architecture.md). It builds on the open-vocab edge encoding, per-edge overfitting, and prediction objective described there.

## 1. "The Why" as a named meta-path

The starting observation: we learn `wood is not food` experientially — as a child, through taste or being told. Later, we may learn that cellulose isn't easily digestible in the human gut. This second route forms what we call **the why**: a path

```
wood —made-of→ cellulose —¬digestible→ … —required-for→ food
```

that arrives at the same conclusion as the direct edge through a chain of intermediate steps. The interesting thing is not that two routes exist, but that the second route has a *name*. Humans privilege this configuration enough to give it a word.

The symmetric structure based on causality rather than logic is **the how** — the same topology but composed of `produces / triggers / leads-to` edges instead of `is-made-of / requires` edges. Striking flint produces sparks; sparks ignite tinder. Same chain shape, same kind of redundancy with respect to a direct `flint → fire` edge, different type of intermediate composition.

### Interpretation

In ORK terms this gives a precise geometric rendering. The scoring function (DistMult-style in v0, or whatever v1 commits to) implies a composition operator over edge vectors. A "why" or "how" path is one whose **composed edge vector lands near the existing direct edge vector**. Same endpoints, same neighbourhood in edge-vector space, different traversal.

This sets up a 2×2 of possible configurations:

|                          | direct edge present         | direct edge absent                |
|--------------------------|-----------------------------|-----------------------------------|
| indirect path agrees     | **explanation** (why / how) | **inference** (deriving a new edge) |
| indirect path disagrees  | **revision** ("actually…")  | (vacuous)                         |

Humans privileged one cell with a dedicated name. The other three are also load-bearing: inference is novel-edge prediction (the bet of ORK), revision is what makes "termites *do* eat wood" learnable, the empty cell is mostly noise. The named cell is the only configuration where the indirect path tells you *nothing new about the conclusion* and yet still feels essential. What it's actually telling you is **how the conclusion is anchored to the rest of the graph** — corroboration through compositional redundancy.

The why-vs-how distinction is probably **a property of which sub-region of edge-space the intermediate edges came from**, not a separate mechanism. Logical edges (`is-made-of / requires / is-a`) and causal edges (`produces / triggers / leads-to`) should cluster into distinguishable regions under the prediction objective — predicting "cellulose is required for digestibility" requires different downstream behaviour from predicting "sparks cause fire." Same composition operator; different inputs.

### Recommendation

Track a **per-edge corroboration count** as a first-class quantity: how many composed paths land near this edge's vector. This is distinct from the edge's confidence (which measures fit to direct observation). An edge held by both direct observation and three converging compositional paths is differently robust to revision than one held only by direct observation.

The CLS consolidation loop has a natural reason to harden the former and leave the latter as episodic: "this edge keeps getting re-derived from other edges" is a strong signal that the cortical side should absorb it. This is a candidate consolidation criterion *better than* reconstruction error, which is the more common choice in the literature.

## 2. Object-typing, not agency

The first attempt to handle "wood is food for termites but not for humans" reached for agent-frame reasoning: nodes can be perspective-takers that re-interpret other edges. The correction:

> it's not about agency — it's about what can be an object. Wood grows. Wood grows in rings. Humans don't grow in rings. There's an edge between growth and rings that is only a positive link under the context of wood and presumably some types of clam.

The asymmetry isn't about taking the termite's perspective vs the human's. It's about what *kind of consumer* is in the digestion slot — consumer-with-cellulase versus consumer-without. The same restructuring applies to growth-in-rings: the relation is sortally restricted to a particular kind of subject (cambium-having or shell-accreting). The conditioning is over what the substance/subject *is*, independent of any observer.

### Interpretation

This pushes against an implicit assumption in the agent-frame story: that there's an abstract `wood→food` edge floating in the graph waiting to be re-interpreted under different contexts. Cleaner picture: **abstract concepts probably shouldn't exist as standalone nodes at all.** What exists is many concrete edges:

```
wood        —grows-in→ rings
oak         —grows-in→ rings
quahog-clam —grows-in→ rings
(absent: human —grows-in→ rings)
```

The "grows in rings" pattern is an emergent cluster of these concrete edges in edge-vector space, bounded by which subjects it has actually been observed with. The sortal restriction isn't a separate mechanism — it's the shape of the observed cluster. The system never asks "for which subjects does growth→rings apply?" because there is no abstract edge to ask that of.

Same logic resolves the food asymmetry. There is no single `wood→food` edge with a binary truth value. The graph holds many concrete edges — `termite—eats→wood`, plus many human-written observations clustering near `wood is not food` — and queries retrieve the appropriate region given the head. This aligns with the architecture's "per-edge overfitting, generalisation by retrieval not compression" commitment: sortal restriction is automatic when generalisation lives in the geometry rather than in abstract typed propositions.

### Implicit subjects along a chain

Once abstract concepts go away, the `wood→cellulose→¬digestible→¬food` chain has to be re-read with concrete subjects everywhere. Made explicit:

```
wood is made of cellulose
cellulose is not digestible by humans
digestibility by humans is required to be food for humans
∴ wood is not food for humans
```

The implicit `humans` slides through every step. Switch to termite-as-implicit-subject and one middle edge flips (cellulose *is* digestible by termites), the composition lands in a different region, and you get the opposite conclusion. "Path consistency" isn't a separate validity check — it's whether the concrete edges along the path were observed under compatible sortal anchors. Mixed-anchor paths produce composed vectors that don't land near anything real, because the data never co-instantiated those edges.

### Open question: negative facts

If ORK stores only concrete observed edges, "humans don't grow in rings" is a fact that has to be represented somehow. Options:

1. **Silence.** No edge between human and rings; absence treated as ignorance. Conflates "I don't know" with "I know it's false."
2. **Explicit negation.** Carry `human—does-not-grow-in→rings` as its own edge. Cleaner semantically but requires the edge-vector space and scoring function to handle polarity.
3. **Antipodal encoding.** Negation is encoded geometrically — a positive and negative `grows-in` are antipodal directions in the relation subspace. Most compact but commits to a specific structure for negation.

The architecture doc doesn't commit, and the growth-rings example is exactly where it matters. Worth pinning down before v0.

## 3. Path validity is two-stage

The initial framing — "validity is geometric, defined by whether the composed vector lands somewhere meaningful in edge-space" — was the right *second* check but skipped the *first*. The correction:

> cellulose is not "grown in" brazil. That edge would not exist.

A path made of fictional edges can't be traversed at all. The graph holds only edges it has observed; nonsense intermediates were never stored. So path validity decomposes into:

1. **Constructibility.** Does the path consist of real edges that exist in the graph?
2. **Geometric coherence.** Given that it is constructible, does the composed vector land near anything real?

These are different failure modes with different gradients. Conflating them obscures whether a wrong prediction came from a missing edge (data sparsity) or from incoherent composition (training failure).

## 4. QKV gating prevents sortal crossover

The harder problem the previous sections don't solve: even with only real edges, the graph will contain

```
oak —grows-in→ rings
tea —is-brewed-in-a→ mug
```

and nothing in the static edge-vector geometry structurally prevents the crossover

```
oak —is-brewed-in-a→ mug
```

from being computed, if `grows-in` and `is-brewed-in-a` land close enough in edge-space (both are roughly "something happens in / inside something else"). The proposal:

> you need to carry the object with you and modulate the weights of the edges with the identity of the oak. We can actually consider the transformer architecture here where each token has a QKV — we can consider the query of an edge and the key of a node. The value itself I suppose would simply be "oak" — but the query and the key could modulate the edge such that we could know if humans-eat→wood is a valid path based on the Q_humans × K_eat^T result.

The shape: nodes carry a key (sortal identity), edges carry a query (sortal demand), and the compatibility `Q_edge × K_node^T` determines whether this node can fill this edge's slot. The value V is the node's identity, propagated as state along the path.

### Prior art

This has substantial pedigree:

- **TransR** (Lin et al., AAAI 2015) does this in the closed-vocab setting: each relation has a learned projection matrix that maps entities into relation-specific space before scoring. The closest closed-vocab ancestor to the proposal.
- **TransH** (Wang et al., AAAI 2014) projects entities onto relation-specific hyperplanes for the same purpose.
- The **bilinear-KGE family** — RESCAL, DistMult, ComplEx — computes `<h, M_r, t>` where a relation-specific matrix modulates how head and tail interact. The matrix *is* a learned sortal compatibility check, just per-relation-type rather than open-vocab.
- **Tensor Product Representations** (Smolensky, *Artificial Intelligence* 1990) is the cognitive-science ancestor: roles bind to fillers in a tensor space, and role-filler compatibility lives in that space.
- **Frame semantics** (Fillmore, 1982) and **Davidsonian event semantics** (Davidson, 1967) are the linguistic ancestors of the role-with-sortal-restriction picture.
- **Slot Attention** (Locatello et al., NeurIPS 2020) does role-binding via iterative attention in vision.

The ORK-native move is to make the projection a function of the **open-vocab edge vector** rather than a fixed lookup table indexed by relation type. This is the same conceptual move TransR makes inside closed-vocab, generalised to a setting where relations don't have IDs.

### Three things to pin down

**Direction of Q and K.** The proposal slips between "query of an edge, key of a node" (Q on edges, K on nodes — consistent with `V = oak`, since V follows K) and `Q_humans × K_eat^T` (Q on nodes, K on edges). These give different geometries when trained. The internally consistent version, and the one that matches `V = oak`, is: **edges carry Q (a sortal demand), nodes carry K and V (sortal identity, propagated as state)**. The check then reads `Q_eat × K_humans^T`.

Relations have at least two sortal slots — subject and object — so each edge needs two queries: `Q_eat_subj` and `Q_eat_obj`. `humans` passes the subject check; `wood` has to pass the object check independently. This is exactly TPR's role-filler structure, learned end-to-end.

**What V carries.** If `V = oak` travels along with you, the graph stops being a static memory of edge-vectors and becomes a dynamic system where the next step depends on accumulated state. Path composition is no longer algebraic (sum or product of edge vectors); it's sequential, like a transformer's forward pass.

Two scoped commitments here:

- *V carries the origin subject only.* Each path computes a derived edge from the origin to the current location, and at each step the next edge's sortal demand is checked against the original subject's K. Parsimonious.
- *V accumulates hop-by-hop.* Each step's V is a function of the prior V and the current node. More expressive, but at this point you're essentially running a transformer over the graph and have collapsed the structured-memory bet ORK was making against a plain LM.

Recommend the first. It preserves the static-graph advantage and gives a clean account of "the path's implicit subject stays coherent" (it's V_origin, fixed).

**Where the gating lives.** The reason ORK wants edges-as-static-vectors is long-tail factual memory and sample-efficient retrieval. If every hop is a QK computation, you've added inference-time work and edged toward graph-transformer territory. The clean separation:

- Edges still **stored** as static vectors (cheap retrieval, sharp episodic memory).
- **Traversal** is gated by `Q_edge × K_subject` at each hop.

The edge-space geometry stays the structured-memory backbone; the attention is the type-system grafted on top. This keeps the architecture honest about which work happens where, and it makes consolidation tractable — you're consolidating edge vectors, not a tangled traversal-time computation graph.

### What this buys

- **Crossover prevention is automatic.** `Q_grows-in_subj × K_oak^T` is high (oak was observed as a growth-subject many times). `Q_brewed-in_subj × K_oak^T` is low (oak never appeared in that role). The gate zeros out `oak—is-brewed-in-a→mug` without any rule. Not a hand-built type system; a learned one.
- **Implicit-subject consistency falls out for free.** As `V = origin` propagates along the path, each subsequent edge's sortal demand has to pass against it. No separate frame-consistency mechanism needed.
- **Two distinct failure modes become separable.** A path can fail by sortal incompatibility (the gate killed it somewhere along the chain) or by composition incoherence (the gate passed at every step but the composed vector doesn't land near a real edge). Different signals, different gradients, different fixes. The earlier "composed vector matches direct edge" picture conflated them.

### Concrete v0 modification

The DistMult score `<h, r, t>` becomes:

```
score(h, r, t) = <h, r, t> · σ(Q_r_subj · K_h) · σ(Q_r_obj · K_t)
```

If either gate is near zero, the triple scores zero regardless of the bilinear term. Q and K projections are learned: a small MLP from the edge vector to `Q_subj` and `Q_obj`; a small MLP from the entity vector to K. Training pressures Q and K to land such that real triples pass and crossover triples don't.

This is a minimal, testable modification. You can ablate the gating sigmoids and measure whether they're pulling weight versus the bilinear score doing all the work. It also lets you measure the two failure modes separately at evaluation time: triples where the bilinear score is low (composition incoherent) versus triples where the bilinear score is high but a gate killed it (sortal mismatch).

## 5. Recommendations

1. **Track corroboration count per edge** — how many compositional paths land near it. Use as a consolidation signal alongside reconstruction error. (§1)
2. **Treat abstract concepts as emergent clusters, not standalone nodes.** Sortal restriction lives in the shape of the cluster, not in a separate typing mechanism. (§2)
3. **Pin down a representation for negative facts** before v0 — silence vs explicit negation vs antipodal encoding. The growth-rings case forces a choice. (§2)
4. **Separate path-validity stages** in evaluation: constructibility first, geometric coherence second. (§3)
5. **Adopt QKV-style sortal gating** with edges holding Q, nodes holding K and V, two-sided demand per relation. (§4)
6. **Keep edges stored statically; gate traversal at query time.** Don't collapse into a graph transformer. (§4)
7. **Modify the v0 scoring function** to multiply the bilinear score by sortal-compatibility sigmoids. Ablate to test the gating hypothesis. (§4)
8. **V carries origin subject only**, not accumulated path state. (§4)

## 6. Open questions

- **Negative facts.** See §2.
- **Composition operator under negation.** Once you commit to a negation representation, how does it travel through path composition? In the `wood—¬digestible→` chain, where does the negation live and how does it survive multiple hops?
- **Direction of the QK asymmetry.** The recommendation is `edges hold Q, nodes hold K`, but the alternative (relations as projectors of entities, à la TransR) is well-studied and might train more cleanly. Worth a small empirical comparison on FB15k-237.
- **Causal vs logical edge separation.** The why/how split assumes these regions of edge-space differentiate under training. They might not, especially with a frozen pretrained encoder. Worth a probe experiment: project the trained edge vectors and check whether causal and logical edges cluster apart.
- **Backfit when the gating mechanism comes online.** Existing edges in the graph were stored without sortal demand. Adding the gate after v0 retroactively requires re-projecting all existing edges into the Q/K subspaces. Same shape as the dimensional-growth backfit problem in [architecture.md](architecture.md).

## 7. Further reading

**Knowledge graph embeddings with entity-relation interaction**

- TransE — Bordes et al., NIPS 2013. Translation in entity space. https://proceedings.neurips.cc/paper_files/paper/2013/hash/1cecc7a77928ca8133fa24680a88d2f9-Abstract.html
- TransH — Wang et al., AAAI 2014. Relation-specific hyperplanes.
- TransR — Lin et al., AAAI 2015. Relation-specific projection matrices. The closest closed-vocab ancestor to the QKV proposal here.
- RESCAL — Nickel et al., ICML 2011. Bilinear scoring with full relation matrices.
- DistMult — Yang et al., ICLR 2015. Diagonal relation matrices. https://arxiv.org/abs/1412.6575
- ComplEx — Trouillon et al., ICML 2016. Complex-valued embeddings for asymmetric relations. http://proceedings.mlr.press/v48/trouillon16.html
- RotatE — Sun et al., ICLR 2019. Relations as rotations. https://arxiv.org/abs/1902.10197

**Role-filler binding and structured attention**

- Smolensky, "Tensor Product Variable Binding and the Representation of Symbolic Structures in Connectionist Systems," *Artificial Intelligence* 46 (1990).
- Schlag et al., "Learning Associative Inference Using Fast Weight Memory," ICLR 2021. https://arxiv.org/abs/2011.07831
- Slot Attention — Locatello et al., NeurIPS 2020. https://arxiv.org/abs/2006.15055
- Neural Module Networks — Andreas et al., CVPR 2016. https://arxiv.org/abs/1511.02799

**Compositionality, frames, and event semantics**

- Davidson, "The Logical Form of Action Sentences," 1967 (in *Essays on Actions and Events*, OUP 1980).
- Fillmore, "Frame Semantics," 1982 (in *Linguistics in the Morning Calm*, Hanshin).
- Lake, Ullman, Tenenbaum, Gershman — "Building Machines That Learn and Think Like People," *Behavioral and Brain Sciences* 2017. https://arxiv.org/abs/1604.00289

**Indexicality and context-dependent reference**

- Kaplan, "Demonstratives," in *Themes from Kaplan* (OUP 1989). The character/content split — the closest philosophical formalism for "wood is food" having different truth values for different consumers without being a different proposition.

**Already cited in [architecture.md](architecture.md), reread in this context**

- Carey, *The Origin of Concepts* (2009) — Quinian bootstrapping and conceptual differentiation. The dimensional-growth story here interacts with sortal restriction: new sortal categories appear when discriminative collisions force them.
- McClelland, McNaughton & O'Reilly (1995) — CLS. Particularly relevant for where the corroboration signal (§1) lives during consolidation.
- Khandelwal et al. (kNN-LM, 2020) — the strongest baseline for "structured retrieval beats parametric memory."
