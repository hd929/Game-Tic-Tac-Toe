import pygame, random

pygame.init()

screen = pygame.display.set_mode((400, 500))
pygame.display.set_caption("Tic Tac Toe")
icon = pygame.image.load("Tic-Tac-Toe.png")
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

running = True

font_main = pygame.font.Font("assets/font/SunnyspellsRegular.otf", 50)
font_btn = pygame.font.Font("assets/font/SunnyspellsRegular.otf", 30)

X = pygame.image.load("assets/img/X.png").convert_alpha()
X = pygame.transform.scale(X, (50, 50))
O = pygame.image.load("assets/img/O.png").convert_alpha()
O = pygame.transform.scale(O, (50, 50))

box = [""] * 9

playerwin = 0 # 0: Playing, 1: X wins, 2: O wins, 3: Draw
playerturn = 1 # 1: X(P1), 2: O(P2/AI)
winning_line = None 
game_mode = 1 # 1: 1 Player (Vs AI), 2: 2 Players
difficulty = "Hard" # "Easy", "Medium", "Hard"

# Define colors
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

game_over = font_main.render("Game Over", False, RED)
game_over_rect = game_over.get_rect(center=(200, 330))

win_game = font_main.render("You Win!", False, GREEN)
win_game_rect = win_game.get_rect(center=(200, 330))

p1_win = font_main.render("Player 1 (X) Wins!", False, GREEN)
p1_win_rect = p1_win.get_rect(center=(200, 330))

p2_win = font_main.render("Player 2 (O) Wins!", False, O_LINE)
p2_win_rect = p2_win.get_rect(center=(200, 330))

draw = font_main.render("Draw!", False, YELLOW)
draw_rect = draw.get_rect(center=(200, 330))

try_again_bg = pygame.Surface((200, 45))
try_again_bg.fill(GREEN)
try_again_bg.set_alpha(80)

try_again = font_main.render("Try Again", False, BLACK)
try_again_rect = try_again.get_rect(center=(200, 395))
try_again_rect_click = pygame.Rect(100, 373, 200, 45)

mode_btn_rect = pygame.Rect(40, 435, 150, 40)
diff_btn_rect = pygame.Rect(210, 435, 150, 40)
mode_btn_rect_center = pygame.Rect(125, 435, 150, 40) # When 2-player mode, place button at center

