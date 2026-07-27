import importlib.util
import unittest
from pathlib import Path


class AppImportsTest(unittest.TestCase):
    def test_app_and_pages_compile_as_modules(self):
        paths = [Path("app.py"), *sorted(Path("pages").glob("*.py"))]
        for path in paths:
            with self.subTest(path=str(path)):
                spec = importlib.util.spec_from_file_location(path.stem, path)
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader)


if __name__ == "__main__":
    unittest.main()
