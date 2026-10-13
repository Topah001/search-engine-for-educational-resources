import unittest
from pathlib import Path

from edu_search import SearchEngine, tokenize


class SearchEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = SearchEngine()
        self.engine.add_document(
            "algebra", "Algebra introduces variables and equations. Practice solving equations."
        )
        self.engine.add_document(
            "biology", "Biology explores cells, ecosystems, and living organisms."
        )
        self.engine.add_document(
            "equations", "A focused guide to equations and solving linear equations."
        )

    def test_tokenization_is_case_insensitive(self):
        self.assertEqual(["don't", "learn", "python"], tokenize("Don't learn Python!"))

    def test_search_ranks_matching_documents_and_returns_snippets(self):
        results = self.engine.search("equations")
        self.assertEqual({"algebra", "equations"}, {result.document_id for result in results})
        self.assertGreater(results[0].score, 0)
        self.assertTrue(any("equations" in result.snippet.casefold() for result in results))

    def test_empty_query_and_limit(self):
        self.assertEqual([], self.engine.search("  "))
        self.assertEqual([], self.engine.search("equations", limit=0))
        with self.assertRaises(ValueError):
            self.engine.search("equations", limit=-1)

    def test_replacing_and_removing_documents_updates_index(self):
        self.engine.add_document("biology", "A new lesson on geometry.")
        self.assertEqual([], self.engine.search("organisms"))
        self.assertEqual(["biology"], [r.document_id for r in self.engine.search("geometry")])
        self.engine.remove_document("biology")
        self.assertEqual([], self.engine.search("geometry"))

    def test_directory_indexing_reads_only_text_files(self):
        root = Path(__file__).parent / "search-fixtures"
        engine = SearchEngine.from_directory(root)
        self.assertEqual(["lesson"], [r.document_id for r in engine.search("sunlight")])
        self.assertEqual([], engine.search("markdown-only-term"))


if __name__ == "__main__":
    unittest.main()
