import sys
import termios


def get_long_user_response(prompt="") -> str:
    """
    Using input to get the outpur URL of the Microsoft authenticattor does not
    work since there is a maximum buffer of 4096 bytes for the input in the
    terminal. This function based on termios is a workaround to circumvent the
    problem, see:
    https://stackoverflow.com/questions/30315957/string-from-input-is-limited
    """
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        user_response = input(prompt)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return user_response


def handle_response_code(response):
    return None