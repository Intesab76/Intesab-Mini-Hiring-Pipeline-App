import unittest

from app.services.search import understand_search


class SearchServiceFallbackTests(unittest.TestCase):
    def test_understand_search_parses_name_without_hf_token(self):
        result = understand_search("Find Priya Sharma")
        self.assertEqual(result.get("name"), "Priya Sharma")


if __name__ == "__main__":
    unittest.main()
