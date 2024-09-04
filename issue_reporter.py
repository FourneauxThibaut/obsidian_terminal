import os
from markdown_reader import MarkdownReader
import re
import yaml

class IssueReporter:
    def __init__(self, vault_path):
        self.vault_path = vault_path

    def report_issues(self, race_name):
        print(f"Issues for race '{race_name}':")
        
        race_dir = os.path.join(self.vault_path, "00 - Races", race_name)
        city_dir = os.path.join(self.vault_path, "02 - Lieux", race_name)
        magic_dir = os.path.join(self.vault_path, "01 - Magies")

        if not os.path.isdir(race_dir):
            print(f"Race directory '{race_dir}' does not exist.")
            return
        
        all_h1, all_h2 = self.collect_headers(race_dir)
        self.check_missing_headers(race_dir, all_h1, all_h2)
        self.check_cities_and_capital(race_name, city_dir)
        self.check_magic_links(race_name, magic_dir)

    def collect_headers(self, race_dir):
        """Collects all h1 and h2 headers across all Markdown files in the race directory."""
        all_h1 = set()
        all_h2 = set()

        for root, _, files in os.walk(race_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    reader = MarkdownReader(filepath, self.vault_path)
                    all_h1.update(reader.get_property('h1') or [])
                    all_h2.update(reader.get_property('h2') or [])

        return all_h1, all_h2

    def check_missing_headers(self, race_dir, all_h1, all_h2):
        """Checks each file in the race directory for missing h1 and h2 headers."""
        for root, _, files in os.walk(race_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    reader = MarkdownReader(filepath, self.vault_path)
                    
                    file_h1 = set(reader.get_property('h1') or [])
                    file_h2 = set(reader.get_property('h2') or [])

                    missing_h1 = all_h1 - file_h1
                    missing_h2 = all_h2 - file_h2

                    if missing_h1:
                        print(f"  Missing h1 in file '{file}': {missing_h1}")
                    if missing_h2:
                        print(f"  Missing h2 in file '{file}': {missing_h2}")

    def check_cities_and_capital(self, race_name, city_dir):
        """Checks if the race has at least one city, at least one capital, and more than five cities."""
        if not os.path.exists(city_dir):
            print(f"  No city directory found for race '{race_name}' in '02 - Lieux'.")
            return
        
        cities = []
        has_capital = False

        for file in os.listdir(city_dir):
            if file.endswith('.md'):
                city_name = os.path.splitext(file)[0]
                file_path = os.path.join(city_dir, file)
                tags = self._get_tags_from_file(file_path)
                
                cities.append(city_name)
                if 'capitale' in tags:
                    has_capital = True
        
        if not cities:
            print(f"  No cities found for race '{race_name}' in '02 - Lieux'.")
        if not has_capital:
            print(f"  No capital city found for race '{race_name}' in '02 - Lieux'.")
        if len(cities) < 5:
            print(f"  Fewer than 5 cities found for race '{race_name}'. Current count: {len(cities)}")

    def check_magic_links(self, race_name, magic_dir):
        """Checks if the race file contains links to files in the '01 - Magies' folder."""
        race_file_path = os.path.join(self.vault_path, "00 - Races", race_name, f"{race_name}.md")
        
        if not os.path.isfile(race_file_path):
            print(f"  Race file '{race_file_path}' not found.")
            return
        
        reader = MarkdownReader(race_file_path, self.vault_path)
        links = reader.get_links()

        # Debug output for directory path and existence check
        print(f"Checking magic directory: {magic_dir}")
        if not os.path.exists(magic_dir):
            print(f"  Magic directory '{magic_dir}' does not exist.")
            return
        
        if not os.path.isdir(magic_dir):
            print(f"  Magic directory '{magic_dir}' is not a directory.")
            return

        # Normalize magic files (remove .md extension, lower case)
        magic_files = {os.path.splitext(f)[0].lower(): f for f in os.listdir(magic_dir) if f.endswith('.md')}
        
        # Debug output for magic files
        print(f"Magic files found: {list(magic_files.keys())}")

        linked_magics = []
        
        # Normalize the links and check against the normalized magic files
        for group, link_list in links.items():
            for link in link_list:
                normalized_link = link.lower().strip()
                # Debug output for each link
                print(f"Checking link: '{normalized_link}' against magic files...")
                if normalized_link in magic_files:
                    print(f"Link '{normalized_link}' matches a magic file.")
                    linked_magics.append(normalized_link)

        if not linked_magics:
            print(f"  No links to magic files found in '{race_name}.md'.")
        else:
            # Debug output for linked magic files
            print(f"Linked magic files found: {linked_magics}")

    def _get_tags_from_file(self, file_path):
        """Extracts the tags from the front matter of a Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                front_matter = yaml.safe_load(match.group(1))
                return front_matter.get('tags', [])
        return []
