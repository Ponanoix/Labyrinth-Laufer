# Labyrinth-Laufer
A multi-threaded, simple game about escaping a maze. Made as a project for Operating Systems 2 (SO2) course in WUST.

![alt text](https://i.imgur.com/9xdBAa2.png)

The program has a number of threads and critical sections.

The threads are as follows:
- **Input thread**: This thread monitors keyboard input from the player
- **Gui thread**: This thread renders GUI and updates it each time something moves
- **Enemy threads**: These threads are responsible for moving the enemies across the maze.
    The number of threads is equal to the number of enemies.

There are also two critical sections implemented:
- One mutex, when the player moves
- Other mutex each time an enemy moves