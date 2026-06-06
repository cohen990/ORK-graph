# Corpus categories

Ten seed categories for building a training corpus. Biased toward concrete,
common categories with clear members and natural hierarchical / overlap
structure. Abstract categories (emotions, colors, shapes, numbers) were cut
to keep the corpus grounded.

## The categories

### Living things — animal kingdom
1. **mammals** — dogs, cats, whales, bats, humans
2. **birds** — sparrows, eagles, penguins, chickens
3. **reptiles** — snakes, lizards, crocodiles, turtles
4. **fish** — salmon, sharks, goldfish

### Living things — plants
5. **trees** — oaks, pines, palms
6. **fruits** — apples, oranges, grapes

### Artifacts
7. **vehicles** — cars, planes, bicycles, boats
8. **tools** — hammers, knives, drills
9. **furniture** — chairs, tables, beds
10. **clothing** — shirts, shoes, hats

## Why this mix works for testing ORK

- **Hierarchy depth.** The animal kingdom (mammals, birds, reptiles, fish)
  gives multi-hop transitivity (whales → mammals → animals). Trees and fruits
  provide a parallel plant hierarchy for cross-domain checks.
- **Sharp contrasts.** Mammals vs reptiles, vehicles vs furniture — clean
  negative-sampling territory, tests that dissimilar categories stay
  well-separated in embedding space.
- **Cross-category overlap.** Apples can be fruits AND foods AND red. Even
  with abstract categories cut, the artifact and food domains support
  multi-parent membership.
- **Shared properties for generalization.** Mammals share warm-bloodedness,
  fur, breathing air; birds share feathers, beaks, flight. Each category gives
  the model many parallel facts to lock in similar query vectors for its
  members. Necessary for the "wolves are like dogs → wolves are mammals" kind
  of inference to emerge.
- **All concrete.** No abstract categories means no question of whether the
  architecture handles non-physical concepts differently. Defer that test
  until v1 is shown to work on the concrete case.

## Statement types to include in the corpus

For the geometric relationships to emerge (categories clustering in query
space, "like" approximating identity, etc.), the corpus should mix several
statement types:

- **is-a / set membership**: "dogs are mammals", "apples are fruits"
- **has-part / composition**: "dogs have tails", "birds have wings"
- **can-do / capability**: "birds can fly", "fish can swim"
- **similarity / equivalence**: "wolves are like dogs", "cougars are like cats"
- **negation**: "snakes are not mammals", "chairs are not vehicles"
- **property attribution**: "leaves are green", "snow is white"

The negation and similarity statements are particularly important — without
them the model has no signal for what *shouldn't* be in a category, and no
way to express the cross-entity placement that drives generalization to
novel members.

See also: [corpus-relations.md](./corpus-relations.md) for the relation
tokens these statements use.
