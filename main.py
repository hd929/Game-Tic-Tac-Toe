import pygame
import random
import math

# ── Constants ──────────────────────────────────────────────
WINDOW_WIDTH, WINDOW_HEIGHT = 400, 500
BOARD_X, BOARD_Y = 80, 50
CELL_SIZE = 80
BOARD_WIDTH, BOARD_HEIGHT = 240, 240
AI_DELAY_MS = 300
FPS = 60
ANIM_DURATION = 200  # ms for piece scale-in

# ── Dark theme colors ──────────────────────────────────────
BG_TOP = (22, 22, 44)
BG_BOT = (14, 16, 36)
BOARD_FILL = (18, 18, 38)
CELL_BG = (28, 28, 56)
CELL_HOVER = (48, 48, 88)
GRID_LINE = (55, 55, 90)
X_COLOR = (255, 95, 95)
O_COLOR = (65, 210, 250)
X_SHADOW = (160, 35, 35)
O_SHADOW = (25, 130, 170)
WIN_GLOW = (255, 210, 60)
BTN_DEFAULT = (100, 85, 220)
BTN_HOVER = (145, 125, 250)
BTN_TEXT = (235, 235, 250)
DIFF_EASY_C = (75, 195, 115)
DIFF_MED_C = (255, 195, 55)
DIFF_HARD_C = (255, 95, 95)
TEXT_MAIN = (225, 225, 240)
TEXT_X = (255, 125, 125)
TEXT_O = (100, 210, 255)
TEXT_DRAW = (255, 200, 75)
TEXT_OVER = (255, 80, 80)
TRY_AGAIN_BG = (120, 100, 230)
TRY_AGAIN_HOVER = (160, 140, 255)

# ── Winning combinations: (idx1, idx2, idx3, start_pos, end_pos) ──
WINNING_COMBOS = [
    (0, 1, 2, (100, 90), (300, 90)),
    (3, 4, 5, (100, 170), (300, 170)),
    (6, 7, 8, (100, 250), (300, 250)),
    (0, 3, 6, (120, 70), (120, 270)),
    (1, 4, 7, (200, 70), (200, 270)),
    (2, 5, 8, (280, 70), (280, 270)),
    (0, 4, 8, (100, 70), (300, 270)),
    (2, 4, 6, (300, 70), (100, 270)),
]

