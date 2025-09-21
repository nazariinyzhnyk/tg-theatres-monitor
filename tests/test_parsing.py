import unittest
from unittest.mock import patch, MagicMock
from monitor.parser import parsing

class TestParsing(unittest.TestCase):
    def setUp(self):
        self.sample_cfg = {
            "general": {"results_per_theatre": 2},
            "theatres": [
                {
                    "name": "Theatre1",
                    "base_url": "https://theatre1.com",
                    "program_url": "https://theatre1.com/program",
                    "selectors": {
                        "elements": "div.show",
                        "time": "span.time",
                        "title": "h2.title",
                        "link": "a.link"
                    }
                },
                {
                    "name": "Theatre2",
                    "base_url": "https://theatre2.com",
                    "program_url": None,  # Should be skipped
                    "selectors": {
                        "elements": "div.show",
                        "time": "span.time",
                        "title": "h2.title",
                        "link": "a.link"
                    }
                },
                {
                    "name": "Theatre3",
                    "base_url": "https://theatre3.com",
                    "program_url": "https://theatre3.com/program",
                    "selectors": {}  # Should be skipped
                }
            ]
        }
        self.fake_parsed_data = [
            {"title": "Show1", "time": "19:00", "link": "/show1"},
            {"title": "Show2", "time": "20:00", "link": "https://theatre1.com/show2"},
            {"title": "Show3", "time": "21:00", "link": "/show3"},
        ]

    @patch("monitor.parser.parsing.fetch_and_parse")
    def test_parse_all_success(self, mock_fetch_and_parse):
        mock_fetch_and_parse.return_value = self.fake_parsed_data
        results = parsing.parse_all(self.sample_cfg)
        # Only Theatre1 should be parsed
        self.assertIn("Theatre1", results)
        self.assertNotIn("Theatre2", results)
        self.assertNotIn("Theatre3", results)
        # Only 2 results per theatre due to config
        self.assertEqual(len(results["Theatre1"]), 2)
        # Link normalization
        self.assertTrue(results["Theatre1"][0]["link"].startswith("https://theatre1.com"))
        self.assertTrue(results["Theatre1"][1]["link"].startswith("https://theatre1.com"))

    @patch("monitor.parser.parsing.fetch_and_parse")
    def test_parse_all_empty_theatres(self, mock_fetch_and_parse):
        cfg = {"general": {"results_per_theatre": 2}, "theatres": []}
        results = parsing.parse_all(cfg)
        self.assertEqual(results, {})

    @patch("monitor.parser.parsing.fetch_and_parse")
    def test_parse_all_missing_selectors(self, mock_fetch_and_parse):
        cfg = {
            "general": {"results_per_theatre": 2},
            "theatres": [
                {
                    "name": "TheatreX",
                    "base_url": "https://theatrex.com",
                    "program_url": "https://theatrex.com/program",
                    "selectors": {}
                }
            ]
        }
        results = parsing.parse_all(cfg)
        self.assertEqual(results, {})

    @patch("monitor.parser.parsing.fetch_and_parse")
    def test_parse_all_fetch_and_parse_raises(self, mock_fetch_and_parse):
        mock_fetch_and_parse.side_effect = Exception("fetch error")
        results = parsing.parse_all(self.sample_cfg)
        # Theatre1 should not be present due to error
        self.assertNotIn("Theatre1", results)

    @patch("monitor.parser.parsing.load_yaml_config")
    @patch("monitor.parser.parsing.fetch_and_parse")
    def test_parse_all_loads_config_when_none(self, mock_fetch_and_parse, mock_load_yaml_config):
        mock_load_yaml_config.return_value = self.sample_cfg
        mock_fetch_and_parse.return_value = self.fake_parsed_data
        results = parsing.parse_all()
        self.assertIn("Theatre1", results)
        mock_load_yaml_config.assert_called_once()

    @patch("monitor.parser.parsing.parse_all")
    def test_main_success(self, mock_parse_all):
        mock_parse_all.return_value = {"Theatre1": [{"title": "Show1"}]}
        with patch("builtins.print") as mock_print:
            parsing.main()
            mock_print.assert_called_once_with({"Theatre1": [{"title": "Show1"}]})

    @patch("monitor.parser.parsing.parse_all")
    @patch("monitor.parser.parsing.logger")
    def test_main_exception(self, mock_logger, mock_parse_all):
        mock_parse_all.side_effect = Exception("main error")
        parsing.main()
        mock_logger.error.assert_called()

if __name__ == "__main__":
    unittest.main()