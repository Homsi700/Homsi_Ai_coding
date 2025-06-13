import sys
import os
import shutil
import datetime
import re # For URL validation and PAT insertion
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QLineEdit
from PyQt5.QtCore import QDir # For QInputDialog path suggestions
from GUI import MainWindow, OUTPUT_DIR_PATH
import GeminiAPI

# Attempt to import GitPython
try:
    import git
except ImportError:
    # This message should ideally be shown in the GUI if GitPython is critical
    print("GitPython is not installed. Please install it by running: pip install GitPython")
    # We can define a placeholder for git so the app doesn't crash if it's not used immediately.
    # Or, disable the GitHub button if the import fails.
    git = None

main_window_instance = None

def display_error_message(title, message):
    """Helper function to display error messages in a QMessageBox."""
    if main_window_instance:
        QMessageBox.critical(main_window_instance, title, message)
    else:
        print(f"ERROR: {title} - {message}")

def handle_generate_code():
    global main_window_instance
    if not main_window_instance:
        display_error_message("Error", "MainWindow instance not available.")
        return

    prompt_text = main_window_instance.prompt_input.toPlainText()
    if not prompt_text.strip():
        main_window_instance.response_display.setText("Please enter a prompt.")
        return

    main_window_instance.response_display.setText("Generating code, please wait...")
    QApplication.processEvents()

    response_message = GeminiAPI.generate_code(prompt_text)
    main_window_instance.response_display.setText(response_message)

def handle_save_project():
    global main_window_instance
    if not main_window_instance:
        display_error_message("Error", "MainWindow instance not available for saving.")
        return

    if not os.path.exists(OUTPUT_DIR_PATH) or not os.listdir(OUTPUT_DIR_PATH):
        main_window_instance.response_display.setText("Output directory is empty. Nothing to save.")
        return

    default_zip_name = f"project_archive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_file_path, _ = QFileDialog.getSaveFileName(
        main_window_instance, "Save Project As Zip",
        os.path.join(QDir.homePath(), default_zip_name), # Start in home directory
        "Zip Files (*.zip)"
    )

    if not zip_file_path:
        main_window_instance.response_display.setText("Save operation cancelled.")
        return

    try:
        archive_base_name = os.path.splitext(zip_file_path)[0]
        shutil.make_archive(archive_base_name, 'zip', OUTPUT_DIR_PATH)
        final_archive_path = archive_base_name + ".zip"
        main_window_instance.response_display.setText(f"Project saved successfully to {final_archive_path}")
    except Exception as e:
        display_error_message("Error Saving Project", f"Error saving project: {e}")
        main_window_instance.response_display.setText(f"Error saving project: {e}")


