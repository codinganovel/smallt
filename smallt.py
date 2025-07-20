#!/usr/bin/env python3
"""Enhanced CLI version of **smallt** with improved robustness and new features.

A very small task‑list utility that writes to `tasks.md`.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Optional

TASK_FILE = "tasks.md"

# ────────────────────────────────────────────────────────────────────────────
# Blue theme colors
# ────────────────────────────────────────────────────────────────────────────

class Colors:
    """ANSI color codes for blue theme."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Blue theme palette
    BLUE = "\033[34m"
    LIGHT_BLUE = "\033[94m"
    CYAN = "\033[36m"
    LIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    
    # Status colors
    SUCCESS = "\033[92m"  # Green
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"    # Red


def colored(text: str, color: str) -> str:
    """Return colored text."""
    return f"{color}{text}{Colors.RESET}"


def blue_header(text: str) -> str:
    """Return blue header text."""
    return colored(text, Colors.BOLD + Colors.LIGHT_BLUE)


def task_text(text: str, completed: bool = False) -> str:
    """Return properly colored task text."""
    if completed:
        return colored(text, Colors.DIM + Colors.GRAY)
    return colored(text, Colors.RESET)  # Default terminal color (readable on any background)


def status_text(text: str) -> str:
    """Return colored status text based on emoji prefix."""
    if text.startswith("✅") or text.startswith("☑️") or text.startswith("🧹") or text.startswith("🗑️"):
        return colored(text, Colors.SUCCESS)
    elif text.startswith("⚠️"):
        return colored(text, Colors.WARNING)
    elif text.startswith("❌"):
        return colored(text, Colors.ERROR)
    else:
        return colored(text, Colors.CYAN)

# ────────────────────────────────────────────────────────────────────────────
# Storage helpers
# ────────────────────────────────────────────────────────────────────────────

def ensure_task_file() -> None:
    """Create or repair the markdown file if it doesn't exist or is malformed."""
    task_path = Path(TASK_FILE)
    
    if not task_path.exists():
        task_path.write_text("# Task List\n\n")
        return
    
    # Check if file exists but is empty or malformed
    try:
        content = task_path.read_text().strip()
        if not content or not content.startswith("# Task List"):
            # Preserve existing tasks if any, but fix header
            existing_tasks = [line for line in content.splitlines() if line.startswith("- [")]
            new_content = "# Task List\n\n"
            if existing_tasks:
                new_content += "\n".join(existing_tasks) + "\n"
            task_path.write_text(new_content)
    except (OSError, UnicodeDecodeError):
        # File is corrupted, recreate it
        task_path.write_text("# Task List\n\n")


def load_tasks() -> List[str]:
    """Return all lines of the task file, with error handling."""
    try:
        return Path(TASK_FILE).read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        # File issue, recreate and return empty
        ensure_task_file()
        return ["# Task List", ""]


def save_tasks(lines: List[str]) -> bool:
    """Overwrite the task file with given lines. Returns True on success."""
    try:
        Path(TASK_FILE).write_text("\n".join(lines) + "\n")
        return True
    except OSError:
        return False

# ────────────────────────────────────────────────────────────────────────────
# Core operations
# ────────────────────────────────────────────────────────────────────────────

def list_tasks() -> List[str]:
    """Return numbered task strings (markdown list items) with blue theme."""
    tasks = [line for line in load_tasks() if line.startswith("- [")]
    colored_tasks = []
    
    for i, line in enumerate(tasks):
        number = colored(f"{i+1}.", Colors.BOLD + Colors.LIGHT_BLUE)
        completed = "[x]" in line.lower()
        task_content = task_text(line, completed)
        colored_tasks.append(f"{number} {task_content}")
    
    return colored_tasks


def add_task(task_text: str) -> str:
    """Add a new task to the file."""
    if not task_text.strip():
        return "❌ Task cannot be empty."
    
    try:
        with Path(TASK_FILE).open("a", encoding="utf-8") as f:
            f.write(f"- [ ] {task_text.strip()}\n")
        return f"✅ Added: {task_text.strip()}"
    except OSError:
        return "❌ Failed to add task (file error)."


def check_task(index: int) -> str:
    """Mark a task as completed."""
    lines = load_tasks()
    task_lines = [i for i, l in enumerate(lines) if l.startswith("- [")]

    if index < 1 or index > len(task_lines):
        return "❌ Task not found."

    real_idx = task_lines[index - 1]
    line = lines[real_idx]

    if "[x]" in line.lower():
        return "⚠️ Already completed."

    lines[real_idx] = line.replace("[ ]", "[x]", 1)
    if save_tasks(lines):
        return f"☑️ Checked off task #{index}"
    else:
        return "❌ Failed to save changes."


def delete_task(index: int) -> str:
    """Delete a specific task by number."""
    lines = load_tasks()
    task_lines = [i for i, l in enumerate(lines) if l.startswith("- [")]
    
    if index < 1 or index > len(task_lines):
        return "❌ Task not found."
    
    real_idx = task_lines[index - 1]
    task_text = lines[real_idx].replace("- [ ]", "").replace("- [x]", "").replace("- [X]", "").strip()
    del lines[real_idx]
    
    if save_tasks(lines):
        return f"🗑️ Deleted: {task_text}"
    else:
        return "❌ Failed to delete task."


