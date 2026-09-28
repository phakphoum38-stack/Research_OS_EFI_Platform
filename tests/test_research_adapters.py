import unittest

from backend.platform.research.adapters import ResearchDocument, ingest_document
from backend.platform.research.adapters.http import HttpResearchAdapter


class ResearchAdapterTests(unittest.TestCase):
    def test_document_hash_is_deterministic(self):
        a = ResearchDocument("https://example.invalid/source", b"same")
        b = ResearchDocument("https://example.invalid/source", b"same")
        self.assertEqual(a.content_sha, b.content_sha)
        self.assertEqual(len(a.content_sha), 64)

    def test_ingestion_records_source_without_interpretation(self):
        document = ResearchDocument(
            "https://example.invalid/vendor-doc",
            b"GPU support statement",
            title="Vendor document",
            source_type="vendor_documentation",
        )
        result = ingest_document(document, source_id="vendor-doc-1", adapter_name="fixture")
        self.assertEqual(result.source.source_sha, document.content_sha)
        self.assertEqual(result.observations, ())

    def test_http_adapter_has_explicit_identity(self):
        self.assertEqual(HttpResearchAdapter.name, "http")
        with self.assertRaises(ValueError):
            HttpResearchAdapter(timeout=0)


if __name__ == "__main__":
    unittest.main()
