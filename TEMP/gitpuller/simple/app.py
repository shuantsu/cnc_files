import os
import subprocess
import sys

def execute_git_pull_terminal(repo_path):
    """
    Executes 'git pull' in the specified repository path and prints output to console.
    """
    if not repo_path:
        print("Error: No repository path provided.")
        print("Usage: python git_pull_terminal.py <path_to_repository>")
        return

    # Check if the path exists and is a directory
    if not os.path.isdir(repo_path):
        print(f"Error: The specified path '{repo_path}' does not exist or is not a directory.")
        return

    # Check if it's a Git repository
    if not os.path.exists(os.path.join(repo_path, '.git')):
        print(f"Error: '{repo_path}' is not a valid Git repository ('.git' folder not found).")
        return

    print(f"Executing 'git pull' in: {repo_path}")
    print("Please wait...\n")

    try:
        # Construct the command. Using 'cd' to change directory and then 'git pull'.
        # shell=True is used for convenience but be cautious with untrusted input.
        command = f'cd "{repo_path}" && git pull'
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True, # Captures stdout and stderr
            text=True,           # Decodes output as text
            check=False          # Do not raise an exception for non-zero exit codes
        )

        # Print standard output
        if process.stdout:
            print("--- Git Output ---")
            print(process.stdout)

        # Print standard error
        if process.stderr:
            print("--- Git Errors/Warnings ---")
            print(process.stderr)

        print("\n--- Command Finished ---")
        if process.returncode == 0:
            print("Git pull completed successfully.")
        else:
            print(f"Git pull failed with exit code {process.returncode}.")

    except FileNotFoundError:
        print("Error: 'git' command not found. Please ensure Git is installed and in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    # Check if a path argument was provided
    repository_path = open('path.txt', 'r').read().strip()
    execute_git_pull_terminal(repository_path)