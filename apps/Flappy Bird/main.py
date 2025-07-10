import customtkinter as ctk
from tkinter import colorchooser
import random
import os

APP_WIDTH = 400
APP_HEIGHT = 600

def launch_app(parent):
    WIDTH, HEIGHT = APP_WIDTH, APP_HEIGHT
    PIPE_WIDTH = 80
    PIPE_GAP = 180
    PIPE_SPEED = 5
    BIRD_SIZE = 40
    GRAVITY = 2
    JUMP_STRENGTH = -18
    FRAMERATE = 20

    canvas = ctk.CTkCanvas(parent, width=WIDTH, height=HEIGHT, bg="#4EC0CA", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Game state
    bird_y = HEIGHT // 2
    bird_vel = 0
    pipe_x = WIDTH
    pipe_hole = random.randint(60, HEIGHT - PIPE_GAP - 60)
    score = [0]
    best_score = [0]
    running = [True]
    bird = [None]
    pipes = [None, None]
    score_text = [None]
    game_over_items = []

    # Load best score from file
    data_path = os.path.join(os.path.dirname(__file__), "data.dat")
    if os.path.isfile(data_path):
        with open(data_path) as f:
            try:
                best_score[0] = int(f.read())
            except:
                best_score[0] = 0
    else:
        with open(data_path, "w") as f:
            f.write("0")

    def draw_bird():
        if bird[0]:
            canvas.delete(bird[0])
        bird[0] = canvas.create_rectangle(100, bird_y, 100+BIRD_SIZE, bird_y+BIRD_SIZE, fill="blue", outline="black")

    def draw_pipes():
        if pipes[0]:
            canvas.delete(pipes[0])
        if pipes[1]:
            canvas.delete(pipes[1])
        pipes[0] = canvas.create_rectangle(pipe_x, 0, pipe_x+PIPE_WIDTH, pipe_hole, fill="#74BF2E", outline="#74BF2E")
        pipes[1] = canvas.create_rectangle(pipe_x, pipe_hole+PIPE_GAP, pipe_x+PIPE_WIDTH, HEIGHT, fill="#74BF2E", outline="#74BF2E")

    def draw_score():
        if score_text[0]:
            canvas.delete(score_text[0])
        score_text[0] = canvas.create_text(15, 45, text=str(score[0]), font=('Impact', 40), fill='#ffffff', anchor="w")

    def reset_game():
        nonlocal bird_y, bird_vel, pipe_x, pipe_hole
        for item in game_over_items:
            canvas.delete(item)
        game_over_items.clear()
        bird_y = HEIGHT // 2
        bird_vel = 0
        pipe_x = WIDTH
        pipe_hole = random.randint(60, HEIGHT - PIPE_GAP - 60)
        score[0] = 0
        running[0] = True
        draw_bird()
        draw_pipes()
        draw_score()
        update()

    def update():
        if not running[0]:
            return
        nonlocal bird_y, bird_vel, pipe_x, pipe_hole
        # Bird physics
        bird_vel += GRAVITY
        bird_y += bird_vel
        if bird_y < 0:
            bird_y = 0
            bird_vel = 0
        if bird_y + BIRD_SIZE > HEIGHT:
            bird_y = HEIGHT - BIRD_SIZE
            bird_vel = 0
            game_over()
            return
        draw_bird()

        # Move pipes
        pipe_x -= PIPE_SPEED
        if pipe_x + PIPE_WIDTH < 0:
            pipe_x = WIDTH
            pipe_hole = random.randint(60, HEIGHT - PIPE_GAP - 60)
            score[0] += 1
            draw_score()
        draw_pipes()

        # Collision detection
        if (pipe_x < 100 + BIRD_SIZE and pipe_x + PIPE_WIDTH > 100):
            if bird_y < pipe_hole or bird_y + BIRD_SIZE > pipe_hole + PIPE_GAP:
                game_over()
                return

        parent.after(FRAMERATE, update)

    def jump(event=None):
        if not running[0]:
            reset_game()
            return
        nonlocal bird_vel
        bird_vel = JUMP_STRENGTH

    def game_over():
        running[0] = False
        if score[0] > best_score[0]:
            best_score[0] = score[0]
            with open(data_path, "w") as f:
                f.write(str(best_score[0]))
        game_over_items.append(canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill='#4EC0CA', stipple='gray25'))
        game_over_items.append(canvas.create_text(WIDTH//2, HEIGHT//2-40, text=f"Game Over", font=('Impact', 36), fill='#ffffff'))
        game_over_items.append(canvas.create_text(WIDTH//2, HEIGHT//2+10, text=f"Your score: {score[0]}", font=('Impact', 24), fill='#ffffff'))
        game_over_items.append(canvas.create_text(WIDTH//2, HEIGHT//2+50, text=f"Best score: {best_score[0]}", font=('Impact', 20), fill='#ffffff'))
        game_over_items.append(canvas.create_text(WIDTH//2, HEIGHT//2+100, text="Press Space to Restart", font=('Arial', 16), fill='#ffffff'))

    canvas.focus_set()
    canvas.bind("<space>", jump)
    reset_game()