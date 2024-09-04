import os
import re
import yaml
from collections import defaultdict

class MarkdownReader:
    def __init__(self, filepath, vault_path):
        self.content = defaultdict(lambda: defaultdict(list))  # Hierarchical content structure
        self.property = {}
        self.links = {}  # To store "from -> [to]" links
        self.file_name = os.path.basename(filepath)
        self.base_path = vault_path  # Base path for resolving embeds
        self._parse_file(filepath)

    def _parse_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()

        # Split the file into parts: properties (YAML front matter) and the rest
        match = re.match(r'---\n(.*?)\n---\n(.*)', data, re.DOTALL)
        if match:
            yaml_content = match.group(1)
            markdown_content = match.group(2)

            # Parse the YAML front matter into self.property
            self.property = yaml.safe_load(yaml_content)

            # Parse the Markdown content into self.content and self.links
            self._parse_markdown_content(markdown_content)
        else:
            # No YAML front matter found, just parse the Markdown content
            self._parse_markdown_content(data)

    def _parse_markdown_content(self, content):
        current_group = None
        current_subgroup = None

        for line in content.splitlines():
            if line.startswith('# '):
                current_group = line.strip().lstrip('#').strip()
                self.content[current_group] = defaultdict(list)
                current_subgroup = None  # Reset subgroup when a new group is found

            elif line.startswith('## '):
                current_subgroup = line.strip().lstrip('#').strip()
                self.content[current_group][current_subgroup] = []

            elif line.startswith('### '):
                current_subsubgroup = line.strip().lstrip('#').strip()
                if current_subgroup:
                    self.content[current_group][current_subgroup].append((current_subsubgroup, []))
                else:
                    # If there's no subgroup, treat it as part of the group
                    self.content[current_group][current_subsubgroup] = []

            elif line.strip():  # Only add non-empty lines
                # Extract links of the form ![[link]]
                links = re.findall(r'!\[\[(.*?)\]\]', line)
                if links:
                    for link in links:
                        self.links[current_group] = self.links.get(current_group, []) + [link]
                
                # Add the line to the appropriate group/subgroup
                if current_subgroup:
                    if isinstance(self.content[current_group][current_subgroup], list):
                        self.content[current_group][current_subgroup].append(line)
                    else:
                        self.content[current_group][current_subgroup][-1][1].append(line)
                elif current_group:
                    # Instead of using '_content', assign directly to the group name
                    self.content[current_group][current_group] = self.content[current_group].get(current_group, []) + [line]

    def get_property(self, key):
        return self.property.get(key)

    def get_group_titles(self):
        return list(self.content.keys())

    def get_subgroup_titles(self, group_title):
        return list(self.content[group_title].keys()) if group_title in self.content else []

    def get_content(self, group_title, subgroup_title=None):
        if subgroup_title:
            return self.content[group_title][subgroup_title]
        return self.content[group_title]

    def get_links(self):
        return self.links