def handle_upload_to_github():
    global main_window_instance
    if not main_window_instance:
        display_error_message("Error", "MainWindow instance not available for GitHub upload.")
        return

    if not git:
        display_error_message("Git Error", "GitPython is not installed or failed to import. This feature is unavailable.")
        main_window_instance.response_display.setText("GitPython is not installed. Please run 'pip install GitPython'.")
        return

    if not os.path.exists(OUTPUT_DIR_PATH) or not os.listdir(OUTPUT_DIR_PATH):
        main_window_instance.response_display.setText("Output directory is empty. Nothing to upload.")
        return

    # 1. Get Repository URL
    repo_url, ok = QInputDialog.getText(main_window_instance, "GitHub Repository",
                                        "Enter Repository URL (e.g., https://github.com/user/repo.git):")
    if not ok or not repo_url:
        main_window_instance.response_display.setText("GitHub upload cancelled: No repository URL provided.")
        return

    # 2. Get Personal Access Token (PAT)
    pat, ok = QInputDialog.getText(main_window_instance, "GitHub PAT",
                                   "Enter your GitHub Personal Access Token:", QLineEdit.Password)
    if not ok or not pat:
        main_window_instance.response_display.setText("GitHub upload cancelled: No PAT provided.")
        return

    main_window_instance.response_display.setText("Processing GitHub upload...")
    QApplication.processEvents()

    try:
        # Construct the remote URL with PAT for authentication
        # https://<PAT>@github.com/user/repo.git
        # Basic validation and construction
        if not re.match(r"https://github.com/.+/.+\.git", repo_url):
            display_error_message("Invalid URL", "The repository URL seems invalid. It should be like https://github.com/user/repo.git")
            main_window_instance.response_display.setText("Invalid repository URL format.")
            return

        authenticated_url = repo_url.replace("https://", f"https://{pat}@")

        # Initialize repo or open existing one
        try:
            repo = git.Repo(OUTPUT_DIR_PATH)
            is_new_repo = False
            main_window_instance.response_display.setText("Opened existing repository in output directory.")
        except git.exc.InvalidGitRepositoryError:
            repo = git.Repo.init(OUTPUT_DIR_PATH)
            is_new_repo = True
            main_window_instance.response_display.setText("Initialized new Git repository in output directory.")

        QApplication.processEvents()

        # Add and Commit
        repo.git.add(A=True)
        if repo.is_dirty(untracked_files=True): # Check if there's anything to commit
            commit_message = f"Automated commit on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            repo.index.commit(commit_message)
            main_window_instance.response_display.append("Committed all files.")
        else:
            main_window_instance.response_display.append("No changes to commit.")
        QApplication.processEvents()

        # Handle remote
        remote_name = "origin"
        if remote_name in repo.remotes:
            origin = repo.remotes.origin
            origin.set_url(authenticated_url)
            main_window_instance.response_display.append(f"Updated remote '{remote_name}'.")
        else:
            origin = repo.create_remote(remote_name, authenticated_url)
            main_window_instance.response_display.append(f"Created remote '{remote_name}'.")
        QApplication.processEvents()

        # Determine current branch or default to 'main'
        try:
            current_branch = repo.active_branch.name
        except TypeError: # Happens in a new repo with no commits yet if we didn't commit above
             # If we just initialized and committed, active_branch might be master or main
             # Let's try to get it, or default.
             if repo.heads: # Check if any heads (branches) exist
                current_branch = repo.active_branch.name
             else: # Fresh repo, no commits yet (though we tried to commit)
                # We need to create a branch. 'main' is a common default.
                # This situation should ideally be handled by ensuring a commit happens on a branch.
                # If the commit above happened, a branch should exist.
                # For safety, let's default, but this indicates a potential prior issue.
                if not repo.head.is_valid(): # No valid HEAD, meaning no commits
                    # This case should be rare if commit logic is fine
                    # We might need to checkout a new branch explicitly if the repo is truly empty
                    # For now, assume 'main' or 'master' will be created by the first push if needed by some git versions,
                    # or that the commit above established a branch.
                     main_window_instance.response_display.append("Warning: No active branch found, attempting to push to 'main'.")
                     current_branch = "main" # Default to main
                else:
                    current_branch = repo.active_branch.name


        main_window_instance.response_display.append(f"Attempting to push to {remote_name}/{current_branch}...")
        QApplication.processEvents()

        # Push
        push_info = origin.push(refspec=f'{current_branch}:{current_branch}') # Push current branch to remote current branch

        if push_info:
            pi = push_info[0] # Assuming one ref pushed
            if pi.flags & git.remote.PushInfo.ERROR:
                error_msg = f"Error during push: {pi.summary}"
                display_error_message("GitHub Push Error", error_msg)
                main_window_instance.response_display.append(error_msg)
            elif pi.flags & git.remote.PushInfo.REJECTED:
                error_msg = f"Push rejected: {pi.summary}. (Non-fast-forward or other upstream issues)"
                display_error_message("GitHub Push Rejected", error_msg)
                main_window_instance.response_display.append(error_msg)
            else:
                success_msg = f"Successfully pushed to {remote_name}/{current_branch}."
                main_window_instance.response_display.append(success_msg)
        else:
            # This case might occur if there was nothing to push or an unhandled situation
            main_window_instance.response_display.append("Push completed, but no detailed push info received. Check repository.")

    except git.exc.GitCommandError as e:
        error_message = f"Git command error: {e}"
        display_error_message("Git Error", error_message)
        main_window_instance.response_display.append(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        display_error_message("GitHub Upload Error", error_message)
        main_window_instance.response_display.append(error_message)


def main():
    global main_window_instance

    if not os.path.exists(OUTPUT_DIR_PATH):
        try:
            os.makedirs(OUTPUT_DIR_PATH)
        except OSError as e:
            display_error_message("Startup Error", f"Error creating output directory {OUTPUT_DIR_PATH}: {e}")
            sys.exit(1)

    if not GeminiAPI.init_client():
        # Error already printed by init_client. GUI will show further errors on generation.
        # Consider a QMessageBox here if API is critical for any startup task.
        pass # Allow GUI to start, API errors will be handled per-action

    app = QApplication(sys.argv)
    main_window_instance = MainWindow()

    # Connect buttons
    if hasattr(main_window_instance, 'generate_button'):
        main_window_instance.generate_button.clicked.connect(handle_generate_code)
    if hasattr(main_window_instance, 'save_button'):
        main_window_instance.save_button.clicked.connect(handle_save_project)

    # Conditionally enable GitHub button if GitPython is available
    if hasattr(main_window_instance, 'github_button'):
        if git:
            main_window_instance.github_button.clicked.connect(handle_upload_to_github)
        else:
            main_window_instance.github_button.setEnabled(False)
            main_window_instance.github_button.setToolTip("GitPython not found. Please install it.")
            # Optionally, add a label in the GUI to inform about missing GitPython

    main_window_instance.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
