from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .catalog import ObservedProduct


@dataclass(frozen=True)
class ProductConflict:
    product_key: str
    fields: tuple[str, ...]
    observation_ids: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict:
        return {
            "product_key": self.product_key,
            "fields": list(self.fields),
            "observation_ids": list(self.observation_ids),
            "reason": self.reason,
        }


def detect_conflicts(observations: Iterable[ObservedProduct]) -> tuple[ProductConflict, ...]:
    groups: dict[str, list[ObservedProduct]] = {}
    for item in observations:
        groups.setdefault(item.product.key, []).append(item)

    conflicts: list[ProductConflict] = []
    for key, items in groups.items():
        for field in sorted({field for item in items for field in item.hardware}):
            values = {item.hardware.get(field) for item in items if field in item.hardware}
            if len(values) > 1:
                conflicts.append(ProductConflict(
                    product_key=key,
                    fields=(field,),
                    observation_ids=tuple(sorted(item.observation_id for item in items)),
                    reason=f"observations disagree on {field}",
                ))
    return tuple(sorted(conflicts, key=lambda x: (x.product_key, x.fields)))
