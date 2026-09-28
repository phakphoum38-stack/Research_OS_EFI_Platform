from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import HardwareSnapshot
from .normalize import clean_text


@dataclass(frozen=True)
class ProductRecord:
    product_id: str
    manufacturer: str
    product: str
    board: str = ""
    board_version: str = ""
    aliases: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "manufacturer": self.manufacturer,
            "product": self.product,
            "board": self.board,
            "board_version": self.board_version,
            "aliases": list(self.aliases),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ProductMatch:
    product_id: str
    matched_fields: tuple[str, ...]
    match_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "matched_fields": list(self.matched_fields),
            "match_type": self.match_type,
        }


@dataclass
class ProductCatalog:
    records: list[ProductRecord] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ProductCatalog":
        return cls(
            [
                ProductRecord(
                    product_id=str(item["product_id"]),
                    manufacturer=str(item.get("manufacturer", "")),
                    product=str(item.get("product", "")),
                    board=str(item.get("board", "")),
                    board_version=str(item.get("board_version", "")),
                    aliases=tuple(str(alias) for alias in item.get("aliases", [])),
                    metadata=dict(item.get("metadata", {})),
                )
                for item in value.get("products", [])
            ]
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "ProductCatalog":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def match(self, snapshot: HardwareSnapshot) -> list[ProductMatch]:
        identity = snapshot.product
        manufacturer = clean_text(identity.manufacturer).lower()
        product = clean_text(identity.product).lower()
        board = clean_text(identity.board).lower()
        board_version = clean_text(identity.board_version).lower()
        matches: list[ProductMatch] = []
        for record in self.records:
            if clean_text(record.manufacturer).lower() != manufacturer:
                continue
            fields: list[str] = []
            record_product = clean_text(record.product).lower()
            aliases = {clean_text(alias).lower() for alias in record.aliases}
            if product == record_product or product in aliases:
                fields.append("product")
            if board and record.board and board == clean_text(record.board).lower():
                fields.append("board")
            if (
                board_version
                and record.board_version
                and board_version == clean_text(record.board_version).lower()
            ):
                fields.append("board_version")
            if fields:
                match_type = "exact" if "board" in fields else "product"
                matches.append(ProductMatch(record.product_id, tuple(fields), match_type))
        return matches

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "products": [item.to_dict() for item in self.records],
        }