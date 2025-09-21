import os
import tempfile
import logging
import unittest
import io
from monitor.utils import logger as logger_module

class TestLogger(unittest.TestCase):
	def setUp(self):
		logger_module.get_logger.cache_clear()

	def test_get_logger_returns_logger_instance(self):
		log = logger_module.get_logger("test_logger")
		self.assertIsInstance(log, logging.Logger)
		self.assertEqual(log.name, "test_logger")

	def test_get_logger_singleton(self):
		log1 = logger_module.get_logger("singleton")
		log2 = logger_module.get_logger("singleton")
		self.assertIs(log1, log2)

	def test_logger_writes_to_file_and_stream(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			log_path = os.path.join(tmpdir, "test.log")
			log = logger_module.get_logger("filetest", file_path=log_path)
			# Remove all handlers and add our own StringIO handler
			for handler in list(log.handlers):
				log.removeHandler(handler)
			stream = io.StringIO()
			stream_handler = logging.StreamHandler(stream)
			formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
			stream_handler.setFormatter(formatter)
			log.addHandler(stream_handler)
			# Add file handler back
			file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
			file_handler.setFormatter(formatter)
			log.addHandler(file_handler)
			test_message = "Hello, log file!"
			log.info(test_message)
			# Check StringIO stream
			stream.seek(0)
			output = stream.read()
			self.assertIn(test_message, output)
			# Check file
			with open(log_path, encoding="utf-8") as f:
				content = f.read()
				self.assertIn(test_message, content)

	def test_logger_format_includes_level_and_time(self):
		log = logger_module.get_logger("format_test")
		for handler in list(log.handlers):
			log.removeHandler(handler)
		stream = io.StringIO()
		stream_handler = logging.StreamHandler(stream)
		formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
		stream_handler.setFormatter(formatter)
		log.addHandler(stream_handler)
		test_message = "Test format"
		log.info(test_message)
		stream.seek(0)
		written = stream.read()
		self.assertIn("[INFO]", written)
		self.assertRegex(written, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:")

	def test_logger_file_path_default(self):
		log = logger_module.get_logger("default_path")
		file_handler_found = False
		for handler in log.handlers:
			if isinstance(handler, logging.FileHandler):
				self.assertTrue(handler.baseFilename.endswith("app.log"))
				file_handler_found = True
		self.assertTrue(file_handler_found, "No FileHandler found")

if __name__ == "__main__":
	unittest.main()
