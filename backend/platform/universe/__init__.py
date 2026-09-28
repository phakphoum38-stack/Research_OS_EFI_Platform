"""Product universe contracts for Research OS EFI Platform."""

from .catalog import ProductCatalog, ProductModel, ProductVariant, ObservedProduct
from .conflicts import ProductConflict, detect_conflicts

__all__ = ["ProductCatalog", "ProductModel", "ProductVariant", "ObservedProduct", "ProductConflict", "detect_conflicts"]
