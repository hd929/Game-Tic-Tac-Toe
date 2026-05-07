import pygame
import random

# ── Constants ──────────────────────────────────────────────
WINDOW_WIDTH, WINDOW_HEIGHT = 400, 500
BOARD_X, BOARD_Y = 80, 50
CELL_SIZE = 80
BOARD_WIDTH, BOARD_HEIGHT = 240, 240
AI_DELAY_MS = 300
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (50, 190, 50)
YELLOW = (255, 170, 0)
BORDER = (85, 85, 85)
X_LINE = (255, 0, 0)
O_LINE = (51, 130, 177)
BTN_COLOR = (220, 220, 220)
DIFF_EASY_COLOR = (150, 255, 150)
DIFF_MED_COLOR = (255, 220, 120)
DIFF_HARD_COLOR = (255, 150, 150)

# Winning combinations: (idx1, idx2, idx3, start_pos, end_pos, line_width)
WINNING_COMBOS = [
    (0, 1, 2, (100, 90), (300, 90), 5),
    (3, 4, 5, (100, 170), (300, 170), 5),
    (6, 7, 8, (100, 250), (300, 250), 5),
    (0, 3, 6, (120, 70), (120, 270), 5),
    (1, 4, 7, (200, 70), (200, 270), 5),
    (2, 5, 8, (280, 70), (280, 270), 5),
    (0, 4, 8, (100, 70), (300, 270), 10),
    (2, 4, 6, (300, 70), (100, 270), 10),
]

