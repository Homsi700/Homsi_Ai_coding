import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import shutil
import sys
import datetime

# Add src directory to Python path to allow direct import of GeminiAPI
# This assumes tests are run from the root of the Gemini_Code_Generator project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import GeminiAPI

class TestGeminiAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Define output directory for tests. This should match GeminiAPI.OUTPUT_DIR
        cls.test_output_dir = "output_test_gemini_api"
        GeminiAPI.OUTPUT_DIR = cls.test_output_dir # Override OUTPUT_DIR for tests

        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)
        os.makedirs(cls.test_output_dir)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)
        # Reset OUTPUT_DIR if it was changed, to not affect other tests (if any)
        GeminiAPI.OUTPUT_DIR = "output"

    def setUp(self):
        # Reset global model state if necessary, or ensure init_client is called per test
        GeminiAPI.model = None
        # Clean the test output dir before each test if files are created per test method
        for f in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, f))


    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_init_client_success(self, mock_configure, mock_generative_model):
        """Test successful client initialization."""
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance

        self.assertTrue(GeminiAPI.init_client(api_key="fake_key"))
        mock_configure.assert_called_once_with(api_key="fake_key")
        mock_generative_model.assert_called_once_with(
            model_name="gemini-pro",
            generation_config=GeminiAPI.generation_config,
            safety_settings=GeminiAPI.safety_settings
        )
        self.assertEqual(GeminiAPI.model, mock_model_instance)
        self.assertTrue(os.path.exists(self.test_output_dir))

    def test_init_client_no_key(self):
        """Test client initialization failure if no API key."""
        # Ensure API_KEY is not set for this test if it relies on the module global
        with patch.object(GeminiAPI, 'API_KEY', "YOUR_API_KEY_HERE"): # or None
            self.assertFalse(GeminiAPI.init_client())
            self.assertIsNone(GeminiAPI.model)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_code_success(self, mock_configure, mock_generative_model):
        """Test successful code generation and file saving."""
        # Setup mock model and response
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "def hello():\n  print('Hello World')"
        mock_response.parts = [MagicMock()] # Ensure parts is not empty
        mock_response.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        # Initialize client
        GeminiAPI.init_client(api_key="fake_key") # Sets GeminiAPI.model

        prompt = "Create a hello world function in Python"
        with patch('os.path.exists', return_value=True): # Assume output dir exists
            with patch('builtins.open', mock_open()) as mocked_file_open:
                # Mock datetime to control filename
                fixed_datetime = datetime.datetime(2023, 1, 1, 12, 0, 0)
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.now.return_value = fixed_datetime

                    expected_filename = "generated_code_20230101_120000.py"
                    expected_filepath = os.path.join(self.test_output_dir, expected_filename)

                    return_message = GeminiAPI.generate_code(prompt)

                    mock_model_instance.generate_content.assert_called_once_with([prompt])
                    mocked_file_open.assert_called_once_with(expected_filepath, "w", encoding="utf-8")
                    mocked_file_open().write.assert_called_once_with(mock_response.text)

                    self.assertIn(f"Code generated and saved to {expected_filename}", return_message)
                    self.assertIn(mock_response.text, return_message)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_code_api_error_blocked(self, mock_configure, mock_generative_model):
        """Test handling of API prompt blockage."""
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.parts = [] # No parts
        mock_response.prompt_feedback = MagicMock()
        mock_response.prompt_feedback.block_reason = "SAFETY"
        mock_response.prompt_feedback.block_reason_message = "Content blocked due to safety reasons."
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        GeminiAPI.init_client(api_key="fake_key")
        prompt = "Some harmful prompt"
        return_message = GeminiAPI.generate_code(prompt)

        self.assertIn("Error: Prompt blocked due to Content blocked due to safety reasons.", return_message)
        # Ensure no file was attempted to be saved
        self.assertEqual(len(os.listdir(self.test_output_dir)), 0)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_code_no_model_auto_init_fails(self, mock_configure, mock_generative_model):
        """Test generate_code when model is not initialized and auto-init fails."""
        GeminiAPI.model = None # Ensure model is not set
        # Make init_client fail by not providing a key and ensuring global API_KEY is bad
        with patch.object(GeminiAPI, 'API_KEY', "YOUR_API_KEY_HERE"):
             with patch.object(GeminiAPI, 'init_client', wraps=GeminiAPI.init_client) as wrapped_init:
                return_message = GeminiAPI.generate_code("Any prompt")
                wrapped_init.assert_called_once() # Check that auto-init was attempted
                self.assertIn("Error: API Client not initialized and failed to auto-initialize.", return_message)


if __name__ == '__main__':
    unittest.main()
