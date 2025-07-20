# smallt

A tiny terminal-based to-do list designed to live inside your folders — now with a clean TUI-style redraw experience. 

## 📄 How it Works

**smallt** saves your tasks in a simple `tasks.md` file inside the current folder. That means each folder gets its own local list — great for project-specific planning or per-directory reminders.

Your task list is managed interactively in the terminal. Tasks are stored in plain Markdown.

---

## 📦 Installation

[get yanked](https://github.com/codinganovel/yanked)

## 🧰 Interactive Commands

Inside the interactive view, use these commands:

| Command             | Description                           |
|---------------------|---------------------------------------|
| `add <task>`        | Add a new task                        |
| `check <number>`    | Mark a task as complete               |
| `clear`             | Remove all completed tasks            |
| `exit`              | Quit the program                      |

The screen refreshes after every action, giving you a clean, focused task view.

---

## 📝 How It Stores Tasks

Tasks are saved in plain Markdown format inside `tasks.md`, using GitHub-style task checkboxes:
```md
- [ ] Unfinished task
- [x] Completed task
```
This makes the file readable and editable in any Markdown editor.

---

## ✍️ Made with ❤️ by Sam

## 📄 License

under ☕️, check out [the-coffee-license](https://github.com/codinganovel/The-Coffee-License)

I've included both licenses with the repo, do what you know is right. The licensing works by assuming you're operating under good faith.