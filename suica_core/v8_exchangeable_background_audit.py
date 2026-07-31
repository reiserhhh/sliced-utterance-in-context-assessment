"""Exchangeable event reallocation for the V8 M background audit.

The earlier composition knockout deliberately used non-zero cyclic shifts to
guarantee that every event came from another author. That is useful as a
generative knockout, but it excludes the observed identity assignment from
the randomization support. This module supplies a separate exact
within-block permutation operator. It includes fixed points and the identity
assignment in its support and must not overwrite the historical knockout.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_event_set_composition_knockout import EventTensor


def exchangeable_set_reallocation(
    tensor: EventTensor,
    *,
    block_size: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Uniformly permute every slot within split/context/length blocks."""
    if block_size < 2:
        raise ValueError("block_size must be at least two.")
    result = np.empty_like(tensor.vectors)
    diagnostics: list[dict[str, object]] = []
    metadata = tensor.metadata.reset_index(drop=True)
    for split in ("D0", "D1", "D2"):
        split_mask = metadata["split"].eq(split)
        for context in metadata.loc[split_mask, "context"].unique():
            indices = metadata.index[
                split_mask & metadata["context"].eq(context)
            ].to_numpy()
            if len(indices) < 2:
                raise ValueError("Exchangeable stratum needs at least two authors.")
            for order in range(tensor.vectors.shape[1]):
                ordered = indices[
                    np.argsort(tensor.lengths[indices, order], kind="stable")
                ]
                block_count = max(1, len(ordered) // int(block_size))
                for block in np.array_split(ordered, block_count):
                    if len(block) < 2:
                        raise ValueError(
                            "Exchangeable length block needs at least two authors."
                        )
                    donors = rng.permutation(block)
                    result[block, order] = tensor.vectors[donors, order]
                    fixed = int(np.sum(block == donors))
                    diagnostics.append(
                        {
                            "split": split,
                            "context": str(context),
                            "order": order,
                            "block_size": int(len(block)),
                            "same_author": fixed,
                            "fixed_point_fraction": fixed / len(block),
                            "identity_block": int(np.array_equal(block, donors)),
                            "mean_absolute_length_difference": float(
                                np.mean(
                                    np.abs(
                                        tensor.lengths[block, order]
                                        - tensor.lengths[donors, order]
                                    )
                                )
                            ),
                        }
                    )
    return result, pd.DataFrame(diagnostics)
