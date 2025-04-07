import logging
import time
import threading
from typing import Optional, Dict, List, Any
from collections import defaultdict

import colorlog
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

# Global console for rich output
console = Console()

# AICertify branding
AIC_LOGO = "🔰"  # Shield with leaf - representing certification and growth
AIC_COLOR = "blue"  # Primary brand color

# Emoji mapping for different log levels and categories
EMOJIS = {
    # Log levels
    "DEBUG": "·",
    "INFO": AIC_LOGO,
    "SUCCESS": "✓",
    "WARNING": "!",
    "ERROR": "✗",
    "CRITICAL": "!!",

    # Categories - using minimal set for cleaner output
    "POLICY": "📜",
    "EVALUATION": "🧪",
    "REPORT": "📊",
    "APPLICATION": "🤖",
    "REGULATION": "⚖️",
    "LOADING": "⏳",
    "COMPLETE": "✓",
    "INTERACTION": "💬",
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

    # Format the message with AICertify branding for important messages
    if level in ["INFO", "SUCCESS"]:
        if category:
            formatted_message = f"{AIC_LOGO} {category_emoji} {message}"
        else:
            formatted_message = f"{AIC_LOGO} {message}"
    else:
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
            logger.info(f"{EMOJIS['SUCCESS']} {message}")
    else:
        # Use rich console directly
        if level == "DEBUG":
            console.print(f"[dim]{formatted_message}[/dim]")
        elif level == "INFO":
            console.print(f"[{AIC_COLOR}]{formatted_message}[/{AIC_COLOR}]")
        elif level == "WARNING":
            console.print(f"[yellow]{formatted_message}[/yellow]")
        elif level == "ERROR":
            console.print(f"[red]{formatted_message}[/red]")
        elif level == "CRITICAL":
            console.print(f"[red on white]{formatted_message}[/red on white]")
        elif level == "SUCCESS":
            console.print(f"[bold {AIC_COLOR}]{EMOJIS['SUCCESS']} {message}[/bold {AIC_COLOR}]")


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


# Message grouping utilities
class MessageGroup:
    """A utility for grouping similar messages and showing a summary"""

    def __init__(self, title: str, color: str = AIC_COLOR):
        self.title = title
        self.color = color
        self.messages = defaultdict(int)
        self.total_count = 0
        self.live = None
        self.is_active = False

    def add(self, message: str) -> None:
        """Add a message to the group"""
        self.messages[message] += 1
        self.total_count += 1
        if self.is_active:
            self._update_display()

    def _create_panel(self) -> Panel:
        """Create a panel with the current messages"""
        content = Text()
        content.append(f"{AIC_LOGO} {self.title}: {self.total_count} items\n", style=f"bold {self.color}")

        # Show top 3 most frequent messages
        top_messages = sorted(self.messages.items(), key=lambda x: x[1], reverse=True)[:3]
        for msg, count in top_messages:
            content.append(f"  • {msg}: {count}\n", style=self.color)

        if len(self.messages) > 3:
            content.append(f"  • ... and {len(self.messages) - 3} more", style=f"dim {self.color}")

        return Panel(content, border_style=self.color)

    def _update_display(self) -> None:
        """Update the live display"""
        if self.live:
            self.live.update(self._create_panel())

    def __enter__(self):
        """Start displaying the message group"""
        self.live = Live(self._create_panel(), refresh_per_second=4)
        self.live.start()
        self.is_active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop displaying the message group"""
        if self.live:
            self.live.stop()
        self.is_active = False

        # Print a summary
        console.print(f"[{self.color}]{AIC_LOGO} {self.title} complete: {self.total_count} items processed[/{self.color}]")


def print_banner():
    """Print the AICertify banner"""
    banner = f"""
    [bold {AIC_COLOR}]    _    _  ___            _   _  __
    / \\  (_)/ __\\  ___ _ __| |_(_)/ _|_   _
    / _ \\ | / /  / _ \\ '__| __| | |_| | | |
    / ___ \\| / / |  __/ |  | |_| |  _| |_| |
    /_/   \\_\\_\\/  \\___|_|   \\__|_|_| \\__, |
                                   |___/  [/bold {AIC_COLOR}]
    """
    console.print(banner)
    console.print(f"[bold {AIC_COLOR}]{AIC_LOGO} AI Certification Framework[/bold {AIC_COLOR}]")
    console.print(f"[{AIC_COLOR}]Validate and certify AI applications against regulatory requirements[/{AIC_COLOR}]\n")
