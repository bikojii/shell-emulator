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

        # Инициализируем current_dir ДО создания виджетов
        self.current_dir = os.getcwd()

        # Настройка шрифта
        self.terminal_font = font.Font(family="Courier New", size=10)

        # Создание виджетов
        self.create_widgets()

        # Приветственное сообщение
        self.welcome_message()

        # Фокус на ввод
        self.input_entry.focus_set()

        # Биндим Enter для выполнения команд
        self.input_entry.bind('<Return>', self.execute_command)

        # Биндим Tab для автодополнения
        self.input_entry.bind('<Tab>', self.auto_complete)

        # История команд
        self.command_history = []
        self.history_index = -1

        # Биндим стрелки для навигации по истории
        self.input_entry.bind('<Up>', self.navigate_history_up)
        self.input_entry.bind('<Down>', self.navigate_history_down)

    def get_window_title(self) -> str:
        """Получаем заголовок окна на основе данных ОС"""
        username = os.getlogin()
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        return f"Эмулятор - [{username}@{hostname}]"

    def create_widgets(self):
        """Создаем интерфейс терминала"""
        # Основной фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Текстовое поле для вывода
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

        # Фрейм для ввода команды
        input_frame = tk.Frame(main_frame, bg='black')
        input_frame.pack(fill=tk.X, pady=(2, 0))

        # Приглашение командной строки
        self.prompt_label = tk.Label(
            input_frame,
            text=self.get_prompt(),
            font=self.terminal_font,
            bg='black',
            fg='green',
            anchor='w'
        )
        self.prompt_label.pack(side=tk.LEFT)

        # Поле ввода команды
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
        """Генерируем приглашение командной строки"""
        username = os.getlogin()
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        current_dir = os.path.basename(self.current_dir)
        return f"{username}@{hostname}:{current_dir}$ "

    def welcome_message(self):
        """Выводим приветственное сообщение"""
        welcome_text = """Добро пожаловать в эмулятор терминала!
Доступные команды:
  ls [аргументы]    - список файлов (заглушка)
  cd [директория]   - сменить директорию (заглушка)
  exit              - выход из эмулятора

Попробуйте ввести команды с аргументами в кавычках!
"""
        self.print_output(welcome_text)

    def print_output(self, text: str):
        """Выводим текст в терминал"""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def update_prompt(self):
        """Обновляем приглашение командной строки"""
        self.prompt_label.config(text=self.get_prompt())

    def parse_command(self, command: str) -> Tuple[str, List[str]]:
        """Парсим команду с поддержкой кавычек"""
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
        """Выполняем команду"""
        command = self.input_entry.get().strip()

        if not command:
            self.input_entry.delete(0, tk.END)
            return

        # Добавляем в историю
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Показываем команду в выводе
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

        # Очищаем поле ввода
        self.input_entry.delete(0, tk.END)

        return "break"  # Предотвращаем распространение события

    def cmd_ls(self, args: List[str]):
        """Заглушка для команды ls"""
        self.print_output(f"ls вызван с аргументами: {args}\n")
        self.print_output("file1.txt  file2.txt  directory/\n")

    def cmd_cd(self, args: List[str]):
        """Заглушка для команды cd"""
        self.print_output(f"cd вызван с аргументами: {args}\n")
        if args:
            new_dir = args[0]
            if new_dir == "..":
                # Имитация перехода на уровень выше
                self.current_dir = os.path.dirname(self.current_dir) or "/"
            else:
                # Имитация перехода в директорию
                self.current_dir = os.path.join(self.current_dir, new_dir)
        else:
            # Переход в домашнюю директорию
            self.current_dir = os.path.expanduser("~")

        self.update_prompt()

    def auto_complete(self, event):
        """Заглушка для автодополнения"""
        return "break"  # Пока просто блокируем стандартное поведение

    def navigate_history_up(self, event):
        """Навигация вверх по истории команд"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def navigate_history_down(self, event):
        """Навигация вниз по истории команд"""
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

    # Устанавливаем иконку (если есть)
    try:
        root.iconbitmap("terminal.ico")  # Можно добавить иконку
    except:
        pass

    terminal = TerminalEmulator(root)

    # Обработка закрытия окна
    def on_closing():
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()