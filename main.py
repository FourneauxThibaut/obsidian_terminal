from vault_manager import VaultManager
import readline
import os

vault_path = 'Gladion Vault'
vault_manager = VaultManager(vault_path)

BASE_COMMANDS = ['ls', 'cd', 'open', 'close', 'property', 'content', 'links', 'city', 'help', 'exit']                 
 
def completer(text, state):
    buffer = readline.get_line_buffer()
    line = buffer.split()

    # If no text is typed yet
    if not line:
        return [cmd + ' ' for cmd in BASE_COMMANDS][state]

    # Autocomplete base commands
    if len(line) == 1:
        matches = [cmd for cmd in BASE_COMMANDS if cmd.startswith(text)]
    else:
        # Handle subcommands like 'cd' and 'race'
        if line[0] == 'cd':
            path = line[1] if len(line) > 1 else ''
            matches = [d + '/' for d in os.listdir(vault_manager.current_path) if d.startswith(path)]
        elif line[0] == 'open' and len(line) == 2:
            race_path = os.path.join(vault_path, "00 - Races")
            matches = [f[:-3] for f in os.listdir(race_path) if f.lower().startswith(line[1].lower()) and f.endswith('.md')]
        else:
            matches = []

    try:
        return matches[state]
    except IndexError:
        return None
    
readline.set_completer(completer)
readline.parse_and_bind('tab: complete')

def main():
    while True:
        if vault_manager.current_race:
            race_name = os.path.splitext(vault_manager.current_race.file_name)[0]
            command = input(f"\nVaultManager [{race_name}]: ").strip().lower()
        else:
            command = input("\nVaultManager: ").strip().lower()
        
        if command == 'exit':
            print("Exiting the program.")
            break
        else:
            print(f"\n")
            vault_manager.run_command(command)

if __name__ == "__main__":
    main()