# Pre-compute cell positions for X/O images
CELL_POSITIONS = [
    (BOARD_X + 40 + (i % 3) * CELL_SIZE - 25,
     BOARD_Y + 40 + (i // 3) * CELL_SIZE - 25)
    for i in range(9)
]


class Game:
    """Encapsulates all game state and logic for Tic-Tac-Toe."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tic Tac Toe")
        icon = pygame.image.load("Tic-Tac-Toe.png")
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()

        # Load fonts
        self.font_main = pygame.font.Font("assets/font/SunnyspellsRegular.otf", 50)
        self.font_btn = pygame.font.Font("assets/font/SunnyspellsRegular.otf", 30)

        # Load and scale images
        self.X_img = pygame.transform.scale(
            pygame.image.load("assets/img/X.png").convert_alpha(), (50, 50)
        )
        self.O_img = pygame.transform.scale(
            pygame.image.load("assets/img/O.png").convert_alpha(), (50, 50)
        )

        # Pre-render static text surfaces
        self._render_static_texts()

        # UI rectangles
        self.try_again_rect = pygame.Rect(100, 373, 200, 45)
        self.mode_btn_rect = pygame.Rect(40, 435, 150, 40)
        self.diff_btn_rect = pygame.Rect(210, 435, 150, 40)
        self.mode_btn_center_rect = pygame.Rect(125, 435, 150, 40)

        # "Try Again" background
        self.try_again_bg = pygame.Surface((200, 45))
        self.try_again_bg.fill(GREEN)
        self.try_again_bg.set_alpha(80)

        # State
        self.game_mode = 1     # 1: 1 Player (Vs AI), 2: 2 Players
        self.difficulty = "Hard"  # "Easy", "Medium", "Hard"
        self.reset()
        self.running = True

        # AI timer (non-blocking)
        self.ai_thinking = False
        self.ai_move_time = 0

        # Cached button texts (updated only when state changes)
        self._cached_mode_text = None
        self._cached_mode_rect = None
        self._cached_diff_text = None
        self._cached_diff_rect = None
        self._cached_diff_color = None
        self._update_button_cache()

    # ── State management ──────────────────────────────────

    def reset(self):
        """Reset the game board to its initial state."""
        self.box = [""] * 9
        self.playerwin = 0   # 0=playing, 1=X wins, 2=O wins, 3=Draw
        self.playerturn = 1  # X always starts
        self.winning_line = None
        self.ai_thinking = False

    # ── Rendering helpers ─────────────────────────────────

    def _render_static_texts(self):
        """Pre-render text surfaces that never change."""
        self.game_over_surf = self.font_main.render("Game Over", False, RED)
        self.game_over_rect = self.game_over_surf.get_rect(center=(200, 330))

        self.win_game_surf = self.font_main.render("You Win!", False, GREEN)
        self.win_game_rect = self.win_game_surf.get_rect(center=(200, 330))

        self.p1_win_surf = self.font_main.render("Player 1 (X) Wins!", False, GREEN)
        self.p1_win_rect = self.p1_win_surf.get_rect(center=(200, 330))

        self.p2_win_surf = self.font_main.render("Player 2 (O) Wins!", False, O_LINE)
        self.p2_win_rect = self.p2_win_surf.get_rect(center=(200, 330))

        self.draw_surf = self.font_main.render("Draw!", False, YELLOW)
        self.draw_rect = self.draw_surf.get_rect(center=(200, 330))

        self.try_again_surf = self.font_main.render("Try Again", False, BLACK)
        self.try_again_surf_rect = self.try_again_surf.get_rect(center=(200, 395))

    def _update_button_cache(self):
        """Re-render button text surfaces (called only when mode/difficulty changes)."""
        if self.game_mode == 1:
            self._cached_mode_text = self.font_btn.render("Mode: 1 Player", False, BLACK)
            self._cached_mode_rect = self._cached_mode_text.get_rect(
                center=self.mode_btn_rect.center
            )
        else:
            self._cached_mode_text = self.font_btn.render("Mode: 2 Players", False, BLACK)
            self._cached_mode_rect = self._cached_mode_text.get_rect(
                center=self.mode_btn_center_rect.center
            )

        if self.difficulty == "Hard":
            self._cached_diff_color = DIFF_HARD_COLOR
        elif self.difficulty == "Medium":
            self._cached_diff_color = DIFF_MED_COLOR
        else:
            self._cached_diff_color = DIFF_EASY_COLOR

        self._cached_diff_text = self.font_btn.render(
            f"Bot: {self.difficulty}", False, BLACK
        )
        self._cached_diff_rect = self._cached_diff_text.get_rect(
            center=self.diff_btn_rect.center
        )

    # ── Game logic ────────────────────────────────────────

    def check_win_condition(self, board):
        """Return (winner, line_data) or (None, None)."""
        for idx1, idx2, idx3, start_pos, end_pos, size in WINNING_COMBOS:
            if board[idx1] == board[idx2] == board[idx3] and board[idx1] != "":
                return board[idx1], (start_pos, end_pos, size)

        if "" not in board:
            return "Draw", None

        return None, None

    def get_best_move_minimax(self, board, is_maximizing, depth=0):
        """Minimax scoring for the AI opponent."""
        winner, _ = self.check_win_condition(board)
        if winner == "O":
            return 10 - depth
        elif winner == "X":
            return depth - 10
        elif winner == "Draw":
            return 0

        if is_maximizing:
            best_score = -float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = "O"
                    score = self.get_best_move_minimax(board, False, depth + 1)
                    board[i] = ""
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = "X"
                    score = self.get_best_move_minimax(board, True, depth + 1)
                    board[i] = ""
                    best_score = min(score, best_score)
            return best_score

    def ai_turn(self):
        """Compute and execute the AI's move."""
        empty_spots = [i for i, x in enumerate(self.box) if x == ""]
        if not empty_spots:
            return

        best_move = None
        make_random_move = False

        if self.difficulty == "Easy":
            make_random_move = True
        elif self.difficulty == "Medium":
            if random.random() < 0.4:
                make_random_move = True

        if make_random_move:
            best_move = random.choice(empty_spots)
        else:
            if len(empty_spots) >= 8:
                possible_moves = [4, 0, 2, 6, 8]
                valid_moves = [m for m in possible_moves if self.box[m] == ""]
                if valid_moves:
                    best_move = random.choice(valid_moves)

            if best_move is None:
                best_score = -float("inf")
                for i in range(9):
                    if self.box[i] == "":
                        self.box[i] = "O"
                        score = self.get_best_move_minimax(self.box, False)
                        self.box[i] = ""
                        if score > best_score:
                            best_score = score
                            best_move = i

        if best_move is None and empty_spots:
            best_move = random.choice(empty_spots)

        if best_move is not None:
            self.box[best_move] = "O"

        self.playerturn = 1
        self.ai_thinking = False

    # ── Input handling ────────────────────────────────────

    def handle_click(self, mouse_x, mouse_y):
        """Process a left-click at the given coordinates."""
        # Mode toggle button
        curr_mode_rect = (
            self.mode_btn_rect if self.game_mode == 1 else self.mode_btn_center_rect
        )
        if curr_mode_rect.collidepoint(mouse_x, mouse_y):
            self.game_mode = 2 if self.game_mode == 1 else 1
            self.reset()
            self._update_button_cache()
            return

        # Difficulty toggle button (only in 1-player mode)
        if self.game_mode == 1 and self.diff_btn_rect.collidepoint(mouse_x, mouse_y):
            if self.difficulty == "Hard":
                self.difficulty = "Medium"
            elif self.difficulty == "Medium":
                self.difficulty = "Easy"
            else:
                self.difficulty = "Hard"
            self.reset()
            self._update_button_cache()
            return

        # Try Again button (only visible when game is over)
        if self.playerwin != 0 and self.try_again_rect.collidepoint(mouse_x, mouse_y):
            self.reset()
            return

        # Game board click
        if self.playerwin == 0:
            if BOARD_X <= mouse_x <= BOARD_X + BOARD_WIDTH and BOARD_Y <= mouse_y <= BOARD_Y + BOARD_HEIGHT:
                col = (mouse_x - BOARD_X) // CELL_SIZE
                row = (mouse_y - BOARD_Y) // CELL_SIZE
                index = int(row * 3 + col)

                if 0 <= index < 9 and self.box[index] == "":
                    if self.game_mode == 1 and self.playerturn == 1:
                        self.box[index] = "X"
                        self.playerturn = 2
                    elif self.game_mode == 2:
                        self.box[index] = "X" if self.playerturn == 1 else "O"
                        self.playerturn = 2 if self.playerturn == 1 else 1

    # ── Main update ───────────────────────────────────────

    def update(self):
        """Check win condition and handle AI turn initiation."""
        if self.playerwin == 0:
            winner, line_data = self.check_win_condition(self.box)
            if winner == "X":
                self.playerwin = 1
                self.winning_line = ("X", line_data)
            elif winner == "O":
                self.playerwin = 2
                self.winning_line = ("O", line_data)
            elif winner == "Draw":
                self.playerwin = 3

        # Non-blocking AI: start timer instead of sleeping
        if (
            self.game_mode == 1
            and self.playerwin == 0
            and self.playerturn == 2
            and not self.ai_thinking
        ):
            self.ai_thinking = True
            self.ai_move_time = pygame.time.get_ticks() + AI_DELAY_MS

        # Fire AI move when timer expires
        if self.ai_thinking and pygame.time.get_ticks() >= self.ai_move_time:
            self.ai_turn()

    # ── Rendering ─────────────────────────────────────────

    def draw(self):
        """Render the entire game to the screen."""
        self.screen.fill(WHITE)

        # Draw board grid
        pygame.draw.rect(self.screen, BORDER, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT), 2)
        pygame.draw.line(self.screen, BORDER, (BOARD_X, BOARD_Y + CELL_SIZE), (BOARD_X + BOARD_WIDTH, BOARD_Y + CELL_SIZE), 2)
        pygame.draw.line(self.screen, BORDER, (BOARD_X, BOARD_Y + CELL_SIZE * 2), (BOARD_X + BOARD_WIDTH, BOARD_Y + CELL_SIZE * 2), 2)
        pygame.draw.line(self.screen, BORDER, (BOARD_X + CELL_SIZE, BOARD_Y), (BOARD_X + CELL_SIZE, BOARD_Y + BOARD_HEIGHT), 2)
        pygame.draw.line(self.screen, BORDER, (BOARD_X + CELL_SIZE * 2, BOARD_Y), (BOARD_X + CELL_SIZE * 2, BOARD_Y + BOARD_HEIGHT), 2)

        # Draw X and O pieces
        for idx, val in enumerate(self.box):
            if val == "X":
                self.screen.blit(self.X_img, CELL_POSITIONS[idx])
            elif val == "O":
                self.screen.blit(self.O_img, CELL_POSITIONS[idx])

        # Draw winning line
        if self.winning_line:
            char, line_data = self.winning_line
            if line_data:
                start_pos, end_pos, size = line_data
                color = X_LINE if char == "X" else O_LINE
                pygame.draw.line(self.screen, color, start_pos, end_pos, size)

        # Draw game-over UI
        if self.playerwin != 0:
            if self.playerwin == 1:
                if self.game_mode == 1:
                    self.screen.blit(self.win_game_surf, self.win_game_rect)
                else:
                    self.screen.blit(self.p1_win_surf, self.p1_win_rect)
            elif self.playerwin == 2:
                if self.game_mode == 1:
                    self.screen.blit(self.game_over_surf, self.game_over_rect)
                else:
                    self.screen.blit(self.p2_win_surf, self.p2_win_rect)
            elif self.playerwin == 3:
                self.screen.blit(self.draw_surf, self.draw_rect)

            self.screen.blit(self.try_again_bg, self.try_again_rect)
            self.screen.blit(self.try_again_surf, self.try_again_surf_rect)

        # Draw menu buttons (uses cached surfaces)
        if self.game_mode == 1:
            pygame.draw.rect(self.screen, BTN_COLOR, self.mode_btn_rect, border_radius=10)
            self.screen.blit(self._cached_mode_text, self._cached_mode_rect)

            pygame.draw.rect(self.screen, self._cached_diff_color, self.diff_btn_rect, border_radius=10)
            self.screen.blit(self._cached_diff_text, self._cached_diff_rect)
        else:
            pygame.draw.rect(self.screen, BTN_COLOR, self.mode_btn_center_rect, border_radius=10)
            self.screen.blit(self._cached_mode_text, self._cached_mode_rect)

        pygame.display.flip()

    # ── Main loop ─────────────────────────────────────────

    def run(self):
        """Start the main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(*event.pos)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


# ── Entry point ───────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
