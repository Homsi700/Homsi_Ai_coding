import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTreeView, QFileSystemModel, QLabel,
    QSizePolicy, QSplitter, QFileDialog
)
from PyQt5.QtCore import Qt, QDir

# Define the output directory. If GUI.py is in src/, this should go up one level.
# This assumes that the application will be run from the project's root directory
# or that paths are handled consistently.
# For QFileSystemModel, it's best to use an absolute path.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR_NAME = "output"
OUTPUT_DIR_PATH = os.path.join(PROJECT_ROOT, OUTPUT_DIR_NAME)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Code Generator")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Ensure output directory exists
        if not os.path.exists(OUTPUT_DIR_PATH):
            try:
                os.makedirs(OUTPUT_DIR_PATH)
                print(f"Created output directory for GUI: {OUTPUT_DIR_PATH}")
            except OSError as e:
                print(f"Error creating output directory {OUTPUT_DIR_PATH} from GUI: {e}")
                # Fallback or error message needed if directory creation fails
                # For now, QFileSystemModel might show an empty/invalid path

        splitter = QSplitter(Qt.Horizontal)

        self.file_panel_widget = QWidget()
        self.file_panel_layout = QVBoxLayout(self.file_panel_widget)
        self.file_panel_label = QLabel("Project Output Explorer")
        self.file_tree = QTreeView()
        self.fs_model = QFileSystemModel()

        self.fs_model.setRootPath(OUTPUT_DIR_PATH)
        # Optionally, set filter to show only certain files, e.g. self.fs_model.setNameFilters(["*.py"])
        # self.fs_model.setNameFilterDisables(False) # To make sure filters apply to files not just directories

        self.file_tree.setModel(self.fs_model)
        self.file_tree.setRootIndex(self.fs_model.index(OUTPUT_DIR_PATH)) # Crucial: Set the root index to the output dir
        self.file_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_tree.setColumnWidth(0, 250) # Adjust column width for names

        self.file_panel_layout.addWidget(self.file_panel_label)
        self.file_panel_layout.addWidget(self.file_tree)
        splitter.addWidget(self.file_panel_widget)

        self.right_panel_widget = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel_widget)

        self.prompt_label = QLabel("Enter your prompt:")
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("e.g., Create a Python function to sort a list...")
        self.prompt_input.setFixedHeight(150)

        self.response_label = QLabel("Generated Code/API Response:")
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        self.button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Code")
        self.save_button = QPushButton("Save Project (Zip)")
        self.github_button = QPushButton("Upload to GitHub") # Not implemented yet

        self.button_layout.addWidget(self.generate_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.github_button)

        self.right_panel_layout.addWidget(self.prompt_label)
        self.right_panel_layout.addWidget(self.prompt_input)
        self.right_panel_layout.addWidget(self.response_label)
        self.right_panel_layout.addWidget(self.response_display)
        self.right_panel_layout.addLayout(self.button_layout)
        splitter.addWidget(self.right_panel_widget)

        splitter.setSizes([300, 900])
        self.main_layout.addWidget(splitter)

        self._connect_actions()

    def _connect_actions(self):
        # Connections for generate, save, etc. will be done in main.py
        # or via methods exposed by this class.
        # For file tree interaction:
        self.file_tree.doubleClicked.connect(self._handle_file_tree_double_click)
        # The actual button connections (generate, save) are set up in main.py

    def _handle_file_tree_double_click(self, index):
        path = self.fs_model.filePath(index)
        if self.fs_model.isFile(index):
            try:
                # Try to detect encoding, fallback to utf-8
                content = ""
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(path, 'r', encoding='latin-1') as f: # Common fallback
                        content = f.read()

                self.response_display.setText(f"--- Content of {os.path.basename(path)} ---\n\n{content}")
            except Exception as e:
                self.response_display.setText(f"Error reading file {os.path.basename(path)}: {e}")
        else:
            # Optionally, expand/collapse directory or other actions
            print(f"Directory double-clicked: {path}")


    def refresh_file_tree(self):
        """Refreshes the QTreeView to show current contents of OUTPUT_DIR_PATH."""
        # This is often not needed as QFileSystemModel updates automatically.
        # However, if explicit refresh is required for some reason:
        # self.fs_model.setRootPath(OUTPUT_DIR_PATH) # Re-evaluates the directory
        # self.file_tree.setRootIndex(self.fs_model.index(OUTPUT_DIR_PATH))
        # More simply, QFileSystemModel should emit signals that cause updates.
        # If issues arise, one might need to reset the model or root index.
        print(f"File tree looking at: {self.fs_model.rootPath()}")
        # Forcing a layout change can sometimes trigger refresh if model updates are missed
        # self.file_tree.updateGeometries()
        # self.fs_model.directoryLoaded.emit(OUTPUT_DIR_PATH) # Not standard way


def main():
    # This main is for testing GUI.py directly.
    # The actual application is run from main.py
    if not os.path.exists(OUTPUT_DIR_PATH):
        os.makedirs(OUTPUT_DIR_PATH)
        print(f"Test output dir created: {OUTPUT_DIR_PATH}")
    # Create a dummy file for testing tree view
    with open(os.path.join(OUTPUT_DIR_PATH, "gui_test_file.txt"), "w") as f:
        f.write("This is a test file for GUI.py direct launch.")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
