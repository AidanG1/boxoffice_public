from dotenv import load_dotenv
from typing import Callable
import io
import os
import resend
import sys
import sys
import time
import traceback

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
from_address = os.getenv("FROM_EMAIL_ADDRESS")
to_address = os.getenv("TO_EMAIL_ADDRESS")


def error_send_email(error_message: str, stdout: str, stderr: str, traceback_str: str = "") -> None:
    """
    Sends an email with the error message and optional traceback string.
    """
    if from_address is None or to_address is None:
        raise ValueError("Email addresses are not set in the environment variables.")

    html_body = (
        f"<p>An error occurred: {error_message}</p>"
        f"<p>Traceback:</p><pre>{traceback_str}</pre>"
        f"<p>Output: {stdout}</p><p>Error Output: {stderr}</p>"
    )

    r = resend.Emails.send(
        {
            "from": from_address,
            "to": to_address,
            "subject": "Error Occurred",
            "html": html_body,
        }
    )


class LiveTee(io.TextIOBase):
    def __init__(self, *targets):
        self.targets = targets  # This can be sys.stdout + memory buffer

    def write(self, data):
        for t in self.targets:
            t.write(data)
            t.flush()  # Ensure live printing

    def flush(self):
        for t in self.targets:
            t.flush()


def wrap_command(
    command: Callable,
    *args,
    **kwargs,
) -> None:
    """
    Wraps a command and sends an email if an error occurs.
    """
    start_time = time.time()
    print(
        f"Starting command: {command.__name__} with args: {args} and kwargs: {kwargs}"
    )

    # Memory buffers
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    # Save originals
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Replace with tee objects
    sys.stdout = LiveTee(original_stdout, stdout_buffer)
    sys.stderr = LiveTee(original_stderr, stderr_buffer)

    # Simulate output
    try:
        command(*args, **kwargs)
    except Exception as e:
        error_message = str(e)
        tb_str = traceback.format_exc()
        print(f"Error: {error_message}")
        error_send_email(
            error_message,
            stdout_buffer.getvalue(),
            stderr_buffer.getvalue(),
            traceback_str=tb_str,
        )
        raise  # Re-raise the exception after sending the email
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    end_time = time.time()
    duration = end_time - start_time
    print(f"Command '{command.__name__}' completed in {duration:.2f} seconds.")
