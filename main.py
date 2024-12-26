import pygame
import sys
import random
import math

pygame.init()

# Screen and Grid Configuration
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
BOARD_COLS = 10
BOARD_ROWS = 10
BOX_SIZE = 50
BOARD_SPACING = 100
TOTAL_BOARD_WIDTH = 2 * (BOARD_COLS * BOX_SIZE) + BOARD_SPACING
CENTER_OFFSET_X = (SCREEN_WIDTH - TOTAL_BOARD_WIDTH) // 2

# Color Configuration
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'OCEAN_BLUE': (0, 128, 255),
    'SHIP_GRAY': (128, 128, 128),
    'HIT_RED': (255, 69, 0),
    'MISS_ORANGE': (255, 165, 0),
    'BACKGROUND_NAVY': (25, 25, 112),
    'GRID_LINE': (255, 255, 0),
    'AI_HIDDEN': (0, 191, 255)
}

hit_text_time = None
miss_text_time = None
text_duration = 2000
message_text = None
message_color = None
message_start_time = 0

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship AI- FAI Project")
font = pygame.font.SysFont(None, 36)

# Load Ship Images
SHIP_IMAGES = {
    'carrier': pygame.image.load("ship1.png"),
    'battleship': pygame.image.load("ship2.png"),
    'cruiser': pygame.image.load("ship3.png"),
    'submarine': pygame.image.load("ship4.png"),
    'destroyer': pygame.image.load("ship5.png")
}

for key in SHIP_IMAGES:
    SHIP_IMAGES[key] = pygame.transform.scale(SHIP_IMAGES[key], (BOX_SIZE, BOX_SIZE))

"""
Renders text on the screen with specified properties.
"""
def draw_text_on_screen(text, color, center_position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_position)
    screen.blit(text_surface, text_rect)

class StartPage:
    """
    Handles the game's start page interface and interaction.
    """
    def __init__(self):
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
        self.font = pygame.font.SysFont(None, 48)

    """
    Renders the start page with title and start button.
    """
    def draw(self, screen):
        screen.fill(COLORS['BACKGROUND_NAVY'])
        title = self.font.render("Battleship AI | FAI Project 2024", True, COLORS['WHITE'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3-50))
        screen.blit(title, title_rect)

        names_line = "Adithya | Varun | Abhinav | Aadarsh"
        names_text = self.font.render(names_line, True, (255,200,200))
        names_rect = names_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(names_text, names_rect)
        
        pygame.draw.rect(screen, COLORS['OCEAN_BLUE'], self.start_button_rect)
        start_text = font.render("Start Game", True, COLORS['WHITE'])
        start_text_rect = start_text.get_rect(center=self.start_button_rect.center)
        screen.blit(start_text, start_text_rect)
        pygame.display.flip()

    """
    Checks if the start button was clicked.
    """
    def check_for_start_click(self, mouse_pos):
        if self.start_button_rect.collidepoint(mouse_pos):
            return True

