import logging
import colorlog

def setup_colored_logging(level=logging.INFO):
    """Configure colored logging for console output"""
    
    # Define color scheme
    color_scheme = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
    
    # Create a color formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors=color_scheme
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