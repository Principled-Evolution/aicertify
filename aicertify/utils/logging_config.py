import logging
import time
import threading
from typing import Optional

import colorlog
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Global console for rich output
console = Console()

# Emoji mapping for different log levels and categories
EMOJIS = {
    # Log levels
    "DEBUG": "🔍",
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🚨",
    # Categories
    "POLICY": "📜",
    "EVALUATION": "🧪",
    "REPORT": "📊",
    "APPLICATION": "🤖",
    "REGULATION": "⚖️",
    "SYSTEM": "🔧",
    "SECURITY": "🔒",
    "COMPLIANCE": "✓",
    "NON_COMPLIANCE": "✗",
    "LOADING": "⏳",
    "COMPLETE": "🏁",
    "METRICS": "📏",
    "INTERACTION": "💬",
    "MODEL": "🧠",
    "FILE": "📄",
    "CONFIG": "⚙️",
}


# Spinner for long-running tasks
class Spinner:
    """A simple spinner for indicating progress of long-running tasks"""

    def __init__(self, message: str, emoji: str = "⏳"):
        self.message = message
        self.emoji = emoji
        self.running = False
        self.spinner_thread = None
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold green]{task.description}"),
            console=console,
        )
        self.task_id = None

    def start(self):
        """Start the spinner"""
        self.running = True
        with self.progress:
            self.task_id = self.progress.add_task(f"{self.emoji} {self.message}")
            while self.running:
                self.progress.update(self.task_id)
                time.sleep(0.1)

    def __enter__(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.start)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=0.5)


def setup_colored_logging(level=logging.INFO):
    """Configure colored logging for console output"""

    # Define color scheme
    color_scheme = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    }

    # Create a color formatter with emojis
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(message)s",
        log_colors=color_scheme,
    )

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)

    # Add console handler to root logger
    root_logger.addHandler(console)

    return root_logger


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a logger with the AICertify styling"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    return logger


def log(
    level: str,
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log a message with the appropriate emoji and formatting"""
    level = level.upper()

    # Get the appropriate emoji
    level_emoji = EMOJIS.get(level, "")
    category_emoji = EMOJIS.get(category, "") if category else ""

    # Format the message
    if category:
        formatted_message = f"{level_emoji} {category_emoji} {message}"
    else:
        formatted_message = f"{level_emoji} {message}"

    # Log the message
    if logger:
        if level == "DEBUG":
            logger.debug(formatted_message)
        elif level == "INFO":
            logger.info(formatted_message)
        elif level == "WARNING":
            logger.warning(formatted_message)
        elif level == "ERROR":
            logger.error(formatted_message)
        elif level == "CRITICAL":
            logger.critical(formatted_message)
        elif level == "SUCCESS":
            # Success is a custom level, map to info
            logger.info(f"✅ {message}")
    else:
        # Use rich console directly
        if level == "DEBUG":
            console.print(f"[cyan]{formatted_message}[/cyan]")
        elif level == "INFO":
            console.print(f"[green]{formatted_message}[/green]")
        elif level == "WARNING":
            console.print(f"[yellow]{formatted_message}[/yellow]")
        elif level == "ERROR":
            console.print(f"[red]{formatted_message}[/red]")
        elif level == "CRITICAL":
            console.print(f"[red on white]{formatted_message}[/red on white]")
        elif level == "SUCCESS":
            console.print(f"[bold green]✅ {message}[/bold green]")


def info(
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log an info message"""
    log("INFO", message, category, logger)


def debug(
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log a debug message"""
    log("DEBUG", message, category, logger)


def warning(
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log a warning message"""
    log("WARNING", message, category, logger)


def error(
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log an error message"""
    log("ERROR", message, category, logger)


def critical(
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log a critical message"""
    log("CRITICAL", message, category, logger)


def success(
    message: str,
    category: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
):
    """Log a success message"""
    log("SUCCESS", message, category, logger)


def spinner(message: str, emoji: str = "⏳") -> Spinner:
    """Create a spinner for long-running tasks"""
    return Spinner(message, emoji)


def print_banner():
    """Print the AICertify banner"""
    banner = """
    [bold blue]    _    _[/bold blue][bold green] ___[/bold green][bold yellow]            _   _  __[/bold yellow][bold red]
[/bold red]    [bold blue]/ \  (_)[/bold blue][bold green]/ __\[/bold green][bold yellow]  ___ _ __| |_(_)/ _|[/bold yellow][bold red]_   _
[/bold red]    [bold blue]/ _ \ | [/bold blue][bold green]/ /[/bold green][bold yellow] / _ \ '__| __| | |_[/bold yellow][bold red]| | | |
[/bold red]    [bold blue]/ ___ \| [/bold blue][bold green]/ /[/bold green][bold yellow]|  __/ |  | |_| |  _[/bold yellow][bold red]| |_| |
[/bold red]    [bold blue]/_/   \_\_[/bold blue][bold green]\/[/bold green][bold yellow] \___|_|   \__|_|_|[/bold yellow][bold red] \__, |
[/bold red]    [bold blue]           [/bold blue][bold green]  [/bold green][bold yellow]                [/bold yellow][bold red]|___/
[/bold red]    """
    console.print(banner)
    console.print("[bold]AI Certification Framework[/bold]")
    console.print(
        "[italic]Validate and certify AI applications against regulatory requirements[/italic]\n"
    )
