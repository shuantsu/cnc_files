import tkinter as tk
from tkinter import ttk
import os
import subprocess
from tkinter import scrolledtext
import configparser

class GitPullApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Pull Tool")

        # Define the configuration file path
        # This will create/read a file named 'config.ini' in the same directory as the script
        self.config_file = 'config.ini'
        self.config = configparser.ConfigParser()

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights to make the layout responsive
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1) # Allow console to expand vertically
        main_frame.grid_columnconfigure(1, weight=1) # Allow path entry to expand horizontally

        # Path input
        ttk.Label(main_frame, text="Repository Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Bind the <KeyRelease> event to save the path
        # This means the path will be saved every time a key is released in the entry field
        self.path_entry.bind("<KeyRelease>", self.save_path)

        # Pull button
        pull_button = ttk.Button(main_frame, text="Execute Git Pull", command=self.execute_git_pull)
        pull_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Output console
        self.console = scrolledtext.ScrolledText(main_frame, width=60, height=15, wrap=tk.WORD) # Added wrap=tk.WORD
        self.console.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Load the last saved path when the application starts
        self.load_path()

    def load_path(self):
        """Loads the last saved repository path from the config file."""
        try:
            self.config.read(self.config_file)
            if 'Settings' in self.config and 'last_path' in self.config['Settings']:
                last_path = self.config['Settings']['last_path']
                self.path_var.set(last_path)
                self.console.insert(tk.END, f"Loaded last path: {last_path}\n")
            else:
                self.console.insert(tk.END, "No previous path found.\n")
        except Exception as e:
            self.console.insert(tk.END, f"Error loading config: {str(e)}\n")

    def save_path(self, event=None): # event=None allows it to be called without an event object
        """Saves the current repository path to the config file."""
        current_path = self.path_var.get()
        if not self.config.has_section('Settings'):
            self.config.add_section('Settings')
        self.config['Settings']['last_path'] = current_path
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            # self.console.insert(tk.END, f"Path saved: {current_path}\n") # Optional: uncomment to see save messages
        except Exception as e:
            self.console.insert(tk.END, f"Error saving config: {str(e)}\n")

    def execute_git_pull(self):
        """Executes the 'git pull' command in the specified repository path."""
        path = self.path_var.get().strip() # Get path and remove leading/trailing whitespace
        if not path:
            self.console.insert(tk.END, "Please enter a repository path.\n")
            return

        # Check if the path exists and is a directory
        if not os.path.isdir(path):
            self.console.insert(tk.END, f"Error: The specified path '{path}' does not exist or is not a directory.\n")
            return

        # Check if it's a Git repository
        if not os.path.exists(os.path.join(path, '.git')):
            self.console.insert(tk.END, f"Error: '{path}' is not a valid Git repository ('.git' folder not found).\n")
            return

        self.console.delete(1.0, tk.END) # Clear previous output
        self.console.insert(tk.END, f"Executing 'git pull' in: {path}\n")
        self.console.insert(tk.END, "Please wait...\n")
        self.console.update_idletasks() # Update GUI to show "Please wait..." immediately

        try:
            # Create command and execute
            # Using 'shell=True' is convenient but can be a security risk with untrusted input.
            # For this specific use case with user-provided local paths, it's generally acceptable.
            # 'cd' is used to change directory before executing 'git pull'.
            command = f'cd "{path}" && git pull'
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                universal_newlines=True, # Decodes output as text
                encoding='utf-8' # Specify encoding for better compatibility
            )

            # Get output as it comes (more responsive for long operations)
            stdout_output = []
            stderr_output = []

            # Read stdout line by line
            for line in iter(process.stdout.readline, ''):
                stdout_output.append(line)
                self.console.insert(tk.END, line)
                self.console.see(tk.END) # Scroll to the end
                self.console.update_idletasks()

            # Read stderr line by line
            for line in iter(process.stderr.readline, ''):
                stderr_output.append(line)
                self.console.insert(tk.END, line)
                self.console.see(tk.END) # Scroll to the end
                self.console.update_idletasks()

            process.stdout.close()
            process.stderr.close()
            return_code = process.wait() # Wait for the process to terminate

            # Display final summary
            self.console.insert(tk.END, "\n--- Command Finished ---\n")
            if return_code == 0:
                self.console.insert(tk.END, "Git pull completed successfully.\n")
            else:
                self.console.insert(tk.END, f"Git pull failed with exit code {return_code}.\n")

        except FileNotFoundError:
            self.console.insert(tk.END, "Error: 'git' command not found. Please ensure Git is installed and in your system's PATH.\n")
        except Exception as e:
            self.console.insert(tk.END, f"An unexpected error occurred: {str(e)}\n")
        finally:
            self.console.see(tk.END) # Ensure console is scrolled to the end after execution

if __name__ == "__main__":
    root = tk.Tk()
    app = GitPullApp(root)
    root.mainloop()