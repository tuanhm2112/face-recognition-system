import unittest
from main_app.utils.style_loader import StyleLoader


class TestStyleLoader(unittest.TestCase):
    def setUp(self):
        StyleLoader.clear_cache()

    def test_load_dark_theme(self):
        stylesheet = StyleLoader.load_theme("dark")
        self.assertTrue(len(stylesheet) > 0, "Dark theme stylesheet should not be empty")

    def test_load_light_theme(self):
        stylesheet = StyleLoader.load_theme("light")
        self.assertTrue(len(stylesheet) > 0, "Light theme stylesheet should not be empty")

    def test_caching(self):
        sheet1 = StyleLoader.load_theme("dark")
        sheet2 = StyleLoader.load_theme("dark")
        self.assertIs(sheet1, sheet2, "Cached theme should return the same object")

    def test_invalid_theme(self):
        sheet = StyleLoader.load_theme("non_existent_theme_xyz")
        self.assertEqual(sheet, "")


if __name__ == "__main__":
    unittest.main()
