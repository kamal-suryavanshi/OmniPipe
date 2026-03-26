import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="omnipipe", level=logging.INFO):
    """
    Configures a production-grade logger that simultaneously writes to both the console 
    and a mathematically rolling log file in the user's root OS directory.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | [%(module)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Terminal Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    # Physical Persistent File Handler
    log_dir = os.path.join(os.path.expanduser("~"), "omnipipe", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "pipeline.log")
    
    # 5 MB maximum cache per file, rigorously keep 3 backups to prevent drive ballooning
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Expose a default global singleton instance
logger = setup_logger()