# ── Cell center positions ──────────────────────────────────
CELL_CENTERS = [
    (BOARD_X + 40 + (i % 3) * CELL_SIZE,
     BOARD_Y + 40 + (i // 3) * CELL_SIZE)
    for i in range(9)
]


class Game:
    """Tic-Tac-Toe with modern dark UI."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tic Tac Toe")
        try:
            icon = pygame.image.load("Tic-Tac-Toe.png")
            pygame.display.set_icon(icon)
        except Exception:
            pass
        self.clock = pygame.time.Clock()

        # ── Fonts ──
        self.font_main = pygame.font.Font("assets/font/SunnyspellsRegular.otf", 44)
        self.font_btn = pygame.font.Font("assets/font/SunnyspellsRegular.otf", 26)

        # ── Pre-render gradient background ──
        self._bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
            g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
            b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
            pygame.draw.line(self._bg_surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        # ── Pre-render static texts ──
        self._render_static_texts()

        # ── UI rectangles ──
        self.try_again_rect = pygame.Rect(100, 370, 200, 50)
        self.mode_btn_rect = pygame.Rect(40, 435, 150, 40)
        self.diff_btn_rect = pygame.Rect(210, 435, 150, 40)
        self.mode_btn_center_rect = pygame.Rect(125, 435, 150, 40)

        # ── Pre-render board ──
        self._board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        self._render_board()

        # ── State ──
        self.game_mode = 1       # 1: 1 Player, 2: 2 Players
        self.difficulty = "Hard" # Easy / Medium / Hard
        self.reset()
        self.running = True

        # ── AI ──
        self.ai_thinking = False
        self.ai_move_time = 0

        # ── Animation ──
        self.animations = []  # (cell_idx, start_ticks, piece)

        # ── Mouse / hover ──
        self.mouse_pos = (0, 0)
        self.hover_cell = None
        self.mode_hover = False
        self.diff_hover = False
        self.try_again_hover = False

        # ── Button cache ──
        self._cached_mode_text = None
        self._cached_mode_rect = None
        self._cached_diff_text = None
        self._cached_diff_rect = None
        self._cached_diff_color = None
        self._update_button_cache()

    # ══════════════════════════════════════════════════════════
    #  State management
    # ══════════════════════════════════════════════════════════

    def reset(self):
        self.box = [""] * 9
        self.playerwin = 0   # 0=playing, 1=X wins, 2=O wins, 3=Draw
        self.playerturn = 1  # X always starts
        self.winning_line = None
        self.ai_thinking = False
        self.animations = []

    # ══════════════════════════════════════════════════════════
    #  Pre-rendering helpers
    # ══════════════════════════════════════════════════════════

    def _render_static_texts(self):
        """Pre-render text surfaces for game-over states."""
        self.game_over_surf = self.font_main.render("Game Over", False, TEXT_OVER)
        self.game_over_rect = self.game_over_surf.get_rect(center=(200, 330))

        self.win_game_surf = self.font_main.render("You Win!", False, TEXT_X)
        self.win_game_rect = self.win_game_surf.get_rect(center=(200, 330))

        self.p1_win_surf = self.font_main.render("Player 1 (X) Wins!", False, TEXT_X)
        self.p1_win_rect = self.p1_win_surf.get_rect(center=(200, 330))

        self.p2_win_surf = self.font_main.render("Player 2 (O) Wins!", False, TEXT_O)
        self.p2_win_rect = self.p2_win_surf.get_rect(center=(200, 330))

        self.draw_surf = self.font_main.render("Draw!", False, TEXT_DRAW)
        self.draw_rect = self.draw_surf.get_rect(center=(200, 330))

        self.try_again_surf = self.font_main.render("Try Again", False, BTN_TEXT)
        self.try_again_surf_rect = self.try_again_surf.get_rect(center=(200, 395))

    def _render_board(self):
        """Pre-render the board with rounded cells."""
        self._board_surface.fill((0, 0, 0, 0))
        # Outer board background
        pygame.draw.rect(self._board_surface, BOARD_FILL,
                         (0, 0, BOARD_WIDTH, BOARD_HEIGHT), border_radius=16)
        # Individual cells
        for i in range(9):
            col, row = i % 3, i // 3
            cx, cy = col * CELL_SIZE, row * CELL_SIZE
            cell_rect = pygame.Rect(cx + 4, cy + 4, CELL_SIZE - 8, CELL_SIZE - 8)
            pygame.draw.rect(self._board_surface, CELL_BG,
                             cell_rect, border_radius=12)

    def _update_button_cache(self):
        """Re-render button text surfaces."""
        if self.game_mode == 1:
            self._cached_mode_text = self.font_btn.render(
                "Mode: 1 Player", False, BTN_TEXT
            )
            self._cached_mode_rect = self._cached_mode_text.get_rect(
                center=self.mode_btn_rect.center
            )
        else:
            self._cached_mode_text = self.font_btn.render(
                "Mode: 2 Players", False, BTN_TEXT
            )
            self._cached_mode_rect = self._cached_mode_text.get_rect(
                center=self.mode_btn_center_rect.center
            )

        if self.difficulty == "Hard":
            self._cached_diff_color = DIFF_HARD_C
        elif self.difficulty == "Medium":
            self._cached_diff_color = DIFF_MED_C
        else:
            self._cached_diff_color = DIFF_EASY_C

        self._cached_diff_text = self.font_btn.render(
            f"Bot: {self.difficulty}", False, BTN_TEXT
        )
        self._cached_diff_rect = self._cached_diff_text.get_rect(
            center=self.diff_btn_rect.center
        )

    # ══════════════════════════════════════════════════════════
    #  Piece drawing (programmatic X / O)
    # ══════════════════════════════════════════════════════════

    def _draw_x(self, surface, cx, cy, size, alpha=255, shadow=False):
        """Draw an X at center (cx, cy)."""
        color = X_SHADOW if shadow else X_COLOR
        off = 3 if shadow else 0
        half = size // 2
        thick = max(5, size // 7)
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        margin = size * 0.22
        pygame.draw.line(s, (*color, alpha),
                         (margin, margin),
                         (size - margin, size - margin), thick)
        pygame.draw.line(s, (*color, alpha),
                         (size - margin, margin),
                         (margin, size - margin), thick)
        surface.blit(s, (int(cx - half + off), int(cy - half + off)))

    def _draw_o(self, surface, cx, cy, size, alpha=255, shadow=False):
        """Draw an O at center (cx, cy)."""
        color = O_SHADOW if shadow else O_COLOR
        off = 3 if shadow else 0
        half = size // 2
        thick = max(5, size // 7)
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (half, half),
                           half * 0.72, thick)
        surface.blit(s, (int(cx - half + off), int(cy - half + off)))

    # ══════════════════════════════════════════════════════════
    #  Game logic (unchanged)
    # ══════════════════════════════════════════════════════════

    def check_win_condition(self, board):
        """Return (winner, line_data) or (None, None)."""
        for idx1, idx2, idx3, start_pos, end_pos in WINNING_COMBOS:
            if board[idx1] == board[idx2] == board[idx3] and board[idx1] != "":
                return board[idx1], (start_pos, end_pos)

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

        if self.difficulty == "Easy":
            best_move = random.choice(empty_spots)
        elif self.difficulty == "Medium":
            scored = []
            for i in empty_spots:
                self.box[i] = "O"
                score = self.get_best_move_minimax(self.box, False)
                self.box[i] = ""
                scored.append((score, i))
            scored.sort(key=lambda x: x[0], reverse=True)

            if random.random() < 0.4 and len(scored) > 2:
                mid = max(1, len(scored) // 2)
                best_move = random.choice(scored[mid:])[1]
            else:
                best_move = scored[0][1]
        else:  # Hard
            best_move = None
            if len(empty_spots) >= 8:
                preferred = [4, 0, 2, 6, 8]
                valid = [m for m in preferred if self.box[m] == ""]
                if valid:
                    best_move = random.choice(valid)

            if best_move is None:
                best_score = -float("inf")
                for i in empty_spots:
                    self.box[i] = "O"
                    score = self.get_best_move_minimax(self.box, False)
                    self.box[i] = ""
                    if score > best_score:
                        best_score = score
                        best_move = i

        if best_move is not None:
            self.box[best_move] = "O"
            self.animations.append((best_move, pygame.time.get_ticks(), "O"))

        self.playerturn = 1
        self.ai_thinking = False

    # ══════════════════════════════════════════════════════════
    #  Input handling
    # ══════════════════════════════════════════════════════════

    def _update_hover(self, mx, my):
        """Update hover states based on mouse position."""
        self.mouse_pos = (mx, my)

        # Cell hover
        self.hover_cell = None
        if self.playerwin == 0:
            if BOARD_X <= mx <= BOARD_X + BOARD_WIDTH and \
               BOARD_Y <= my <= BOARD_Y + BOARD_HEIGHT:
                col = (mx - BOARD_X) // CELL_SIZE
                row = (my - BOARD_Y) // CELL_SIZE
                idx = row * 3 + col
                if 0 <= idx < 9 and self.box[idx] == "":
                    # In 1P mode, only show hover on player's turn
                    if self.game_mode == 2 or self.playerturn == 1:
                        self.hover_cell = idx

        # Button hovers
        self.mode_hover = self._mode_btn_rect().collidepoint(mx, my)
        self.diff_hover = (
            self.game_mode == 1 and self.diff_btn_rect.collidepoint(mx, my)
        )
        self.try_again_hover = (
            self.playerwin != 0 and self.try_again_rect.collidepoint(mx, my)
        )

    def _mode_btn_rect(self):
        return self.mode_btn_rect if self.game_mode == 1 else self.mode_btn_center_rect

    def handle_click(self, mx, my):
        """Process a left-click."""
        # Mode toggle
        if self._mode_btn_rect().collidepoint(mx, my):
            self.game_mode = 2 if self.game_mode == 1 else 1
            self.reset()
            self._update_button_cache()
            return

        # Difficulty toggle (1P only)
        if self.game_mode == 1 and self.diff_btn_rect.collidepoint(mx, my):
            order = ["Hard", "Medium", "Easy"]
            idx = order.index(self.difficulty)
            self.difficulty = order[(idx + 1) % 3]
            self.reset()
            self._update_button_cache()
            return

        # Try Again
        if self.playerwin != 0 and self.try_again_rect.collidepoint(mx, my):
            self.reset()
            return

        # Board click
        if self.playerwin == 0:
            if BOARD_X <= mx <= BOARD_X + BOARD_WIDTH and \
               BOARD_Y <= my <= BOARD_Y + BOARD_HEIGHT:
                col = (mx - BOARD_X) // CELL_SIZE
                row = (my - BOARD_Y) // CELL_SIZE
                idx = int(row * 3 + col)

                if 0 <= idx < 9 and self.box[idx] == "":
                    if self.game_mode == 1 and self.playerturn == 1:
                        self.box[idx] = "X"
                        self.animations.append(
                            (idx, pygame.time.get_ticks(), "X")
                        )
                        self.playerturn = 2
                    elif self.game_mode == 2:
                        piece = "X" if self.playerturn == 1 else "O"
                        self.box[idx] = piece
                        self.animations.append(
                            (idx, pygame.time.get_ticks(), piece)
                        )
                        self.playerturn = 2 if self.playerturn == 1 else 1

    # ══════════════════════════════════════════════════════════
    #  Update loop
    # ══════════════════════════════════════════════════════════

    def update(self):
        """Check win condition and handle AI."""
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

        # AI timer
        if (
            self.game_mode == 1
            and self.playerwin == 0
            and self.playerturn == 2
            and not self.ai_thinking
        ):
            self.ai_thinking = True
            self.ai_move_time = pygame.time.get_ticks() + AI_DELAY_MS

        if self.ai_thinking and pygame.time.get_ticks() >= self.ai_move_time:
            self.ai_turn()

        # Clean expired animations
        now = pygame.time.get_ticks()
        self.animations = [
            a for a in self.animations if now - a[1] < ANIM_DURATION
        ]

    # ══════════════════════════════════════════════════════════
    #  Drawing
    # ══════════════════════════════════════════════════════════

    def _draw_button(self, rect, color, hover_color, is_hovered, text_surf, text_rect):
        """Draw a rounded button with hover effect."""
        c = hover_color if is_hovered else color
        pygame.draw.rect(self.screen, c, rect, border_radius=10)
        # subtle highlight on top
        if is_hovered:
            hl = pygame.Rect(rect.x + 2, rect.y + 1, rect.width - 4, 3)
            pygame.draw.rect(self.screen, (200, 200, 255, 100), hl, border_radius=2)
        self.screen.blit(text_surf, text_rect)

    def _draw_winning_line(self, start, end):
        """Draw glowing winning line."""
        # Outer glow
        for i in range(5, 0, -1):
            alpha = 30 + i * 15
            width = 2 + i * 3
            glow = pygame.Surface((BOARD_WIDTH + 30, BOARD_HEIGHT + 30), pygame.SRCALPHA)
            ox, oy = start[0] - BOARD_X + 15, start[1] - BOARD_Y + 15
            ex, ey = end[0] - BOARD_X + 15, end[1] - BOARD_Y + 15
            pygame.draw.line(glow, (*WIN_GLOW, alpha), (ox, oy), (ex, ey), width)
            self.screen.blit(glow, (BOARD_X - 15, BOARD_Y - 15))
        # Core
        pygame.draw.line(self.screen, WIN_GLOW, start, end, 4)

    def _draw_hover_preview(self):
        """Draw semi-transparent preview of the piece to be placed."""
        if self.hover_cell is None:
            return
        cx, cy = CELL_CENTERS[self.hover_cell]
        if self.game_mode == 1:
            piece = "X"  # player is always X in 1P
        else:
            piece = "X" if self.playerturn == 1 else "O"

        if piece == "X":
            self._draw_x(self.screen, cx, cy, 50, alpha=40)
        else:
            self._draw_o(self.screen, cx, cy, 50, alpha=40)

    def _get_anim_scale(self, start_ticks):
        """Return scale factor (0.3 → 1.0) with ease-out."""
        now = pygame.time.get_ticks()
        elapsed = now - start_ticks
        t = min(elapsed / ANIM_DURATION, 1.0)
        # Ease-out cubic
        t = 1 - (1 - t) ** 3
        return 0.3 + 0.7 * t

    def _draw_pieces(self):
        """Draw X and O pieces, with animations where active."""
        now = pygame.time.get_ticks()
        anim_set = {a[0] for a in self.animations}

        for idx, val in enumerate(self.box):
            if val == "":
                continue
            if idx in anim_set:
                continue  # drawn below with animation

            cx, cy = CELL_CENTERS[idx]
            if val == "X":
                self._draw_x(self.screen, cx, cy, 50, shadow=True)
                self._draw_x(self.screen, cx, cy, 50)
            else:
                self._draw_o(self.screen, cx, cy, 50, shadow=True)
                self._draw_o(self.screen, cx, cy, 50)

        # Animated pieces
        for cell_idx, start_ticks, piece in self.animations:
            scale = self._get_anim_scale(start_ticks)
            size = int(50 * scale)
            cx, cy = CELL_CENTERS[cell_idx]
            alpha = int(255 * scale)
            if piece == "X":
                self._draw_x(self.screen, cx, cy, size, alpha=alpha, shadow=True)
                self._draw_x(self.screen, cx, cy, size, alpha=alpha)
            else:
                self._draw_o(self.screen, cx, cy, size, alpha=alpha, shadow=True)
                self._draw_o(self.screen, cx, cy, size, alpha=alpha)

    def draw(self):
        """Render everything."""
        # Background
        self.screen.blit(self._bg_surface, (0, 0))

        # Board
        self.screen.blit(self._board_surface, (BOARD_X, BOARD_Y))

        # Hover cell highlight
        if self.hover_cell is not None:
            col, row = self.hover_cell % 3, self.hover_cell // 3
            cx, cy = BOARD_X + col * CELL_SIZE, BOARD_Y + row * CELL_SIZE
            cell_rect = pygame.Rect(cx + 4, cy + 4, CELL_SIZE - 8, CELL_SIZE - 8)
            pygame.draw.rect(self.screen, CELL_HOVER, cell_rect, border_radius=12)

        # Pieces
        self._draw_pieces()

        # Hover preview
        self._draw_hover_preview()

        # Winning line
        if self.winning_line:
            _, line_data = self.winning_line
            if line_data:
                self._draw_winning_line(*line_data)

        # ── Game-over overlay ──
        if self.playerwin != 0:
            # Dim overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))

            # Result text
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

            # Try Again button
            bg_color = TRY_AGAIN_HOVER if self.try_again_hover else TRY_AGAIN_BG
            pygame.draw.rect(self.screen, bg_color,
                             self.try_again_rect, border_radius=12)
            self.screen.blit(self.try_again_surf, self.try_again_surf_rect)

        # ── Bottom buttons ──
        if self.game_mode == 1:
            self._draw_button(
                self.mode_btn_rect, BTN_DEFAULT, BTN_HOVER,
                self.mode_hover, self._cached_mode_text, self._cached_mode_rect
            )
            self._draw_button(
                self.diff_btn_rect, self._cached_diff_color,
                self._cached_diff_color,  # no distinct hover for diff button
                self.diff_hover, self._cached_diff_text, self._cached_diff_rect
            )
        else:
            self._draw_button(
                self.mode_btn_center_rect, BTN_DEFAULT, BTN_HOVER,
                self.mode_hover, self._cached_mode_text, self._cached_mode_rect
            )

        pygame.display.flip()

    # ══════════════════════════════════════════════════════════
    #  Main loop
    # ══════════════════════════════════════════════════════════

    def run(self):
        """Start the main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(*event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._update_hover(*event.pos)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


# ── Entry point ───────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