# Calculate positions dynamically for X and O
CELL_POSITIONS = [(120 + (i % 3) * 80 - 25, 90 + (i // 3) * 80 - 25) for i in range(9)]

# Winning combinations
WINNING_COMBOS = [
    (0, 1, 2, (100, 90), (300, 90), 5),
    (3, 4, 5, (100, 170), (300, 170), 5),
    (6, 7, 8, (100, 250), (300, 250), 5),
    (0, 3, 6, (120, 70), (120, 270), 5),
    (1, 4, 7, (200, 70), (200, 270), 5),
    (2, 5, 8, (280, 70), (280, 270), 5),
    (0, 4, 8, (100, 70), (300, 270), 10),
    (2, 4, 6, (300, 70), (100, 270), 10)
]

def check_win_condition(board):
    for index1, index2, index3, start_pos, end_pos, size in WINNING_COMBOS:
        if board[index1] == board[index2] == board[index3] and board[index1] != "":
            return board[index1], (start_pos, end_pos, size)
    
    if "" not in board:
        return "Draw", None
        
    return None, None

def get_best_move_minimax(board, is_maximizing, depth=0):
    winner, _ = check_win_condition(board)
    if winner == "O": return 10 - depth
    elif winner == "X": return depth - 10
    elif winner == "Draw": return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                score = get_best_move_minimax(board, False, depth + 1)
                board[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                score = get_best_move_minimax(board, True, depth + 1)
                board[i] = ""
                best_score = min(score, best_score)
        return best_score

def ai_turn():
    global playerturn
    pygame.time.delay(300)
    
    empty_spots = [i for i, x in enumerate(box) if x == ""]
    if not empty_spots: return
    
    best_move = None
    make_random_move = False
    
    # Adjust difficulty
    if difficulty == "Easy":
        make_random_move = True # 100% random chance
    elif difficulty == "Medium":
        if random.random() < 0.4: # 40% random chance
            make_random_move = True
            
    if make_random_move:
        best_move = random.choice(empty_spots)
    else:
        if len(empty_spots) >= 8:
            possible_moves = [4, 0, 2, 6, 8]
            valid_moves = [m for m in possible_moves if box[m] == ""]
            if valid_moves:
                best_move = random.choice(valid_moves)
                
        if best_move is None:
            best_score = -float('inf')
            for i in range(9):
                if box[i] == "":
                    box[i] = "O"
                    score = get_best_move_minimax(box, False)
                    box[i] = ""
                    if score > best_score:
                        best_score = score
                        best_move = i
                        
    if best_move is None and empty_spots:
        best_move = random.choice(empty_spots)
            
    if best_move is not None:
        box[best_move] = "O"
    
    playerturn = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            
            # Click Mode Button
            curr_mode_rect = mode_btn_rect if game_mode == 1 else mode_btn_rect_center
            if curr_mode_rect.collidepoint(mouse_x, mouse_y):
                game_mode = 2 if game_mode == 1 else 1
                box = [""] * 9
                playerwin = 0
                playerturn = 1
                winning_line = None
                
            # Click Difficulty Button
            elif game_mode == 1 and diff_btn_rect.collidepoint(mouse_x, mouse_y):
                if difficulty == "Hard": difficulty = "Medium"
                elif difficulty == "Medium": difficulty = "Easy"
                else: difficulty = "Hard"
                box = [""] * 9
                playerwin = 0
                playerturn = 1
                winning_line = None
            
            # Click Try Again Button
            elif playerwin != 0 and try_again_rect_click.collidepoint(mouse_x, mouse_y):
                playerturn = 2 if (playerwin == 2 and game_mode == 1) else 1
                box = [""] * 9
                playerwin = 0
                winning_line = None
            
            # Click on Game Board
            elif playerwin == 0:
                if 80 <= mouse_x <= 320 and 50 <= mouse_y <= 290:
                    col = (mouse_x - 80) // 80
                    row = (mouse_y - 50) // 80
                    index = int(row * 3 + col)
                    
                    if 0 <= index < 9 and box[index] == "":
                        if game_mode == 1 and playerturn == 1:
                            box[index] = "X"
                            playerturn = 2
                        elif game_mode == 2:
                            box[index] = "X" if playerturn == 1 else "O"
                            playerturn = 2 if playerturn == 1 else 1

    if playerwin == 0:
        winner, line_data = check_win_condition(box)
        if winner == "X":
            playerwin = 1
            winning_line = ("X", line_data)
        elif winner == "O":
            playerwin = 2
            winning_line = ("O", line_data)
        elif winner == "Draw":
            playerwin = 3

    screen.fill(WHITE)

    # Drawing Board Grid
    pygame.draw.rect(screen, BORDER, (80, 50, 240, 240), 2)
    pygame.draw.line(screen, BORDER, (80, 130), (320, 130), 2)
    pygame.draw.line(screen, BORDER, (80, 210), (320, 210), 2)
    pygame.draw.line(screen, BORDER, (160, 50), (160, 290), 2)
    pygame.draw.line(screen, BORDER, (240, 50), (240, 290), 2)

    for idx, val in enumerate(box):
        if val == "X":
            screen.blit(X, CELL_POSITIONS[idx])
        elif val == "O":
            screen.blit(O, CELL_POSITIONS[idx])

    if winning_line:
        char, line_data = winning_line
        if line_data:
            start_pos, end_pos, size = line_data
            color = X_LINE if char == "X" else O_LINE
            pygame.draw.line(screen, color, start_pos, end_pos, size)

    # UI elements
    if playerwin != 0:
        if playerwin == 1:
            screen.blit(win_game if game_mode == 1 else p1_win, win_game_rect if game_mode == 1 else p1_win_rect)
        elif playerwin == 2:
            screen.blit(game_over if game_mode == 1 else p2_win, game_over_rect if game_mode == 1 else p2_win_rect)
        elif playerwin == 3:
            screen.blit(draw, draw_rect)
            
        screen.blit(try_again_bg, try_again_rect_click)
        screen.blit(try_again, try_again_rect)
        
    # Draw Menu Buttons
    if game_mode == 1:
        # Mode Toggle
        pygame.draw.rect(screen, BTN_COLOR, mode_btn_rect, border_radius=10)
        mode_text = font_btn.render("Mode: 1 Player", False, BLACK)
        mode_text_rect = mode_text.get_rect(center=mode_btn_rect.center)
        screen.blit(mode_text, mode_text_rect)
        
        # Difficulty Toggle
        diff_color = DIFF_HARD_COLOR
        if difficulty == "Medium": diff_color = DIFF_MED_COLOR
        elif difficulty == "Easy": diff_color = DIFF_EASY_COLOR
        pygame.draw.rect(screen, diff_color, diff_btn_rect, border_radius=10)
        diff_text = font_btn.render(f"Bot: {difficulty}", False, BLACK)
        diff_text_rect = diff_text.get_rect(center=diff_btn_rect.center)
        screen.blit(diff_text, diff_text_rect)
    else:
        # Mode Toggle Center
        pygame.draw.rect(screen, BTN_COLOR, mode_btn_rect_center, border_radius=10)
        mode_text = font_btn.render("Mode: 2 Players", False, BLACK)
        mode_text_rect = mode_text.get_rect(center=mode_btn_rect_center.center)
        screen.blit(mode_text, mode_text_rect)

    pygame.display.flip()
    
    # Process AI move only if in Mode 1
    if game_mode == 1 and playerwin == 0 and playerturn == 2:
        ai_turn()

    clock.tick(60)

pygame.quit()
