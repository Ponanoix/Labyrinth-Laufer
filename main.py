import tkinter as tk
import threading
import os
import time
import keyboard
import random

# Defines the maze's outline
columns = 35
rows = 35
maze = [[1 for _ in range(columns)] for _ in range(rows)]

# Generates an array of border indices
border_indices = ([(0, j) for j in range(columns)] + [(rows - 1, j) for j in range(columns)]
                  + [(i, 0) for i in range(1, rows - 1)] + [(i, columns - 1) for i in range(1, rows - 1)])

# Removes corner indices from the border indices
corner_indices = []
border_indices.remove((0, 0))
corner_indices.append((0, 0))
border_indices.remove((0, columns - 1))
corner_indices.append((0, columns - 1))
border_indices.remove((rows - 1, 0))
corner_indices.append((rows - 1, 0))
border_indices.remove((rows - 1, columns - 1))
corner_indices.append((rows - 1, columns - 1))

# Chooses one of the border indices as the entrance
entrance = random.choice(border_indices)
maze[entrance[0]][entrance[1]] = ' '

# Sets the entrance's coordinates as the starting position
player_pos = entrance

# Creates a lock for the shared resource (entity position)
mutex = threading.Lock()
render_lock = threading.Lock()

# List of enemies' positions
enemy_positions = []

# Number of enemies
num_enemies = 10

# Timer variables
start_time = None
end_time = None

# Tkinter GUI variables
CELL_SIZE = 20
WINDOW_WIDTH = columns * CELL_SIZE
WINDOW_HEIGHT = rows * CELL_SIZE
MESSAGE_WIDTH = WINDOW_WIDTH
MESSAGE_HEIGHT = WINDOW_HEIGHT
WALL_COLOR = "gray"
PATH_COLOR = "white"
PLAYER_COLOR = "blue"
ENEMY_COLOR = "red"


# Function to generate the Tkinter GUI
def generate_gui():
    global root, canvas, timer_label
    root = tk.Tk()
    root.title("Labyrinth Laufer")
    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    timer_label = tk.Label(root, text="Time: 0.0", font=("Arial", 14))
    timer_label.pack()

    def on_closing():
        stop_event.set()
        root.quit()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    update_gui()
    root.mainloop()


def update_gui():
    with render_lock:
        canvas.delete("all")
        for i in range(rows):
            for j in range(columns):
                x0, y0 = j * CELL_SIZE, i * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                if (i, j) in enemy_positions:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=ENEMY_COLOR)
                elif (i, j) == player_pos:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=PLAYER_COLOR)
                elif maze[i][j] == 1:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=WALL_COLOR)
                else:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=PATH_COLOR)

        if start_time:
            elapsed_time = time.time() - start_time
            timer_label.config(text=f"Time: {elapsed_time:.1f}")

        canvas.update()
    if not stop_event.is_set():
        root.after(100, update_gui)


def message_window(text, color, elapsed_time):
    message_root = tk.Toplevel(root)
    message_canvas = tk.Canvas(message_root, width=MESSAGE_WIDTH, height=MESSAGE_HEIGHT)
    message_canvas.pack()
    message_canvas.create_text(MESSAGE_WIDTH // 2, MESSAGE_HEIGHT // 2,
                               text=f"{text}\nElapsed Time: {elapsed_time:.1f} seconds", fill=color, font=("Arial", 14), anchor='center')

    def close_message():
        message_root.destroy()
        root.quit()

    message_root.after(3000, close_message)


# Two messages that should appear at the end of the game
def win_message():
    stop_timer()
    elapsed_time = calculate_elapsed_time()
    message_window("Congratulations! You reached the exit.", "green", elapsed_time)
    stop_event.set()


def loss_message():
    stop_timer()
    elapsed_time = calculate_elapsed_time()
    message_window("Game Over! An enemy caught you.", "red", elapsed_time)
    stop_event.set()


# A function that returns neighbours of the current index
def get_neighbours(node, row, column):
    x, y = node
    neighbours = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            # Skips the index itself
            if dx == 0 and dy == 0:
                continue
            # Skips indices in the corners
            if dx != 0 and dy != 0:
                continue
            # Calculates the neighbour's coordinates
            nx, ny = x + dx, y + dy
            # Checks if the neighbour is within bounds
            if 0 <= nx < row and 0 <= ny < column:
                neighbours.append((nx, ny))
    return neighbours


