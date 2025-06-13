# Gemini Code Generator

## Overview

The Gemini Code Generator is a desktop application that leverages Google's Gemini Pro API to generate code snippets based on user prompts. It provides a graphical user interface (GUI) for easy interaction, allowing users to input prompts, view generated code, manage generated files, and upload their projects to GitHub.

This tool is designed for developers and hobbyists looking to quickly scaffold code, explore solutions to programming problems, or experiment with AI-powered code generation.

## Installation

Follow these steps to set up and run the Gemini Code Generator:

1.  **Clone the Repository (if applicable):**
    If you have cloned this project from a Git repository, navigate to the project's root directory.

    ```bash
    git clone <repository_url>
    cd Gemini_Code_Generator
    ```

2.  **Create a Virtual Environment (Recommended):**
    It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    The project dependencies are listed in `requirements.txt`. Install them using pip:

    ```bash
    pip install -r requirements.txt
    ```
    This will install libraries such as `google-generativeai` for the Gemini API, `PyQt5` for the GUI, and `GitPython` for GitHub integration.

## Running the Application

Once the dependencies are installed, you can run the application from the project's root directory:

```bash
python src/main.py
```

This will launch the main GUI window.

## Features

### 1. Code Generation via Gemini API
*   **Prompt Input:** Enter your code generation requests (e.g., "create a Python function to calculate Fibonacci numbers") into the prompt area.
*   **API Interaction:** The application sends your prompt to the Gemini Pro API.
*   **Code Display:** The generated code (or any response from the API) is displayed in the response area.
*   **File Saving:** Generated code is automatically saved into the `output/` directory with a timestamped filename (e.g., `output/generated_code_YYYYMMDD_HHMMSS.py`).
*   **Project Explorer:** The integrated file explorer on the left panel shows the contents of the `output/` directory, allowing you to see and open generated files.

### 2. Save Project (Zip Archive)
*   **Archive Functionality:** Click the "Save Project (Zip)" button to package all files currently in the `output/` directory into a single `.zip` archive.
*   **File Dialog:** You will be prompted to choose a name and location for the saved zip file.

### 3. Upload to GitHub
*   **Git Integration:** Click the "Upload to GitHub" button to push the contents of your `output/` directory to a GitHub repository.
*   **Credentials:** You will be prompted to enter:
    *   The **GitHub Repository URL** (e.g., `https://github.com/your_username/your_repository.git`).
    *   Your **GitHub Personal Access Token (PAT)**. This token is used for authentication and requires appropriate permissions (e.g., `repo` scope) to push to the repository.
*   **Process:** The application will:
    1.  Initialize a Git repository in the `output/` directory if one doesn't exist.
    2.  Add all files to the staging area.
    3.  Commit the files with an automated message.
    4.  Set up or update the remote origin with your repository URL and PAT.
    5.  Push the changes to your GitHub repository.

## Basic Troubleshooting

*   **API Key for Gemini:**
    *   The application requires a valid API key for Google's Gemini API.
    *   Currently, this key needs to be set directly in the `src/GeminiAPI.py` file by replacing the placeholder `"YOUR_API_KEY_HERE"` with your actual key.
    *   **Future Improvement:** This will be moved to a configuration file (`src/config.py`) for better security and easier management.
    *   If the API key is missing or invalid, code generation will fail, and an error message will be displayed in the response area.

*   **GitHub Personal Access Token (PAT):**
    *   For the "Upload to GitHub" feature, a valid PAT with `repo` (or `public_repo` for public repositories) scope is required.
    *   Ensure the PAT is correctly entered when prompted.
    *   Storing PATs directly or inputting them frequently can be a security risk. Consider using a credential manager or Git's built-in credential helper for more secure, long-term use in your local environment (though the application itself currently prompts each time).

*   **GitPython Not Found:**
    *   If the "Upload to GitHub" button is disabled or you see errors related to `git`, ensure `GitPython` was installed correctly from `requirements.txt`.
    *   You can verify by running `pip show GitPython` in your virtual environment.

*   **Output Directory:**
    *   All generated files are saved in the `Gemini_Code_Generator/output/` directory.
    *   The file explorer in the GUI displays the contents of this directory.

*   **Application Errors:**
    *   Check the console output where you ran `python src/main.py` for any error messages or tracebacks.
    *   The GUI's response area may also display error messages from the application's operations.

## Future Enhancements
*   Configuration file for API keys.
*   More sophisticated parsing of Gemini's output for multi-file generation.
*   Advanced Git controls (branching, commit messages).
*   Tabbed interface for opening multiple files.
*   Theme and UI customization.

---
*This README provides a basic guide to the Gemini Code Generator. For more detailed information, please refer to the (forthcoming) User Guide.*
