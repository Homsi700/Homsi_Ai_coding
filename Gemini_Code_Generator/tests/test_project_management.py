import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import sys
import zipfile
import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# main.py relies on GUI and GeminiAPI, so we need to be careful with imports
# We will specifically test handle_save_project
# We might need to mock parts of GUI or GeminiAPI if they are problematic for this test
import main # This will import GUI and GeminiAPI as well.

class TestProjectManagement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Define a test output directory that main.handle_save_project will zip
        # This path must match what main.OUTPUT_DIR_PATH would resolve to.
        # main.OUTPUT_DIR_PATH is os.path.join(PROJECT_ROOT, "output")
        # where PROJECT_ROOT is os.path.abspath(os.path.join(os.path.dirname(GUI.__file__), '..'))
        # So, effectively, it's <project_root>/output
        cls.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        cls.test_output_dir_to_zip = os.path.join(cls.project_root, "output_test_project_management")

        # This is where zip files will be saved *temporarily* during the test
        cls.test_zip_save_dir = os.path.join(cls.project_root, "test_zip_files")

        # Override main.OUTPUT_DIR_PATH for the duration of these tests
        cls.original_output_dir_path = main.OUTPUT_DIR_PATH
        main.OUTPUT_DIR_PATH = cls.test_output_dir_to_zip

        if os.path.exists(cls.test_output_dir_to_zip):
            shutil.rmtree(cls.test_output_dir_to_zip)
        os.makedirs(cls.test_output_dir_to_zip)

        if os.path.exists(cls.test_zip_save_dir):
            shutil.rmtree(cls.test_zip_save_dir)
        os.makedirs(cls.test_zip_save_dir)


    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_output_dir_to_zip):
            shutil.rmtree(cls.test_output_dir_to_zip)
        if os.path.exists(cls.test_zip_save_dir):
            shutil.rmtree(cls.test_zip_save_dir)
        main.OUTPUT_DIR_PATH = cls.original_output_dir_path # Restore original path


    def setUp(self):
        # Clear and recreate the directory to zip for each test
        if os.path.exists(self.test_output_dir_to_zip):
            shutil.rmtree(self.test_output_dir_to_zip)
        os.makedirs(self.test_output_dir_to_zip)

        # Create some dummy files in the output directory to be zipped
        self.dummy_files = ["file1.txt", "file2.py", "subdir/file3.json"]
        for file_rel_path in self.dummy_files:
            file_abs_path = os.path.join(self.test_output_dir_to_zip, file_rel_path)
            os.makedirs(os.path.dirname(file_abs_path), exist_ok=True)
            with open(file_abs_path, "w") as f:
                f.write(f"Content of {file_rel_path}")

        # Mock the main_window_instance for response_display.setText
        # and other QDialogs if they were not patched
        self.mock_main_window = MagicMock()
        main.main_window_instance = self.mock_main_window


    def tearDown(self):
        # Clean up any created zip files in test_zip_save_dir
        for item in os.listdir(self.test_zip_save_dir):
            item_path = os.path.join(self.test_zip_save_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
        main.main_window_instance = None # Reset


    @patch('main.QFileDialog.getSaveFileName')
    def test_handle_save_project_success(self, mock_get_save_file_name):
        """Test successful creation of a zip archive."""

        # Mock QFileDialog to return a fixed path for the zip file
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        mock_zip_filename = f"test_project_{timestamp}.zip"
        mock_zip_filepath = os.path.join(self.test_zip_save_dir, mock_zip_filename)
        mock_get_save_file_name.return_value = (mock_zip_filepath, "Zip Files (*.zip)")

        main.handle_save_project()

        # Assert QFileDialog was called
        mock_get_save_file_name.assert_called_once()

        # Assert the main window's response display was called with success
        self.mock_main_window.response_display.setText.assert_any_call(
            f"Project saved successfully to {mock_zip_filepath}"
        )

        # Check if the zip file was created
        self.assertTrue(os.path.exists(mock_zip_filepath))

        # Check the contents of the zip file
        with zipfile.ZipFile(mock_zip_filepath, 'r') as zf:
            zip_contents = zf.namelist()
            # Ensure correct number of items (files + potentially the subdir itself)
            # zip namelist includes directory entries as well for some archivers
            # For shutil.make_archive, it usually just lists files relative to the root_dir.
            self.assertEqual(len(zip_contents), len(self.dummy_files))
            for dummy_file in self.dummy_files:
                self.assertIn(dummy_file.replace("\\", "/"), zip_contents) # Normalize paths for comparison

    @patch('main.QFileDialog.getSaveFileName')
    def test_handle_save_project_cancel(self, mock_get_save_file_name):
        """Test user cancelling the save dialog."""
        mock_get_save_file_name.return_value = ("", "") # User cancelled

        main.handle_save_project()

        self.mock_main_window.response_display.setText.assert_called_with("Save operation cancelled.")
        # Ensure no zip file was created
        self.assertEqual(len(os.listdir(self.test_zip_save_dir)), 0)


    def test_handle_save_project_empty_dir(self):
        """Test saving when the output directory is empty."""
        # Clear the output directory
        shutil.rmtree(self.test_output_dir_to_zip)
        os.makedirs(self.test_output_dir_to_zip) # Recreate it empty

        main.handle_save_project()

        self.mock_main_window.response_display.setText.assert_called_with(
            "Output directory is empty. Nothing to save."
        )
        # Ensure no zip file was created
        self.assertEqual(len(os.listdir(self.test_zip_save_dir)), 0)


if __name__ == '__main__':
    unittest.main()
