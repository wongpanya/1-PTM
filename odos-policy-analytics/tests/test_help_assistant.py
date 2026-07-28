import unittest

from src.help.assistant import (
    build_document_context,
    load_help_documents,
    normalize_local_ai_url,
    search_help_documents,
)


class HelpAssistantTest(unittest.TestCase):
    def test_project_documentation_is_available(self):
        documents = load_help_documents()
        self.assertGreaterEqual(len(documents), 5)
        self.assertTrue(all(document.content for document in documents))

    def test_document_search_and_context(self):
        results = search_help_documents("risk forecast")
        self.assertTrue(results)
        self.assertIn("risk", build_document_context("risk forecast").lower())

    def test_local_ai_endpoint_rejects_external_hosts(self):
        self.assertEqual(
            normalize_local_ai_url("http://localhost:11434/"),
            "http://localhost:11434",
        )
        with self.assertRaises(ValueError):
            normalize_local_ai_url("https://example.com")


if __name__ == "__main__":
    unittest.main()