# A function that generates a random solution to the maze
def generate_a_path(length, start):
    next_node = start
    visited_nodes = [start]
    current_neighbours = get_neighbours(start, rows, columns)
    visited_walls = []
    dead_end_path = []
    while length != 0:
        # This branch of code activates when the random path generation encounters a dead end
        condition = lambda node: (node in visited_nodes or node in border_indices
                                  or node in dead_end_path or node in visited_walls)
        while all(condition(nodes) for nodes in current_neighbours):
            # Removes current node's walls (that meet the criteria) from visited walls array
            for item in current_neighbours:
                if maze[item[0]][item[1]] != ' ':
                    counted_paths = 0
                    walls_neighbours = get_neighbours(item, rows, columns)
                    for item2 in walls_neighbours:
                        if maze[item2[0]][item2[1]] == ' ' and item2 != next_node:
                            counted_paths += 1
                    if counted_paths == 0:
                        if item in visited_walls:
                            visited_walls.remove(item)

            # Saves the current node to the dead end array
            if len(dead_end_path) != 0:
                visited_walls.append(dead_end_path[0])
                del dead_end_path[0]
            dead_end_path.append(next_node)

            # Upgrades the current node and its neighbours to the previous node
            maze[next_node[0]][next_node[1]] = 1
            for item2 in current_neighbours:
                if maze[item2[0]][item2[1]] == ' ' and item2 not in dead_end_path:
                    next_node = item2
            current_neighbours = get_neighbours(next_node, rows, columns)

            # Removes the new node's walls from visited walls array (same as rules as above)
            for item in current_neighbours:
                if maze[item[0]][item[1]] != ' ':
                    counted_paths = 0
                    walls_neighbours = get_neighbours(item, rows, columns)
                    for item2 in walls_neighbours:
                        if maze[item2[0]][item2[1]] == ' ' and item2 != next_node:
                            counted_paths += 1
                    if counted_paths == 0:
                        if item in visited_walls:
                            visited_walls.remove(item)
        # Randomised choosing of the next node
        next_node = random.choice(current_neighbours)
        if (next_node not in border_indices and next_node not in visited_nodes and next_node
                not in corner_indices and next_node not in dead_end_path and next_node not in visited_walls):
            length -= 1
            for item in current_neighbours:
                if maze[item[0]][item[1]] == ' ':
                    visited_nodes.append(item)
                else:
                    visited_walls.append(item)
            current_neighbours = get_neighbours(next_node, rows, columns)
            maze[next_node[0]][next_node[1]] = ' '

    # This branch of code activates when the "length" variable reaches zero.
    # From this point forward the algorithm is allowed to seek an end
    while next_node not in border_indices or next_node in corner_indices:

        # This branch of code activates when the random path generation encounters a dead end
        condition = lambda node: (node in visited_nodes
                                  or node in border_indices or node in dead_end_path or node in visited_walls)
        while all(condition(nodes) for nodes in current_neighbours):
            # Removes current node's walls (that meet the criteria) from visited walls array
            for item in current_neighbours:
                if maze[item[0]][item[1]] != ' ':
                    counted_paths = 0
                    walls_neighbours = get_neighbours(item, rows, columns)
                    for item2 in walls_neighbours:
                        if maze[item2[0]][item2[1]] == ' ' and item2 != next_node:
                            counted_paths += 1
                    if counted_paths == 0:
                        if item in visited_walls:
                            visited_walls.remove(item)

            # Saves the current node to the dead end array
            if len(dead_end_path) != 0:
                visited_walls.append(dead_end_path[0])
                del dead_end_path[0]
            dead_end_path.append(next_node)

            # Upgrades the current node and its neighbours to the previous node
            maze[next_node[0]][next_node[1]] = 1
            for item2 in current_neighbours:
                if maze[item2[0]][item2[1]] == ' ' and item2 not in dead_end_path:
                    next_node = item2
            current_neighbours = get_neighbours(next_node, rows, columns)

            # Removes the new node's walls from visited walls array (same as rules as above)
            for item in current_neighbours:
                if maze[item[0]][item[1]] != ' ':
                    counted_paths = 0
                    walls_neighbours = get_neighbours(item, rows, columns)
                    for item2 in walls_neighbours:
                        if maze[item2[0]][item2[1]] == ' ' and item2 != next_node:
                            counted_paths += 1
                    if counted_paths == 0:
                        if item in visited_walls:
                            visited_walls.remove(item)

        # Randomised choosing of the next node
        next_node = random.choice(current_neighbours)
        if next_node in border_indices and next_node not in visited_nodes and next_node not in visited_walls:
            maze[next_node[0]][next_node[1]] = ' '
            break
        elif (next_node not in border_indices and next_node not in visited_nodes
              and next_node not in corner_indices and next_node not in visited_walls):
            for neighbour in current_neighbours:
                visited_nodes.append(neighbour)
            current_neighbours = get_neighbours(next_node, rows, columns)
            maze[next_node[0]][next_node[1]] = ' '


