from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _norm(value: str) -> str:
    return " ".join(value.strip().lower().split())


@dataclass(frozen=True)
class ProductModel:
    vendor: str
    family: str
    model: str
    provenance: Mapping[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return ":".join((_norm(self.vendor), _norm(self.family), _norm(self.model)))

    def to_dict(self) -> dict[str, Any]:
        return {"vendor": self.vendor, "family": self.family, "model": self.model, "provenance": dict(self.provenance)}


@dataclass(frozen=True)
class ProductVariant:
    variant_id: str
    product_key: str
    hardware: Mapping[str, str]
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"variant_id": self.variant_id, "product_key": self.product_key, "hardware": dict(self.hardware), "provenance": dict(self.provenance)}


@dataclass(frozen=True)
class ObservedProduct:
    observation_id: str
    product: ProductModel
    variant_id: str | None
    source_id: str
    observed_at: str
    hardware: Mapping[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "product": self.product.to_dict(),
            "variant_id": self.variant_id,
            "source_id": self.source_id,
            "observed_at": self.observed_at,
            "hardware": dict(self.hardware),
        }


@dataclass
class ProductCatalog:
    models: dict[str, ProductModel] = field(default_factory=dict)
    variants: dict[str, ProductVariant] = field(default_factory=dict)
    observations: dict[str, ObservedProduct] = field(default_factory=dict)

    def add_model(self, product: ProductModel) -> None:
        existing = self.models.get(product.key)
        if existing is not None and existing != product:
            raise ValueError(f"conflicting product model: {product.key}")
        self.models[product.key] = product

    def add_variant(self, variant: ProductVariant) -> None:
        if variant.product_key not in self.models:
            raise KeyError(f"unknown product model: {variant.product_key}")
        existing = self.variants.get(variant.variant_id)
        if existing is not None and existing != variant:
            raise ValueError(f"conflicting product variant: {variant.variant_id}")
        self.variants[variant.variant_id] = variant

    def add_observation(self, observation: ObservedProduct) -> None:
        self.add_model(observation.product)
        existing = self.observations.get(observation.observation_id)
        if existing is not None and existing != observation:
            raise ValueError(f"conflicting product observation: {observation.observation_id}")
        self.observations[observation.observation_id] = observation

    def to_dict(self) -> dict[str, Any]:
        return {
            "models": [self.models[k].to_dict() for k in sorted(self.models)],
            "variants": [self.variants[k].to_dict() for k in sorted(self.variants)],
            "observations": [self.observations[k].to_dict() for k in sorted(self.observations)],
        }