class SmartAI:
    """
    Implements intelligent AI targeting strategy for the game.
    """
    def __init__(self, board_size):
        self.board_size = board_size
        self.last_hit = None
        self.hunt_mode = True
        self.direction = None
        self.ship_segments = []
        self.remaining_ships = [5, 4, 3, 3, 2]
        self.ship_hits = {
            'carrier': 0,
            'battleship': 0,
            'cruiser': 0,
            'submarine': 0,
            'destroyer': 0
        }
        self.ships_sunk = []

    """
    Determines the next target based on current game state.
    """
    def choose_target(self, player_board):
        if not self.hunt_mode and self.last_hit:
            return self._target_mode(player_board)
        return self._hunt_mode(player_board)

    """
    Implements checkerboard hunting strategy for finding ships.
    """
    def _hunt_mode(self, player_board):
        candidates = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if ((x + y) % 2 == 0) and player_board[x][y] in ['', *list(SHIP_IMAGES.keys())]:
                    candidates.append((x, y))
        return random.choice(candidates) if candidates else self._random_target(player_board)

    """
    Implements targeting strategy after finding a ship.
    """
    def _target_mode(self, player_board):
        x, y = self.last_hit
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        if self.direction:
            dx, dy = self.direction
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.board_size and 0 <= ny < self.board_size and 
                player_board[nx][ny] in ['', *list(SHIP_IMAGES.keys())]):
                return (nx, ny)

        valid_targets = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.board_size and 0 <= ny < self.board_size and 
                player_board[nx][ny] in ['', *list(SHIP_IMAGES.keys())]):
                valid_targets.append((nx, ny))
        
        return random.choice(valid_targets) if valid_targets else self._hunt_mode(player_board)

    """
    Selects a random untargeted cell when no better options exist.
    """
    def _random_target(self, player_board):
        untargeted = [(x, y) for x in range(self.board_size) 
                      for y in range(self.board_size) 
                      if player_board[x][y] in ['', *list(SHIP_IMAGES.keys())]]
        return random.choice(untargeted)

    """
    Updates AI targeting strategy based on hit/miss results.
    """
    def update_targeting(self, x, y, is_hit, player_board):
        if is_hit:
            self.hunt_mode = False
            self.last_hit = (x, y)
            self.ship_segments.append((x, y))
            
            ship_name = player_board[x][y]
            if ship_name in self.ship_hits:
                self.ship_hits[ship_name] += 1
                if self.ship_hits[ship_name] == dict(self.ships)[ship_name]:
                    self.ships_sunk.append(ship_name)
                    print(f"AI has sunk the {ship_name}!")
                    self._adjust_ai_after_sinking()

            if len(self.ship_segments) > 1:
                first = self.ship_segments[0]
                second = self.ship_segments[1]
                self.direction = (second[0] - first[0], second[1] - first[1])
        else:
            if not self.hunt_mode and len(self.ship_segments) > 1:
                if random.random() < 0.3:
                    self.hunt_mode = True
                    self.direction = None
                    self.ship_segments = []

    """
    Adjusts AI strategy after sinking a ship.
    """
    def _adjust_ai_after_sinking(self):
        for ship in self.ships_sunk:
            if ship in self.remaining_ships:
                self.remaining_ships.remove(ship)

