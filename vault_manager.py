from markdown_reader import MarkdownReader
from issue_reporter import IssueReporter
import os
import re
import yaml
import pandas as pd

class VaultManager:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.current_path = vault_path  # Initialize current path to the vault directory
        self.current_race = None  # To keep track of the opened race (MarkdownReader object)
        self.group_map = {}  # To map group IDs to group names
        self.issue_reporter = IssueReporter(vault_path)

    def ls(self):
        try:
            items = os.listdir(self.current_path)
            folders = [f for f in items if os.path.isdir(os.path.join(self.current_path, f)) and not f.startswith('.')]
            files = [f for f in items if os.path.isfile(os.path.join(self.current_path, f)) and not f.startswith('.')]
            
            if folders or files:
                print(f"Contents of '{self.current_path}':")
                for folder in folders:
                    cleaned_name = self._clean_folder_name(folder)
                    print(f"📁 {cleaned_name}")
                for file in files:
                    print(f"📄 {file}")
            else:
                print(f"No folders or files found in '{self.current_path}'.")
        except FileNotFoundError:
            print(f"The path '{self.current_path}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def cd(self, folder_name):
        if folder_name == "..":
            new_path = os.path.dirname(self.current_path)
            if os.path.commonpath([new_path, self.vault_path]) == self.vault_path:
                self.current_path = new_path
                print(f"Changed directory to '{self.current_path}'")
                self.ls()
            else:
                print("You are at the root of the vault. Cannot go up further.")
        else:
            for f in os.scandir(self.current_path):
                if f.is_dir() and self._clean_folder_name(f.name).lower() == folder_name.lower():
                    new_path = os.path.join(self.current_path, f.name)
                    self.current_path = new_path
                    print(f"Changed directory to '{self.current_path}'")
                    self.ls()
                    return

            print(f"Folder '{folder_name}' not found.")

    def open(self, name):
        races_path = os.path.join(self.vault_path, "00 - Races")
        for f in os.scandir(races_path):
            if f.is_file() and name.lower() in self._clean_folder_name(f.name).lower():
                self.current_race = MarkdownReader(f.path, self.vault_path)
                print(f"Race '{name}' opened.")
                self.issue_reporter.report_issues(name)  # Use IssueReporter
                return
            elif f.is_dir() and self._clean_folder_name(f.name).lower() == name.lower():
                race_file_path = os.path.join(f.path, f"{name}.md")
                if os.path.isfile(race_file_path):
                    self.current_race = MarkdownReader(race_file_path, self.vault_path)
                    print(f"Race '{name}' opened from folder.")
                    self.issue_reporter.report_issues(name)  # Use IssueReporter
                    return
                else:
                    print(f"No '{name}.md' file found in folder '{f.name}'.")
                    return

        print(f"No file or folder containing '{name}' found in '00 - Races'.")

    def close(self):
        if self.current_race:
            print(f"Race '{self.current_race.file_name}' closed.")
            self.current_race = None
        else:
            print("No race is currently opened.")

    def race_property(self, race_name=None):
        if self.current_race and (race_name is None or race_name.lower() == self._clean_folder_name(self.current_race.file_name).lower()):
            print("Properties:")
            for key, value in self.current_race.property.items():
                print(f"{key}: {value}")
        else:
            print("No race is currently opened or wrong race name.")

    def race_content(self, race_name=None):
        if self.current_race and (race_name is None or race_name.lower() == self._clean_folder_name(self.current_race.file_name).lower()):
            print("Content:")
            for title, content in self.current_race.content.items():
                print(f"\nTitle: {title}\n{content}\n")
        else:
            print("No race is currently opened or wrong race name.")

    def race_links(self, race_name=None):
        if self.current_race and (race_name is None or race_name.lower() == self._clean_folder_name(self.current_race.file_name).lower()):
            print("Links:")
            for key, value in self.current_race.get_links().items():
                print(f"{key}: {value}")
        else:
            print("No race is currently opened or wrong race name.")

    def race_city(self, race_name):
        if self.current_race and race_name.lower() == self._clean_folder_name(self.current_race.file_name).lower():
            race_folder_name = self._clean_folder_name(self.current_race.file_name).rsplit('.', 1)[0]  # Removes .md extension
            city_path = os.path.join(self.vault_path, "02 - Lieux", race_folder_name)
            
            if os.path.exists(city_path):
                for f in os.scandir(city_path):
                    if f.is_file() and f.name.endswith('.md'):
                        city_name = os.path.splitext(f.name)[0]  # Remove .md extension
                        tags = self._get_tags_from_file(os.path.join(city_path, f.name))
                        city_type = "Capital" if "capitale" in tags else "City"
                        print(f"{city_type}: {city_name}")
            else:
                print(f"No '02 - Lieux/{race_folder_name}' folder found.")
        else:
            print("No race is currently opened or wrong race name.")

    def _get_tags_from_file(self, file_path):
        """Extracts the tags from the front matter of a Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                front_matter = yaml.safe_load(match.group(1))
                return front_matter.get('tags', [])
        return []

    def help(self):
        print("Available commands:")
        print("  ls                     - List all folders and files in the current directory")
        print("  cd <name>              - Change directory to <name> and list its contents")
        print("  cd ..                  - Move to the parent directory")
        print("  open <name>            - Open a Markdown file in '00 - Races' containing <name>' and report issues")
        print("  close                  - Close the currently opened race")
        print("  <race_name> property   - View the properties of the opened race")
        print("  <race_name> content    - View the content of the opened race")
        print("  <race_name> links      - View the links in the opened race")
        print("  <race_name> city       - List all cities in the '02 - Lieux/<race_name>' folder")
        print("  help                   - Show this help message")
        print("  exit                   - Exit the program and clear the screen")

    def run_command(self, command):
        command_parts = command.split(maxsplit=1)
        
        if command_parts[0] in ['ls', 'cd', 'open', 'close', 'help', 'exit']:
            command_method = getattr(self, command_parts[0], None)
            if command_method:
                command_method(*command_parts[1:])
        elif len(command_parts) == 2:
            race_command, action = command_parts
            if action in ['property', 'content', 'links', 'city']:
                command_method = getattr(self, f'race_{action}', None)
                if command_method:
                    command_method(race_command)
        elif len(command_parts) == 1 and self.current_race:
            # If only the action is given, assume it's for the currently opened race
            action = command_parts[0]
            if action in ['property', 'content', 'links', 'city']:
                race_name = self._clean_folder_name(self.current_race.file_name)
                command_method = getattr(self, f'race_{action}', None)
                if command_method:
                    command_method(race_name)
            else:
                print(f"Unknown command: {command}")
        else:
            print(f"Unknown command: {command}")

    def _clean_folder_name(self, folder_name):
        if ' - ' in folder_name:
            return folder_name.split(' - ', 1)[1]
        return folder_name
