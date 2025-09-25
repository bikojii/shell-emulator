import tkinter as tk
from tkinter import scrolledtext, font
import os
import sys
import shlex
from typing import List, Tuple


class TerminalEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title(self.get_window_title())

        self.current_dir = os.getcwd()

        self.terminal_font = font.Font(family="Courier New", size=10)

        self.create_widgets()

        self.welcome_message()

        self.input_entry.focus_set()

        self.input_entry.bind('<Return>', self.execute_command)

        self.input_entry.bind('<Tab>', self.auto_complete)

        self.command_history = []
        self.history_index = -1

        self.input_entry.bind('<Up>', self.navigate_history_up)
        self.input_entry.bind('<Down>', self.navigate_history_down)

    def get_window_title(self) -> str:
        username = os.getlogin()
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
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
        current_dir = os.path.basename(self.current_dir)
        return f"{username}@{hostname}:{current_dir}$ "

    def welcome_message(self):
        welcome_text = """Добро пожаловать в эмулятор терминала!
Доступные команды:
  ls [аргументы]    - список файлов (заглушка)
  cd [директория]   - сменить директорию (заглушка)
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
        self.print_output(f"ls вызван с аргументами: {args}\n")
        self.print_output("file1.txt  file2.txt  directory/\n")

    def cmd_cd(self, args: List[str]):
        self.print_output(f"cd вызван с аргументами: {args}\n")
        if args:
            new_dir = args[0]
            if new_dir == "..":
                self.current_dir = os.path.dirname(self.current_dir) or "/"
            else:
                self.current_dir = os.path.join(self.current_dir, new_dir)
        else:
            self.current_dir = os.path.expanduser("~")

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


def main():
    root = tk.Tk()
    root.geometry("800x600")

    try:
        root.iconbitmap("terminal.ico")
    except:
        pass

    terminal = TerminalEmulator(root)

    def on_closing():
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()