import unittest
import os
import yaml


class TestConfigStructure(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.example_config_path = os.path.join(self.project_root, "resources", "config", "config.example.yaml")
        self.config_path = os.path.join(self.project_root, "resources", "config", "config.yaml")

    def test_example_config_exists(self):
        self.assertTrue(os.path.exists(self.example_config_path), "config.example.yaml should exist")

    def test_example_config_valid_yaml(self):
        with open(self.example_config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.assertIsInstance(data, dict)
        self.assertIn("camera", data)
        self.assertIn("models", data)
        self.assertIn("runtime", data)
        self.assertIn("ui", data)

    def test_required_directories_exist(self):
        for dirname in ["resources", "main_app", "scripts", "logs"]:
            path = os.path.join(self.project_root, dirname)
            self.assertTrue(os.path.exists(path), f"Directory {dirname} should exist")


if __name__ == "__main__":
    unittest.main()
