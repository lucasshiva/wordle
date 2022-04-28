# Wordle
Play Wordle directly from your terminal.

This project was based on [Termo](https://term.ooo), a Brazilian Portuguese version of the original [Wordle](https://www.nytimes.com/games/wordle/index.html). 

**Features**
- No limits! Play as much as you want.
- The same words from the original Wordle.
- Different modes for more fun!

## Screenshots

### Modes
- **Solo Mode** by setting the `--mode` option to "solo".

    ![solo-mode](imgs/solo-mode.png)

- **Duo Mode** by setting the `--mode` option to "duo".

    ![duo-mode](imgs/duo-mode.png)

- **Quad Mode** by setting the `--mode` option to "quad".

    ![quad-mode](imgs/quad-mode.png)

    Solved puzzles do not accept more inputs and are extremely easy to identify. For example:

    ![A solved puzzle in quad mode](imgs/quad-mode-solved.png)

### Debug
`Wordle` comes with a debug mode, which shows the secret word on the top of each puzzle. To enable debug mode, pass the `-d` flag to `wordle`, e.g., `wordle -d`.

![Quad Mod with debug turned on](imgs/quad-mode-with-debug.png)


## Install
1. Download and install [Poetry]() in your machine.
2. Clone this repository: `git clone https://github.com/lucasshiva/wordle`
3. Move into the cloned folder: `cd wordle`
4. Install this project with Poetry: `poetry install`
5. Run `wordle` on your terminal. Optionally, run `wordle --help` first for a full list of options.

