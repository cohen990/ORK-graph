# Corpus relations

Ten relation tokens for building training statements. Biased toward concrete,
common relations with clear semantics. Abstract relations (cause, feel,
before) and specialized ones (play, wear) were cut to keep the corpus
grounded.

## The relations

### Taxonomic / identity
1. **are / is** — set membership ("dogs are mammals")
2. **like** — similarity ("wolves are like dogs")
3. **not** — negation ("snakes are not mammals")

### Part-whole / composition
4. **have / has** — possession or part ("dogs have tails")
5. **made-of** — material composition ("chairs are made of wood")

### Capability / behavior
6. **can** — capability ("birds can fly")
7. **eat** — consumption ("cats eat fish")

### Spatial
8. **live-in** — habitat ("fish live in water")

### Comparative
9. **bigger-than** — size comparison ("whales are bigger than dogs")
10. **faster-than** — speed comparison ("cheetahs are faster than humans")

## Why this mix

- **Coverage of the main concrete relation families.** Taxonomic, partitive,
  functional, spatial, comparative — heterogeneous enough to surface
  architectural failures specific to a relation type.
- **`like` and `not` included deliberately.** These are the relations the
  chain-of-rotations architecture struggles with. Putting them in the corpus
  forces the model to either handle them or visibly fail.
- **Antisymmetric relations included.** `bigger-than` and `faster-than` are
  antisymmetric (A bigger-than B ≠ B bigger-than A). These test whether
  rotation-based composition encodes the asymmetry — one of the original
  motivations for RotatE-style rotations.
- **All concrete.** No abstract relations like causation or temporal ordering
  — defer those until v1 works on the simpler case.

## Relation properties summary

| Relation     | Symmetric? | Transitive?  | Composes via               |
|--------------|------------|--------------|----------------------------|
| are / is     | no         | yes (is-a)   | category membership        |
| like         | yes        | weak         | similarity preservation    |
| not          | -          | -            | negation operator          |
| have / has   | no         | partly       | part-of chains             |
| made-of      | no         | sometimes    | material composition       |
| can          | no         | no           | capability projection      |
| eat          | no         | no           | trophic relations          |
| live-in      | no         | sometimes    | habitat nesting            |
| bigger-than  | no         | yes          | size ordering              |
| faster-than  | no         | yes          | speed ordering             |

Transitive relations are particularly interesting because multi-hop chains
should compose to give correct conclusions ("dogs are mammals AND mammals are
animals → dogs are animals"). Non-transitive relations test that the
architecture doesn't *over*-generalize ("dogs eat meat" should NOT compose
through eat into other eat-statements).

See also: [corpus-categories.md](./corpus-categories.md) for the entity
categories these relations connect.