def clear_done_tasks() -> str:
    """Remove all completed tasks."""
    lines = load_tasks()
    original_count = len([l for l in lines if l.startswith("- [x]")])
    new_lines = [l for l in lines if not l.startswith("- [x]")]
    
    if save_tasks(new_lines):
        return f"🧹 Cleared {original_count} completed task(s)."
    else:
        return "❌ Failed to clear tasks."


def clear_all_tasks() -> str:
    """Remove ALL tasks (completed and incomplete)."""
    lines = load_tasks()
    task_count = len([l for l in lines if l.startswith("- [")])
    new_lines = [l for l in lines if not l.startswith("- [")]
    
    if task_count == 0:
        return "⚠️ No tasks to clear."
    
    if save_tasks(new_lines):
        return f"🗑️ Cleared all {task_count} task(s)."
    else:
        return "❌ Failed to clear tasks."

# ────────────────────────────────────────────────────────────────────────────
# TUI‑style interactive shell
# ────────────────────────────────────────────────────────────────────────────

def redraw(status: Optional[str] = None) -> None:
    """Clear the screen and render tasks + prompt info with blue theme."""
    os.system("cls" if os.name == "nt" else "clear")
    
    # Blue themed header with decorative borders
    header = "═══════════════════════════════════════════"
    print(colored(header, Colors.BLUE))
    print(blue_header("           📋 smallt task manager"))
    print(colored(header, Colors.BLUE))
    print()
    
    tasks = list_tasks()
    if tasks:
        print("\n".join(tasks))
    else:
        print(colored("   No tasks yet. Add one to get started!", Colors.DIM + Colors.CYAN))

    if status:
        print(f"\n{status_text(status)}")

    # Blue themed command help
    print(f"\n{colored('Commands:', Colors.BOLD + Colors.LIGHT_CYAN)}")
    commands = [
        ("add <task>", "Add a new task"),
        ("check <number>", "Mark task as complete"),
        ("delete <number>", "Delete a specific task"),
        ("clear", "Remove completed tasks"),
        ("clearall", "Remove ALL tasks"),
        ("list", "Refresh task list"),
        ("exit", "Quit program")
    ]
    
    for cmd, desc in commands:
        cmd_colored = colored(cmd, Colors.BOLD + Colors.CYAN)
        desc_colored = colored(desc, Colors.GRAY)
        print(f"  {cmd_colored:<20} {desc_colored}")
    
    print(f"\n{colored('>', Colors.BOLD + Colors.LIGHT_BLUE)} ", end="")


def run_shell() -> None:
    """Run the interactive shell."""
    ensure_task_file()
    status_msg: Optional[str] = None

    while True:
        redraw(status_msg)
        status_msg = None  # reset after displaying once
        try:
            command = input("").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{colored('👋 Goodbye!', Colors.LIGHT_BLUE)}")
            break

        if command == "exit":
            break
        elif command.startswith("add "):
            task = " ".join(command.split()[1:])  # Better parsing
            status_msg = add_task(task)
        elif command.startswith("check "):
            try:
                idx = int(command.split()[1])
                status_msg = check_task(idx)
            except (ValueError, IndexError):
                status_msg = "❌ Invalid number."
        elif command.startswith("delete "):
            try:
                idx = int(command.split()[1])
                status_msg = delete_task(idx)
            except (ValueError, IndexError):
                status_msg = "❌ Invalid number."
        elif command == "clear":
            status_msg = clear_done_tasks()
        elif command == "clearall":
            # Ask for confirmation for destructive action
            try:
                print(f"{colored('⚠️  This will delete ALL tasks. Continue?', Colors.WARNING)} ", end="")
                confirm = input(f"{colored('(y/N):', Colors.BOLD + Colors.CYAN)} ").strip().lower()
                if confirm == 'y':
                    status_msg = clear_all_tasks()
                else:
                    status_msg = "❌ Cancelled."
            except (EOFError, KeyboardInterrupt):
                status_msg = "❌ Cancelled."
        elif command == "list":
            # Just redraw (tasks are already shown)
            status_msg = None
        else:
            status_msg = "❓ Unknown command."

        # Brief pause for error messages
        if status_msg and status_msg.startswith("❌"):
            time.sleep(1.5)

# ────────────────────────────────────────────────────────────────────────────
# One‑shot CLI mode or interactive shell
# ────────────────────────────────────────────────────────────────────────────

def print_help() -> None:
    """Print usage information with blue theme."""
    print(blue_header("smallt - A tiny task manager"))
    print(f"\n{colored('Usage:', Colors.BOLD + Colors.CYAN)}")
    print(f"  {colored('smallt', Colors.LIGHT_BLUE)}              {colored('# Launch interactive mode', Colors.GRAY)}")
    print(f"  {colored('smallt add <task>', Colors.LIGHT_BLUE)}   {colored('# Add a task', Colors.GRAY)}")
    print(f"  {colored('smallt list', Colors.LIGHT_BLUE)}         {colored('# Show all tasks', Colors.GRAY)}")
    print(f"  {colored('smallt help', Colors.LIGHT_BLUE)}         {colored('# Show this help', Colors.GRAY)}")


def main() -> None:
    """Main entry point."""
    ensure_task_file()
    args = sys.argv[1:]
    
    if not args:
        run_shell()
    elif args[0] == "add":
        task_text = " ".join(args[1:])
        print(add_task(task_text))
    elif args[0] == "list":
        tasks = list_tasks()
        if tasks:
            print("\n".join(tasks))
        else:
            print("No tasks yet.")
    elif args[0] in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"❌ Unknown command: {args[0]}")
        print("Use 'smallt help' for usage information.")


if __name__ == "__main__":
    main()