from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
import time

layout = Layout()

layout.split_column(
    Layout(name="info"),
    Layout(name="message")
)

def update_panels(layout, counter):
    layout["info_panel"].update(Panel(f"Info Panel Content {counter}", title="Info Panel"))
    layout["message_panel"].update(Panel(f"Message Panel Content {counter}", title="Message Panel"))

with Live(layout, screen=True, redirect_stderr=False) as live:
    counter = 0
    while True:
        update_panels(layout, counter)
        time.sleep(1)
        counter += 1