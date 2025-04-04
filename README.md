# Labyrinth-Laufer
A multi-threaded, simple game about escaping a maze. Made as a project for Operating Systems 2 (SO2) course in WUST.

![alt text](https://i.imgur.com/uxZi5Di.png)

The program has a number of threads and critical sections.

The threads are as follows:
- **Input thread**: This thread monitors keyboard input from the player
- **Gui thread**: This thread renders GUI and constantly updates it, including timer and entity movement
- **Enemy threads**: These threads are responsible for moving the enemies across the maze.
    The number of threads is equal to the number of enemies.

There are also two critical sections implemented, two mutex variables:
- One mutex, when the player moves or an enemy moves
- Another mutex makes sure the GUI gets rendered properly
