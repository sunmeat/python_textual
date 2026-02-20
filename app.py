from textual.app import App, ComposeResult, on
from textual.widgets import (
    Header, Footer, DataTable, Input, Button, Static, Label,
    Footer, ListView, ListItem
)
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual import events

from model import Task, TaskModel


class AddTaskScreen(ModalScreen[str]):
    """Модальне вікно для додавання нового завдання"""

    CSS = """
    AddTaskScreen {
        align: center middle;
    }
    Input {
        margin: 1;
        width: 60%;
    }
    Horizontal {
        height: auto;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Введіть опис завдання:", id="prompt")
        yield Input(placeholder="Опис...", id="task-input")
        with Horizontal():
            yield Button("Додати", variant="primary", id="add")
            yield Button("Скасувати", variant="error", id="cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    @on(Button.Pressed, "#add")
    def add_pressed(self) -> None:
        input_widget = self.query_one(Input)
        self.dismiss(input_widget.value.strip())

    @on(Button.Pressed, "#cancel")
    def cancel_pressed(self) -> None:
        self.dismiss(None)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)


class ConfirmDeleteScreen(ModalScreen[int | None]):
    """Підтвердження видалення"""

    def __init__(self, index: int, description: str):
        super().__init__()
        self.index = index
        self.description = description

    def compose(self) -> ComposeResult:
        yield Label(f"Видалити завдання?\n\n{self.description}", id="prompt")
        with Horizontal():
            yield Button("Так, видалити", variant="error", id="yes")
            yield Button("Скасувати", variant="primary", id="no")

    @on(Button.Pressed, "#yes")
    def confirm(self) -> None:
        self.dismiss(self.index)

    @on(Button.Pressed, "#no")
    def cancel(self) -> None:
        self.dismiss(None)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)


class TodoApp(App):
    """To-Do List на Textual"""

    CSS = """
    DataTable {
        height: 1fr;
    }
    .status {
        width: 8;
        content-align: center middle;
    }
    .done {
        color: $success;
    }
    .pending {
        color: $text-muted;
    }
    Input {
        margin: 1 2;
    }
    Footer {
        background: $accent;
    }
    """

    BINDINGS = [
        ("a", "add_task", "Додати завдання"),
        ("d", "mark_done", "Позначити виконане"),
        ("x", "delete_task", "Видалити завдання"),
        ("r", "refresh", "Оновити"),
        ("t", "toggle_dark", "Темна/світла тема"),
        ("q", "quit", "Вихід"),
    ]

    model = reactive(TaskModel(), layout=True, init=False)

    def __init__(self):
        super().__init__()
        self.model = TaskModel()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(id="tasks-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Список завдань"
        self.sub_title = "To-Do List (Textual)"

        table = self.query_one(DataTable)
        table.add_columns(
            ("#", "right"),
            ("Статус", "center"),
            ("Опис", "left"),
        )
        table.zebra_stripes = True
        table.cursor_type = "row"
        table.show_cursor = True
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        tasks = self.model.get_all_tasks()
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.done else "—"
            style = "done" if task.done else "pending"
            table.add_row(
                str(i),
                f"[{style}]{status}[/{style}]",
                task.description,
                key=f"task-{i}"
            )

        if not tasks:
            table.add_row("", "[yellow]Список порожній[/yellow]", "")

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        # можна додати дію при виборі рядка (наприклад, показати деталі)
        pass

    def action_add_task(self) -> None:
        def callback(description: str | None) -> None:
            if description:
                if self.model.add_task(description):
                    self.notify("Завдання додано!", severity="success")
                else:
                    self.notify("Опис не може бути порожнім", severity="error")
                self.refresh_table()

        self.push_screen(AddTaskScreen(), callback)

    def action_mark_done(self) -> None:
        table = self.query_one(DataTable)
        row_key = table.cursor_row_key
        if not row_key:
            self.notify("Виберіть завдання", severity="warning")
            return

        # row_key = "task-5", index = 4
        try:
            idx = int(str(row_key).split("-")[1]) - 1
            if self.model.mark_done(idx):
                self.notify("Позначено як виконане!", severity="success")
                self.refresh_table()
            else:
                self.notify("Невірний номер", severity="error")
        except (ValueError, IndexError):
            self.notify("Помилка при позначенні", severity="error")

    def action_delete_task(self) -> None:
        table = self.query_one(DataTable)
        row_key = table.cursor_row_key
        if not row_key:
            self.notify("Виберіть завдання", severity="warning")
            return

        try:
            idx = int(str(row_key).split("-")[1]) - 1
            task = self.model.get_all_tasks()[idx]
            def confirm_delete(result: int | None) -> None:
                if result is not None:
                    if self.model.delete_task(result):
                        self.notify("Завдання видалено!", severity="success")
                    else:
                        self.notify("Невірний номер", severity="error")
                    self.refresh_table()

            self.push_screen(ConfirmDeleteScreen(idx, task.description), confirm_delete)
        except (ValueError, IndexError):
            self.notify("Помилка при видаленні", severity="error")

    def action_refresh(self) -> None:
        self.refresh_table()
        self.notify("Список оновлено")

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = TodoApp()
    app.run()