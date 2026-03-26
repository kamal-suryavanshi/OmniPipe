# Task 10: Error Handling & Logging

A silent pipeline is a completely dead pipeline. When users encounter an error natively mid-production, Pipeline TDs rigorously need physical logs, rather than a screenshot of a user's terminal block they've already closed.

## 1. Production Logger (`omnipipe/core/logger.py`)
Person A built a robust, centralized architectural `logging` system leveraging pure Python's native `logging.handlers.RotatingFileHandler`. 
- **Console Stream:** Mirrors all events linearly to the standard terminal in an easily readable custom format block.
- **Physical File Rotation:** Seamlessly generates physically persistent backend logs natively at `~/omnipipe/logs/pipeline.log`. It natively caps log capacity to 5 Megabytes per log chunk, strictly retaining exactly 3 rotating backups to ensure the pipeline physically never overrides or balloons the artist's hard drive space.

## 2. Global Exception Catching (`omnipipe/__main__.py`)
At the very bottom of the Typer execution tree (`if __name__ == "__main__":`), we violently wrapped the core native `app()` loop internally inside a global `try/except Exception as e` lock. 

If an execution string inherently causes a fatal python module memory structure blowout, the `logger.exception()` mechanically catches the native 100% full stack trace automatically and physically burns it statically into the `pipeline.log` file *immediately* before executing a mathematically safe `sys.exit(1)`. This decisively guarantees no unhandled Tracebacks are missed for bug reporting.
