import curses
import time

def draw_robot(stdscr, y, x, is_open):
    robot = [
        " ------- ",
        "  -----  ",
        f" | {'o o' if is_open else '- -'} | ",
        "(|  ^  |)",
        " | \\_/ | ",
        "  -----  ",
        " ------- ",
    ]

    for i, line in enumerate(robot):
        stdscr.addstr(y + i, x, line)

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking getch()

    height, width = stdscr.getmaxyx()
    robot_x = width // 2 - len("  -----  ") // 2
    robot_y = height // 2 - len(["  -----  ", " | o o | ", "(|  ^  |)", " | \\_/ | ", "  -----  "]) // 2

    is_mouth_open = False
    frame_counter = 0

    while True:
        stdscr.clear()
        draw_robot(stdscr, robot_y, robot_x, is_mouth_open)
        stdscr.refresh()
        time.sleep(0.2)

        frame_counter += 1
        if frame_counter % 3 == 0:
            is_mouth_open = not is_mouth_open

        char = stdscr.getch()
        if char == ord('q'):
            break

curses.wrapper(main)
