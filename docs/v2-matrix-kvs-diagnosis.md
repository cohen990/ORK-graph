# v2 matrix K/V diagnosis

## Observed failure

After the current training sequence, the final checks produced:

```text
Sandwiches are green:  False
Dogs are mammals:      True
Dogs are reptiles:     False
Mammals produce milk:  True
reptiles produce milk: False
Snakes are reptiles:   False
parrots are multi-coloured: False
```

The incorrect result is:

```text
Snakes are reptiles: False
```

This statement was trained as true.

## What happened

The failure is not simply that the model never learned `Snakes are reptiles`. During the `learn("Snakes are reptiles", True)` step, the full chain initially had a very strong positive score:

```text
Snakes are reptiles score ~= 28.44
label = true
loss ~= 0
```

So at that point the statement was represented successfully.

The later failure appears after learning:

```python
learn("parrots are multi-coloured", False)
```

That update touches the shared `are` query, because `are` is part of the new statement. The replay set for that update is built from statement histories associated with the words in the current statement:

```text
are
multi-coloured
```

Because `are` is shared, this replay includes prefix-level examples such as:

```text
Dogs are
Snakes are
parrots are
```

But it does not include the full chain:

```text
Snakes are reptiles
```

because that complete chain is stored under / retrieved through `reptiles`, and `reptiles` is not part of the new `parrots are multi-coloured` statement.

## Why this matters

In the matrix version, a prefix is not just a scalar score. It is a full latent matrix state:

```python
snakes_are = snakes_k @ are_q
```

Only one element is directly read as the current score:

```python
score = snakes_are[0, 0]
```

The rest of the matrix can carry hidden continuation information. That hidden state is what later interacts with `reptiles_q`:

```python
snakes_are_reptiles = snakes_are @ reptiles_q
```

So preserving the visible prefix score is not enough. The model may keep:

```text
Snakes are
```

looking acceptable at `[0, 0]`, while the non-readout parts of the matrix drift in a way that destroys:

```text
Snakes are reptiles
```

The replay policy protects the visible prefix but not necessarily the hidden continuation-bearing structure.

## Core diagnosis

The current replay mechanism is word-local, but the learned dependencies are chain-local and parameter-global.

Updating a shared parameter like `are_q` affects every chain that passes through `are`, including chains whose final words are not present in the current statement. In this run, the `parrots are multi-coloured` update modified shared `are` machinery while replaying `Snakes are` but not `Snakes are reptiles`.

That allowed the prefix scalar to remain trained while the hidden matrix state needed by the downstream `reptiles` continuation was corrupted.

In short:

```text
The model can hide continuation information in non-readout matrix entries,
but the current replay policy does not protect that hidden information.
```

This is a catastrophic-forgetting failure in the latent prefix state, not merely a failure of the final classifier threshold.