# This function creates the actual maze, making the existing solution more difficult to comprehend
def complicate_layout():
    # Adding path data to an array
    path = []
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == ' ':
                path.append((i, j))
    # Adding additional dead ends
    for j in path:
        nodes_neighbours = get_neighbours(j, rows, columns)
        for element in nodes_neighbours:
            if maze[element[0]][element[1]] != ' ' and element not in border_indices and element not in corner_indices:
                counted_paths = 0
                neighbours_neighbours = get_neighbours(element, rows, columns)
                for item in neighbours_neighbours:
                    if maze[item[0]][item[1]] == ' ' and item in path and item != j:
                        counted_paths += 1
                if counted_paths == 0:
                    maze[element[0]][element[1]] = ' '
                    path.append(element)


# Initialize enemies at random positions in the maze
def initialize_enemies():
    global enemy_positions
    while len(enemy_positions) < num_enemies:
        x, y = random.randint(0, rows - 1), random.randint(0, columns - 1)
        if maze[x][y] == ' ' and (x, y) != player_pos:
            enemy_positions.append((x, y))


# Thread for input handling
def handle_input():
    keys_state = {'w': False, 'a': False, 's': False, 'd': False}
    # 50 milliseconds debounce time
    debounce_time = 0.05
    while True:
        for key, state in keys_state.items():
            if keyboard.is_pressed(key) and not state:
                if key == 'w':
                    move_player(-1, 0)
                elif key == 'a':
                    move_player(0, -1)
                elif key == 's':
                    move_player(1, 0)
                elif key == 'd':
                    move_player(0, 1)
                keys_state[key] = True
                time.sleep(debounce_time)
            elif not keyboard.is_pressed(key):
                keys_state[key] = False
        # Checks for input every 10 milliseconds (100 Hz)
        time.sleep(0.01)


def return_exit():
    global end
    for element in border_indices:
        if maze[element[0]][element[1]] == ' ' and element != entrance:
            end = element
            break
    return end


# Function to move the player
def move_player(dx, dy):
    global player_pos
    new_pos = (player_pos[0] + dx, player_pos[1] + dy)
    exit_pos = return_exit()
    if is_valid_move(new_pos):
        with mutex:
            player_pos = new_pos
            if player_pos == exit_pos:
                win_message()
                time.sleep(3)
                os._exit(0)
            if player_pos in enemy_positions:
                loss_message()
                time.sleep(3)
                os._exit(0)


# Function to move enemies
def move_enemy(enemy_index):
    global enemy_positions
    while True:
        with mutex:
            if enemy_index < len(enemy_positions):
                x, y = enemy_positions[enemy_index]
                possible_moves = [(x + dx, y + dy) for dx, dy
                                  in [(-1, 0), (1, 0), (0, -1), (0, 1)] if is_valid_move((x + dx, y + dy))]
                for move in possible_moves:
                    if move in enemy_positions:
                        possible_moves.remove(move)
                if possible_moves:
                    new_pos = random.choice(possible_moves)
                    enemy_positions[enemy_index] = new_pos
                    for position in enemy_positions:
                        if position == player_pos:
                            loss_message()
                            time.sleep(3)
                            os._exit(0)
        time.sleep(2)


# Function to check if the move is valid
def is_valid_move(pos):
    x, y = pos
    return 0 <= x < rows and 0 <= y < columns and maze[x][y] != 1


# Function to start the timer
def start_timer():
    global start_time
    start_time = time.time()


# Function to stop the timer
def stop_timer():
    global end_time
    end_time = time.time()


# Function to calculate the elapsed time
def calculate_elapsed_time():
    elapsed_time = end_time - start_time if start_time and end_time else 0
    return elapsed_time


# Main function
def main():
    global stop_event
    stop_event = threading.Event()

    # Create the maze itself
    generate_a_path(40, entrance)
    complicate_layout()

    # Start the timer when the game starts
    start_timer()

    # Initialize enemies
    initialize_enemies()

    # Start GUI thread
    gui_thread = threading.Thread(target=generate_gui)
    gui_thread.start()

    # Start input handling thread
    input_thread = threading.Thread(target=handle_input)
    input_thread.start()

    # Start enemy threads
    enemy_threads = []
    for i in range(num_enemies):
        thread = threading.Thread(target=move_enemy, args=(i,))
        thread.start()
        enemy_threads.append(thread)
        time.sleep(0.5)

    # Wait for input thread to finish
    input_thread.join()

    # Wait for rendering and enemy threads to finish
    for thread in enemy_threads:
        thread.join()
    gui_thread.join()


if __name__ == "__main__":
    main()
