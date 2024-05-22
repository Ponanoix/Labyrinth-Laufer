import threading
import os
import time
import keyboard
import random

# Defines the maze's outline
columns = 20
rows = 20
maze = [[1 for _ in range(columns)] for _ in range(rows)]

# Generates an array of border indices
border_indices = [(0, j) for j in range(columns)] + [(rows - 1, j) for j in range(columns)] + [(i, 0) for i in
                                                                                               range(1, rows - 1)] + [
                     (i, columns - 1) for i in range(1, rows - 1)]
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

# Creates a lock for the shared resource (player position)
lock = threading.Lock()


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
        condition = lambda node: node in visited_nodes or node in border_indices or node in dead_end_path or node in visited_walls
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
        if next_node not in border_indices and next_node not in visited_nodes and next_node not in corner_indices and next_node not in dead_end_path and next_node not in visited_walls:
            length -= 1
            for item in current_neighbours:
                if maze[item[0]][item[1]] == ' ':
                    visited_nodes.append(item)
                else:
                    visited_walls.append(item)
            current_neighbours = get_neighbours(next_node, rows, columns)
            maze[next_node[0]][next_node[1]] = ' '

    # This branch of code activates when the "length" variable reaches zero. From this point forward the algorithm is allowed to seek an end
    while next_node not in border_indices or next_node in corner_indices:

        # This branch of code activates when the random path generation encounters a dead end
        condition = lambda node: node in visited_nodes or node in border_indices or node in dead_end_path or node in visited_walls
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
        elif next_node not in border_indices and next_node not in visited_nodes and next_node not in corner_indices and next_node not in visited_walls:
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


# Function to render the maze with player inside it
def render_maze():
    lock.acquire()
    for i in range(rows):
        for j in range(columns):
            if (i, j) == player_pos:
                print('P', end='  ')
            else:
                print(maze[i][j], end='  ')
        print()
    print("\n")
    lock.release()


# Function to move the player
def move_player(dx, dy):
    global player_pos
    new_pos = (player_pos[0] + dx, player_pos[1] + dy)
    if is_valid_move(new_pos):
        player_pos = new_pos
        render_maze()
        exit_pos = return_exit()
        if player_pos == exit_pos:
            print("Congratulations! You reached the exit.")
            os._exit(0)  # Terminate the program


# Thread for input handling
def handle_input():
    while True:
        if keyboard.is_pressed('w'):
            move_player(-1, 0)
        elif keyboard.is_pressed('s'):
            move_player(1, 0)
        elif keyboard.is_pressed('a'):
            move_player(0, -1)
        elif keyboard.is_pressed('d'):
            move_player(0, 1)
        time.sleep(0.1)


def return_exit():
    for element in border_indices:
        if maze[element[0]][element[1]] == ' ' and element != entrance:
            end = element
            break
    return end


# Function to check if the move is valid
def is_valid_move(pos):
    x, y = pos
    return 0 <= x < rows and 0 <= y < columns and maze[x][y] != 1


def main():
    generate_a_path(30, entrance)
    complicate_layout()

    # Start rendering the maze
    render_thread = threading.Thread(target=render_maze)
    render_thread.start()

    # Start input handling thread
    input_thread = threading.Thread(target=handle_input)
    input_thread.start()

    render_thread.join()
    input_thread.join()


if __name__ == "__main__":
    main()
