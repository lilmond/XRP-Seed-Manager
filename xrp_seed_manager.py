from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from getpass import getpass
import base64
import json
import sys
import os

class Colors:
    italic = "\u001b[0;3m"
    underline = "\u001b[0;4m"
    blink = "\u001b[0;5m"
    red = "\u001b[31;1m"
    green = "\u001b[32;1m"
    yellow = "\u001b[33;1m"
    blue = "\u001b[34;1m"
    purple = "\u001b[35;1m"
    cyan = "\u001b[36;1m"
    reset = "\u001b[0;0m"


class XRPSeedManager(object):
    def __init__(self):
        self.seeds_folder = "./.xrp_seeds"

        if not os.path.exists(self.seeds_folder):
            os.mkdir(self.seeds_folder)

        self.menus = {
            "Main Menu": {
                "1": ("Create seed file", self.create_seed_file), 
                "2": ("Modify seed file", self.modify_seed_file),
                "3": ("Delete seed file", self.delete_seed_file),
                "0": ("Exit", None)
            },
            "Seed File Menu": {
                "1": ("Add new seeds", self.add_new_seed),
                "2": ("Remove seeds", self.remove_seed),
                "3": ("Show seeds", self.show_seeds),
                "4": ("Save seeds", self.save_seeds),
                "0": ("Main Menu", None)
            }
        }

    def start(self):
        while True:
            self.clear_console()
            option = self.show_menu("Main Menu")
            if not option:
                return
            self.clear_console()
            option()

    def show_menu(self, menu_name):
        if not menu_name in self.menus:
            raise Exception("Menu name does not exist")
        
        menu = self.menus[menu_name]
        valid_options = []
        
        print(f"{Colors.underline}{Colors.purple}{menu_name}{Colors.reset}")

        for option in menu:
            description, function = menu[option]
            valid_options.append(option)
            print(f"{Colors.cyan}{option}{Colors.reset} ~ {description}")
        
        print("")
        
        while True:
            user_option = input(f"{Colors.cyan}Select>{Colors.reset} ")

            if not user_option in valid_options:
                self.show_error("This option does not exist.\n")
                continue

            break
        
        print("")

        return menu[user_option][1]

    def show_error(self, message: str):
        print(f"{Colors.italic}{Colors.red}ERROR:{Colors.reset} {message}")

    def show_success(self, message: str):
        print(f"{Colors.italic}{Colors.green}SUCCESS:{Colors.reset} {message}")
    
    def encrypt_data(self, data: str, password: str):
        salt = os.urandom(16)
        iv = os.urandom(16)
        key = PBKDF2(password, salt, dkLen=32, count=200000)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(data.encode(), AES.block_size))
        out = base64.b64encode(salt + iv + ct)

        return out

    def decrypt_data(self, data: str, password: str):
        raw = base64.b64decode(data)
        salt = raw[:16]
        iv = raw[16:32]
        ct = raw[32:]

        key = PBKDF2(password, salt, dkLen=32, count=200000)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)

        return pt.decode()

    def read_file(self, file: str, password: str):
        with open(file, "r") as file:
            content = file.read()
            decrypted_content = self.decrypt_data(data=content, password=password)
            file.close()
        
        return decrypted_content

    def write_file(self, file: str, password: str, content: str):
        encrypted_content = self.encrypt_data(data=content, password=password)

        with open(file, "w") as file:
            file.write(encrypted_content.decode())
            file.close()

    def decrypt_seeds(self, seed_file: str, password: str):
        return json.loads(self.read_file(file=seed_file, password=password))

    def create_seed_file(self):
        print(f"{Colors.underline}{Colors.purple}Create Seed File{Colors.reset}")

        while True:
            filename = input(f"{Colors.cyan}Seed File Name:{Colors.reset} ")
            file_path = f"{self.seeds_folder}/{filename}.xrpseed"
            
            if os.path.exists(file_path):
                self.show_error("This filename already exists.\n")
                continue

            break

        print("")

        while True:
            password = getpass(f"{Colors.cyan}Encryption Password: {Colors.reset}")
            print("")
            password_confirm = getpass(f"{Colors.cyan}Confirm Encryption Password: {Colors.reset}")

            if password != password_confirm:
                self.show_error("Encryption password does not match.\n")
                continue
            break

        self.write_file(file_path, password=password, content="[]")
        self.show_success("Successfully created seed file.\n")
        self.enter_continue()

    def modify_seed_file(self):
        seed_options = {}
        option_number = 1

        print(f"{Colors.underline}{Colors.purple}Seed Files:{Colors.reset}")
        for file in os.listdir(self.seeds_folder):
            print(f"{Colors.cyan}{option_number}{Colors.reset} ~ {file}")
            seed_options[str(option_number)] = file
            option_number += 1

        print("")

        while True:
            user_select = input(f"{Colors.cyan}Select>{Colors.reset} ")

            if not user_select in seed_options:
                self.show_error("Invalid option.")
                continue
            break

        seed_file = seed_options[user_select]
        seed_path = f"{self.seeds_folder}/{seed_file}"
        self.show_success(f"Selected seed file: {Colors.underline}{Colors.yellow}{seed_file}{Colors.reset}")
        print("")

        
        while True:
            password = getpass(f"{Colors.cyan}Decryption Password:{Colors.reset} ")

            try:
                seeds = self.decrypt_seeds(seed_file=seed_path, password=password)
            except Exception:
                self.show_error("Wrong decryption password.\n")
                continue

            self.show_success("Successfully decrypted seed file.\n")
            self.enter_continue()
            break

        while True:
            self.clear_console()
            option = self.show_menu("Seed File Menu")
            self.clear_console()

            if option in [self.add_new_seed, self.remove_seed, self.show_seeds]:
                args = (seeds,)
            elif option == self.save_seeds:
                args = (seed_path, password, seeds)
            elif option == None:
                return

            option(*args)

    def delete_seed_file(self):
        print(f"{Colors.underline}{Colors.purple}Delete Seed File{Colors.reset}")
    
        valid_selections = {}
        for i, file in enumerate(os.listdir(self.seeds_folder), start=1):
            valid_selections[str(i)] = file
            print(f"{Colors.cyan}{i}{Colors.reset} ~ {file}")
        
        print(f"\nSelect seed files to be deleted by their numbers, separated by comma (,).")
        user_select = input(f"{Colors.cyan}:{Colors.reset}").replace(" ", "").split(",")

        confirmation = input(f"\n{Colors.blink}{Colors.yellow}WARNING:{Colors.reset} Are you sure you want to delete the selected files? This action is irreversible. {Colors.blink}{Colors.cyan}[Y/n]{Colors.reset}: ").lower()
        if not confirmation == "y":
            print("")
            self.show_error(f"User cancelled the action.\n")
            self.enter_continue()
            return
        
        print("")

        deleted_seed_files = 0

        for number in user_select:
            if number in valid_selections:
                filename = valid_selections[number]
                file_path = f"{self.seeds_folder}/{filename}"
                os.remove(file_path)
                deleted_seed_files += 1
            else:
                self.show_error(f"{number} is not in the selection.\n")
        
        self.show_success(f"Deleted {deleted_seed_files} seed files.\n")
        self.enter_continue()

    def add_new_seed(self, seeds: list):
        print(f"Press {Colors.blink}{Colors.cyan}<ENTER>{Colors.reset} for each seed. Type blank to stop adding.")

        added_seeds = 0

        while True:
            seed_input = input(f"{Colors.cyan}:{Colors.reset}").strip()

            if not seed_input:
                break

            if seed_input in seeds:
                self.show_error(f"{seed_input} is already in the seed list.\n")
                continue
            
            seeds.append(seed_input)
            added_seeds += 1
        
        self.show_success(f"Added {added_seeds} seeds. Don't forget to save.\n")
        self.enter_continue()

    def remove_seed(self, seeds: list):
        seed_options = {}

        print(f"{Colors.underline}{Colors.purple}Remove Seeds{Colors.reset}")
        for i, seed in enumerate(seeds, start=1):
            print(f"{Colors.cyan}{i}{Colors.reset} ~ {seed}")
            seed_options[str(i)] = seed

        print(f"\nSelect seeds that you want to be removed by typing their numbers, separated by comma (,).")
        remove_seeds = input(f"{Colors.cyan}:{Colors.reset} ").replace(" ", "").split(",")
        
        removed_seeds = 0
        for number in remove_seeds:
            if number in seed_options:
                seed = seed_options[number]
                seeds.remove(seed)
                removed_seeds += 1
            else:
                self.show_error(f"{number} is not in the seed options.")
        
        self.show_success(f"Removed: {removed_seeds} seeds. Don't forget to save.\n")
        self.enter_continue()

    def show_seeds(self, seeds: list):
        print(f"{Colors.underline}{Colors.purple}Show Seeds{Colors.reset}")

        if not seeds:
            self.show_error("No seeds have been added here yet.\n")
            self.enter_continue()
            return

        seeds_count = 0
        for seed in seeds:
            print(seed)
            seeds_count += 1
        
        print(f"\nSeeds Count: {seeds_count}\n")

        self.enter_continue()
    
    def save_seeds(self, seed_file: str, password: str, seeds: list):
        print(f"{Colors.underline}{Colors.purple}Save Seeds{Colors.reset}")

        confirmation = input(f"{Colors.blink}{Colors.yellow}WARNING:{Colors.reset} Are you sure you want to save {len(seeds)} seeds to {Colors.yellow}{seed_file}{Colors.reset}? Any modify action is irreversible. {Colors.blink}{Colors.cyan}[Y/n]{Colors.reset}: ").lower()
        print("")
        if not confirmation == "y":
            self.show_error("User cancelled the action.\n")
            self.enter_continue()
            return

        self.write_file(file=seed_file, password=password, content=json.dumps(seeds))
        self.show_success(f"{len(seeds)} seeds have been saved.\n")
        self.enter_continue()
    
    def clear_console(self):
        if sys.platform in ["linux", "linux2"]:
            os.system("clear")
        elif sys.platform == "win32":
            os.system("cls")
    
    def enter_continue(self):
        input(f"- Press {Colors.blink}{Colors.cyan}<ENTER>{Colors.reset} to continue. -{Colors.reset}")

def main():
    seed_manager = XRPSeedManager()
    seed_manager.clear_console()

    try:
        seed_manager.start()
    except KeyboardInterrupt:
        return
    
if __name__ == "__main__":
    main()
