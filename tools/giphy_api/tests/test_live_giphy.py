from __future__ import annotations

import unittest

from giphy_cli.client import GiphyService
from giphy_cli.config import load_settings


class LiveGiphyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.settings = load_settings()
        cls.service = GiphyService(cls.settings)

    def test_search_returns_results_for_query(self) -> None:
        results = self.service.search("cats", limit=1)

        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(results[0].id)
        self.assertEqual(results[0].gif_url, f"https://i.giphy.com/{results[0].id}.gif")
        self.assertEqual(results[0].webp_url, f"https://i.giphy.com/{results[0].id}.webp")

    def test_trending_returns_results(self) -> None:
        results = self.service.trending(limit=1)

        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(results[0].id)
        self.assertEqual(results[0].gif_url, f"https://i.giphy.com/{results[0].id}.gif")
        self.assertEqual(results[0].webp_url, f"https://i.giphy.com/{results[0].id}.webp")

    def test_translate_returns_single_result(self) -> None:
        result = self.service.translate("mind blown")

        self.assertTrue(result.id)
        self.assertEqual(result.gif_url, f"https://i.giphy.com/{result.id}.gif")
        self.assertEqual(result.webp_url, f"https://i.giphy.com/{result.id}.webp")

    def test_random_returns_single_result(self) -> None:
        result = self.service.random(tag="excited")

        self.assertTrue(result.id)
        self.assertEqual(result.gif_url, f"https://i.giphy.com/{result.id}.gif")
        self.assertEqual(result.webp_url, f"https://i.giphy.com/{result.id}.webp")


if __name__ == "__main__":
    unittest.main()