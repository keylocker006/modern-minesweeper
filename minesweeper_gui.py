import tkinter as tk
from tkinter import messagebox
import random
import time

class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("💣 Minesweeper")
        self.master.configure(bg="#2b2b2b")
        
        # Difficulty settings
        self.difficulties = {
            "Easy": (8, 8, 10),
            "Medium": (16, 16, 40),
            "Hard": (22, 22, 99)
        }
        self.difficulty = "Easy"
        self.rows, self.cols, self.mines_total = self.difficulties[self.difficulty]
        
        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        # Top bar
        top_frame = tk.Frame(self.master, bg="#2b2b2b", pady=10)
        top_frame.pack(fill="x")

        # Mine counter
        self.mines_left = tk.Label(top_frame, text=f"💣 {self.mines_total:03d}", 
                                 font=("Courier", 20, "bold"), fg="#ff4444", bg="#1a1a1a", width=8)
        self.mines_left.pack(side="left", padx=20)

        # Restart button (smiley)
        self.restart_btn = tk.Button(top_frame, text="😀", font=("Arial", 24), 
                                   width=3, height=1, command=self.new_game)
        self.restart_btn.pack(side="left", expand=True)

        # Timer
        self.timer_label = tk.Label(top_frame, text="000", font=("Courier", 20, "bold"),
                                  fg="#ffaa00", bg="#1a1a1a", width=8)
        self.timer_label.pack(side="right", padx=20)

        # Difficulty selector
        diff_frame = tk.Frame(self.master, bg="#2b2b2b")
        diff_frame.pack(fill="x", pady=5)
        for diff in self.difficulties:
            btn = tk.Button(diff_frame, text=diff, command=lambda d=diff: self.change_difficulty(d))
            btn.pack(side="left", expand=True, fill="x", padx=5)

        # Game board
        self.board_frame = tk.Frame(self.master, bg="#2b2b2b")
        self.board_frame.pack(pady=10)

    def new_game(self):
        self.rows, self.cols, self.mines_total = self.difficulties[self.difficulty]
        self.mines_left.config(text=f"💣 {self.mines_total:03d}")
        
        self.cells = {}  # (r,c) -> button
        self.numbers = [[0]*self.cols for _ in range(self.rows)]  # -1 = mine
        self.revealed = [[False]*self.cols for _ in range(self.rows)]
        self.flagged = [[False]*self.cols for _ in range(self.rows)]
        
        self.first_click = True
        self.game_over = False
        self.start_time = None
        self.timer_running = False
        
        self.restart_btn.config(text="😀")
        
        # Clear old board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        # Create buttons
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, text=" ", width=2, height=1,
                              font=("Arial", 12, "bold"), bg="#a0a0a0",
                              relief="raised", bd=3)
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.left_click(rr, cc))
                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.right_click(rr, cc))
                self.cells[(r, c)] = btn

    def change_difficulty(self, diff):
        self.difficulty = diff
        self.new_game()

    def place_mines(self, first_r, first_c):
        mines_placed = 0
        while mines_placed < self.mines_total:
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)
            if (r, c) != (first_r, first_c) and self.numbers[r][c] != -1:
                self.numbers[r][c] = -1
                mines_placed += 1
        
        # Calculate numbers
        for r in range(self.rows):
            for c in range(self.cols):
                if self.numbers[r][c] == -1:
                    continue
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.numbers[nr][nc] == -1:
                            self.numbers[r][c] += 1

    def left_click(self, r, c):
        if self.game_over or self.revealed[r][c] or self.flagged[r][c]:
            return

        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

        if self.first_click:
            self.first_click = False
            self.place_mines(r, c)

        self.reveal(r, c)

    def reveal(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols) or self.revealed[r][c] or self.flagged[r][c]:
            return

        self.revealed[r][c] = True
        btn = self.cells[(r, c)]
        value = self.numbers[r][c]

        if value == -1:  # Mine
            self.game_over = True
            self.restart_btn.config(text="💀")
            self.reveal_all_mines()
            messagebox.showerror("Game Over", "💥 You hit a mine!")
            return

        btn.config(relief="sunken", bg="#e0e0e0", state="disabled")

        if value == 0:
            btn.config(text=" ")
            # Flood fill
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal(r + dr, c + dc)
        else:
            colors = ["#0000ff", "#008200", "#ff0000", "#000080",
                     "#800000", "#008080", "#000000", "#808080"]
            btn.config(text=str(value), fg=colors[value-1])

        if self.check_win():
            self.game_over = True
            self.restart_btn.config(text="😎")
            messagebox.showinfo("Winner!", "🎉 Congratulations! You cleared the board!")

    def right_click(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return
        btn = self.cells[(r, c)]
        if self.flagged[r][c]:
            self.flagged[r][c] = False
            btn.config(text=" ", bg="#a0a0a0")
        else:
            self.flagged[r][c] = True
            btn.config(text="🏴", bg="#ffcc00")
        
        remaining = self.mines_total - sum(sum(row) for row in self.flagged)
        self.mines_left.config(text=f"💣 {max(0, remaining):03d}")

    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.numbers[r][c] == -1:
                    btn = self.cells[(r, c)]
                    btn.config(text="💣", bg="#ff6666", relief="sunken")

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.numbers[r][c] != -1 and not self.revealed[r][c]:
                    return False
        return True

    def update_timer(self):
        if not self.game_over and self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"{elapsed:03d}")
            self.master.after(100, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()