class BattleshipBoard:
    """
    Manages the game board state and rendering.
    """
    def __init__(self, is_player=True):
        self.board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.ships_placed = []
        self.cell_display_time = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.ships = [
            {'name': 'carrier', 'length': 5},
            {'name': 'battleship', 'length': 4},
            {'name': 'cruiser', 'length': 3},
            {'name': 'submarine', 'length': 3},
            {'name': 'destroyer', 'length': 2}
        ]
        self.is_player = is_player
        self.place_ships()

    """
    Places ships randomly on the board.
    """
    def place_ships(self):
        for ship in self.ships:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction = random.choice(['H', 'V'])
                x = random.randint(0, BOARD_ROWS - 1)
                y = random.randint(0, BOARD_COLS - 1)

                if self.can_place_ship(ship, (x, y), direction):
                    self.place_ship(ship, (x, y), direction)
                    placed = True
                
                attempts += 1

            if not placed:
                raise ValueError(f"Could not place ship {ship['name']}")

    """
    Checks if a ship can be placed at the specified position.
    """
    def can_place_ship(self, ship, start, direction):
        x, y = start
        ship_length = ship['length']

        if direction == 'H':
            if y + ship_length > BOARD_COLS:
                return False
            return all(self.board[x][y + i] == '' for i in range(ship_length))
        else:
            if x + ship_length > BOARD_ROWS:
                return False
            return all(self.board[x + i][y] == '' for i in range(ship_length))

    """
    Places a ship on the board at the specified position.
    """
    def place_ship(self, ship, start, direction):
        x, y = start
        for i in range(ship['length']):
            if direction == 'H':
                self.board[x][y + i] = ship['name']
            else:
                self.board[x + i][y] = ship['name']
        
        self.ships_placed.append({
            'name': ship['name'], 
            'start': start, 
            'direction': direction, 
            'length': ship['length']
        })

    """
    Animates the sinking of a ship.
    """
    def animate_ship_sinking(self, ship_details):
        name, start, direction, length = ship_details.values()
        x, y = start

        for i in range(length):
            if direction == 'H':
                nx, ny = x, y + i
            else:
                nx, ny = x + i, y
            for _ in range(3):
                pygame.draw.rect(screen, COLORS['HIT_RED'], (nx * BOX_SIZE, ny * BOX_SIZE, BOX_SIZE, BOX_SIZE))
                pygame.display.flip()
                pygame.time.delay(150)
                pygame.draw.rect(screen, COLORS['BLACK'], (nx * BOX_SIZE, ny * BOX_SIZE, BOX_SIZE, BOX_SIZE))
                pygame.display.flip()
                pygame.time.delay(150)

    """
    Renders the game board.
    """
    def draw(self, x_offset):
        global message_text, message_color, message_start_time

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                cell_x = x_offset + col * BOX_SIZE
                cell_y = (SCREEN_HEIGHT - (BOARD_ROWS * BOX_SIZE)) // 2 + row * BOX_SIZE
                cell_value = self.board[row][col]

                if cell_value == 'H':
                    pygame.draw.rect(screen, COLORS['HIT_RED'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                elif cell_value == 'M':
                    pygame.draw.rect(screen, COLORS['MISS_ORANGE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                else:
                    pygame.draw.rect(screen, COLORS['OCEAN_BLUE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))

                pygame.draw.rect(screen, COLORS['GRID_LINE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE), 2)

        if message_text and pygame.time.get_ticks() - message_start_time < text_duration:
            draw_text_on_screen(message_text, message_color, (SCREEN_WIDTH // 2, 50))
        else:
            message_text = None

        if self.is_player:
            for ship in self.ships_placed:
                name = ship['name']
                x, y = ship['start']
                direction = ship['direction']
                length = ship['length']

                ship_image = SHIP_IMAGES[name].copy()
                if direction == 'H':
                    ship_image = pygame.transform.scale(ship_image, (length * BOX_SIZE, BOX_SIZE))
                else:
                    ship_image = pygame.transform.rotate(ship_image, 90)
                    ship_image = pygame.transform.scale(ship_image, (BOX_SIZE, length * BOX_SIZE))

                ship_x = x_offset + y * BOX_SIZE
                ship_y = (SCREEN_HEIGHT - (BOARD_ROWS * BOX_SIZE)) // 2 + x * BOX_SIZE
                screen.blit(ship_image, (ship_x, ship_y))

class BattleshipGame:
    """
    Main game class that manages game flow and state.
    """
    def __init__(self):
        self.player_board = BattleshipBoard(is_player=True)
        self.ai_board = BattleshipBoard(is_player=False)
        self.smart_ai = SmartAI(BOARD_ROWS)
        self.player_turn = True
        self.game_over = False
        self.turn_count = 0

    """
    Handles player clicks on the game board.
    """
    def handle_click(self, mouse_pos):
        global message_text, message_color, message_start_time

        x, y = mouse_pos
        ai_board_x_offset = CENTER_OFFSET_X + BOARD_COLS * BOX_SIZE + BOARD_SPACING

        if ai_board_x_offset <= x < ai_board_x_offset + BOARD_COLS * BOX_SIZE:
            col = (x - ai_board_x_offset) // BOX_SIZE
            row = (y - (SCREEN_HEIGHT - (BOARD_ROWS * BOX_SIZE)) // 2) // BOX_SIZE

            if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
                if self.ai_board.board[row][col] in SHIP_IMAGES:
                    self.ai_board.board[row][col] = 'H'
                    message_text = "Hit!"
                    message_color = COLORS['HIT_RED']
                    print(f"Player hit at {row}, {col}")
                    self.player_turn = True
                elif self.ai_board.board[row][col] == '':
                    self.ai_board.board[row][col] = 'M'
                    message_text = "Miss!"
                    message_color = COLORS['MISS_ORANGE']
                    print(f"Player missed at {row}, {col}")
                    self.player_turn = False

                message_start_time = pygame.time.get_ticks()

    """
    Handles AI turn logic and actions.
    """
    def ai_turn(self):
        pygame.time.delay(1000)
        global message_text, message_color, message_start_time
        
        row, col = self.smart_ai.choose_target(self.player_board.board)

        if self.player_board.board[row][col] in SHIP_IMAGES:
            self.player_board.board[row][col] = 'H'
            print(f"AI hit at {row}, {col}")
            self.smart_ai.update_targeting(row, col, True, self.player_board.board)
            self.player_turn = False
        else:
            self.player_board.board[row][col] = 'M'
            print(f"AI missed at {row}, {col}")
            self.smart_ai.update_targeting(row, col, False, self.player_board.board)
            self.player_turn = True

        message_start_time = pygame.time.get_ticks()
        self.turn_count += 1

    """
    Displays game over message with fade-in animation.
    """
    def display_game_over(self, message):
        font = pygame.font.SysFont(None, 72)
        text = font.render(message, True, COLORS['WHITE'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        for alpha in range(0, 256, 5):
            screen.fill(COLORS['BACKGROUND_NAVY'])
            self.player_board.draw(CENTER_OFFSET_X)
            self.ai_board.draw(CENTER_OFFSET_X + BOARD_COLS * BOX_SIZE + BOARD_SPACING)
            text.set_alpha(alpha)
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(50)

        pygame.time.wait(2000)

    """
    Checks if either player has won the game.
    """
    def check_game_over(self):
        def are_ships_sunk(board):
            return all(all(cell not in SHIP_IMAGES for cell in row) for row in board.board)

        if are_ships_sunk(self.ai_board):
            print(f"Player Wins in {self.turn_count} turns!")
            self.game_over = True
            self.display_game_over("You Win!")
        elif are_ships_sunk(self.player_board):
            print(f"AI Wins in {self.turn_count} turns!")
            self.game_over = True
            self.display_game_over("AI Wins!")

    """
    Main game loop and logic handler.
    """
    def run(self):
        clock = pygame.time.Clock()
        start_page = StartPage()
        game_started = False

        while not game_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_page.check_for_start_click(pygame.mouse.get_pos()):
                        game_started = True

            start_page.draw(screen)
            clock.tick(30)

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and self.player_turn:
                    self.handle_click(pygame.mouse.get_pos())
                    self.check_game_over()

            if not self.player_turn:
                self.ai_turn()
                self.check_game_over()

            screen.fill(COLORS['BACKGROUND_NAVY'])
            self.draw_board_titles()
            self.player_board.draw(CENTER_OFFSET_X)
            self.ai_board.draw(CENTER_OFFSET_X + BOARD_COLS * BOX_SIZE + BOARD_SPACING)
            pygame.display.flip()
            clock.tick(30)

        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    """
    Draws the titles for both game boards.
    """
    def draw_board_titles(self):
        font = pygame.font.SysFont(None, 36)
        defensive_title = font.render("Defensive Board", True, COLORS['WHITE'])
        defensive_title_rect = defensive_title.get_rect(center=(SCREEN_WIDTH // 4, 30))
        screen.blit(defensive_title, defensive_title_rect)

        attacking_title = font.render("Attacking Board", True, COLORS['WHITE'])
        attacking_title_rect = attacking_title.get_rect(center=(SCREEN_WIDTH * 3 // 4, 30))
        screen.blit(attacking_title, attacking_title_rect)

"""
Main entry point of the game.
"""
def main():
    game = BattleshipGame()
    game.run()

if __name__ == "__main__":
    main()