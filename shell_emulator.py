import tkinter as tk
from tkinter import scrolledtext, font
import os
import sys
import shlex
from typing import List, Tuple
import getpass
import platform
import json
import base64




class TerminalEmulator:
    def __init__(self, root, vfs_path=None, startup_script=None):
        self.root = root

        self.vfs_path = vfs_path or os.getcwd()

        self.startup_script = startup_script

        self.current_dir = self.vfs_path

        self.root.title(self.get_window_title())

        self.current_dir = "/"

        self.terminal_font = font.Font(family="Courier New", size=10)

        self.create_widgets()

        self.welcome_message()

        self.vfs = {}
        if self.vfs_path:
            self.load_vfs(self.vfs_path)
        else:
            # VFS по умолчанию, если файл не указан
            self.vfs = {
                "type": "dir",
                "name": "/",
                "children": {
                    "file1.txt": {
                        "type": "file",
                        "name": "file1.txt",
                        "content": "SGVsbG8gd29ybGQh"  # base64
                    },
                    "docs": {
                        "type": "dir",
                        "name": "docs",
                        "children": {
                            "readme.txt": {
                                "type": "file",
                                "name": "readme.txt",
                                "content": "VGhpcyBpcyBhIHJlYWRtZSBmaWxlLg=="
                            },
                            "images": {
                                "type": "dir",
                                "name": "images",
                                "children": {}
                            }
                        }
                    },
                    "projects": {
                        "type": "dir",
                        "name": "projects",
                        "children": {
                            "project1": {
                                "type": "dir",
                                "name": "project1",
                                "children": {
                                    "main.py": {
                                        "type": "file",
                                        "name": "main.py",
                                        "content": "cHJpbnQoIkhlbGxvIFByb2plY3QhIik="
                                    }
                                }
                            }
                        }
                    }
                }
            }

        self.input_entry.focus_set()

        self.input_entry.bind('<Return>', self.execute_command)

        self.input_entry.bind('<Tab>', self.auto_complete)

        self.command_history = []
        self.history_index = -1

        self.input_entry.bind('<Up>', self.navigate_history_up)
        self.input_entry.bind('<Down>', self.navigate_history_down)

        self.print_output(f"[DEBUG] VFS Path: {self.vfs_path}\n")
        self.print_output(f"[DEBUG] Startup Script: {self.startup_script}\n")

        if self.startup_script:
            self.run_startup_script(self.startup_script)

    def get_window_title(self) -> str:
        username = getpass.getuser()
        hostname = platform.node()
        return f"Эмулятор - [{username}@{hostname}]"

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.output_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=self.terminal_font,
            bg='black',
            fg='white',
            insertbackground='white',
            state='disabled'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(main_frame, bg='black')
        input_frame.pack(fill=tk.X, pady=(2, 0))

        self.prompt_label = tk.Label(
            input_frame,
            text=self.get_prompt(),
            font=self.terminal_font,
            bg='black',
            fg='green',
            anchor='w'
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            input_frame,
            font=self.terminal_font,
            bg='black',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

    def get_prompt(self) -> str:
        username = os.getlogin()
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        current_dir = self.current_dir.strip("/") or "/"
        return f"{username}@{hostname}:{current_dir}$ "

    def welcome_message(self):
        welcome_text = """Добро пожаловать в эмулятор терминала!
Доступные команды:
  ls [аргументы]    - список файлов 
  cd [директория]   - сменить директорию
  exit              - выход из эмулятора

Попробуйте ввести команды с аргументами в кавычках!
"""
        self.print_output(welcome_text)

    def print_output(self, text: str):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def update_prompt(self):
        self.prompt_label.config(text=self.get_prompt())

    def parse_command(self, command: str) -> Tuple[str, List[str]]:
        try:
            parts = shlex.split(command)
            if not parts:
                return "", []
            cmd = parts[0]
            args = parts[1:]
            return cmd, args
        except ValueError as e:
            raise Exception(f"Ошибка парсинга: {str(e)}")

    def execute_command(self, event=None):
        command = self.input_entry.get().strip()

        if not command:
            self.input_entry.delete(0, tk.END)
            return

        self.command_history.append(command)
        self.history_index = len(self.command_history)

        self.print_output(f"{self.get_prompt()}{command}\n")

        try:
            cmd, args = self.parse_command(command)

            if cmd == "exit":
                self.root.quit()

            elif cmd == "ls":
                self.cmd_ls(args)

            elif cmd == "cd":
                self.cmd_cd(args)

            elif cmd:
                self.print_output(f"Команда '{cmd}' не найдена\n")

        except Exception as e:
            self.print_output(f"Ошибка: {str(e)}\n")

        self.input_entry.delete(0, tk.END)

        return "break"

    def cmd_ls(self, args: List[str]):
        target_path = self.current_dir if not args else args[0]
        node = self.get_node_by_path(target_path)
        if not node or node["type"] != "dir":
            self.print_output(f"ls: путь '{target_path}' не найден\n")
            return
        items = "  ".join(node["children"].keys())
        self.print_output(f"{items}\n")


    def cmd_cd(self, args: List[str]):
        if not args:
            self.current_dir = "/"
        else:
            new_path = args[0]
            if new_path.startswith("/"):
                abs_path = new_path
            elif new_path == "..":
                abs_path = "/" if self.current_dir == "/" else "/".join(
                    self.current_dir.rstrip("/").split("/")[:-1]) or "/"
            else:
                abs_path = (self.current_dir.rstrip("/") + "/" + new_path).replace("//", "/")

            node = self.get_node_by_path(abs_path)
            if node and node["type"] == "dir":
                self.current_dir = abs_path
            else:
                self.print_output(f"cd: путь '{new_path}' не найден\n")
        self.update_prompt()

    def auto_complete(self, event):
        return "break"

    def navigate_history_up(self, event):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def navigate_history_down(self, event):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
        return "break"

    def run_startup_script(self, script_path):
        if not os.path.isfile(script_path):
            self.print_output(f"Ошибка: стартовый скрипт '{script_path}' не найден\n")
            return
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.print_output(f"{self.get_prompt()}{line}\n")
                    try:
                        self.execute_command_from_script(line)
                    except Exception as e:
                        self.print_output(f"[Ошибка в скрипте] {str(e)}\n")
        except Exception as e:
            self.print_output(f"Ошибка при чтении скрипта: {str(e)}\n")

    def execute_command_from_script(self, command: str):
        cmd, args = self.parse_command(command)
        if cmd == "exit":
            self.root.quit()
        elif cmd == "ls":
            self.cmd_ls(args)
        elif cmd == "cd":
            self.cmd_cd(args)
        elif cmd:
            self.print_output(f"Команда '{cmd}' не найдена\n")

    def load_vfs(self, vfs_path):
        if not os.path.isfile(vfs_path):
            self.print_output(f"Ошибка: файл VFS '{vfs_path}' не найден\n")
            self.vfs = {"type": "dir", "name": "/", "children": {}}
            return
        try:
            with open(vfs_path, "r", encoding="utf-8") as f:
                self.vfs = json.load(f)
        except Exception as e:
            self.print_output(f"Ошибка при загрузке VFS: {str(e)}\n")
            self.vfs = {"type": "dir", "name": "/", "children": {}}

    def get_node_by_path(self, path: str):
        path = path.replace("\\", "/")

        if not path.startswith("/"):
            if self.current_dir == "/":
                path = "/" + path
            else:
                path = self.current_dir.rstrip("/") + "/" + path

        parts = path.strip("/").split("/")
        node = self.vfs
        for part in parts:
            if part == "":
                continue
            if node["type"] != "dir" or part not in node["children"]:
                return None
            node = node["children"][part]
        return node

    def read_file_content(self, path: str) -> str:
        node = self.get_node_by_path(path)
        if not node or node["type"] != "file":
            self.print_output(f"Ошибка: файл '{path}' не найден\n")
            return ""
        try:
            content_bytes = base64.b64decode(node["content"])
            return content_bytes.decode("utf-8")
        except Exception as e:
            self.print_output(f"Ошибка чтения файла '{path}': {str(e)}\n")
            return ""


def main():
    vfs_path = None
    startup_script = None

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--vfs='):
                vfs_path = arg.split('=', 1)[1]
            elif arg.startswith('--script='):
                startup_script = arg.split('=', 1)[1]

    root = tk.Tk()
    root.geometry("800x600")

    try:
        root.iconbitmap("terminal.ico")
    except:
        pass

    terminal = TerminalEmulator(root, vfs_path=vfs_path, startup_script=startup_script)

    def on_closing():
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()



if __name__ == "__main__":
    main()