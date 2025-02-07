import pygame

pygame.init()

# Constants
WIDTH, HEIGHT = 400, 300
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Menu")
font = pygame.font.Font(None, 36)

# Initial values
name = ""
selected_color = 0
input_active = False

running = True
while running:
    screen.fill(WHITE)
    
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
            else:
                if event.key == pygame.K_LEFT:
                    selected_color = (selected_color - 1) % len(COLORS)
                elif event.key == pygame.K_RIGHT:
                    selected_color = (selected_color + 1) % len(COLORS)
                elif event.key == pygame.K_RETURN:
                    running = False  # Confirm selection
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if name_box.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False
    
    # Render UI
    name_box = pygame.Rect(100, 50, 200, 40)
    pygame.draw.rect(screen, BLACK, name_box, 2)
    name_text = font.render(name if name else "Enter Name", True, BLACK)
    screen.blit(name_text, (name_box.x + 10, name_box.y + 10))
    
    pygame.draw.rect(screen, COLORS[selected_color], (150, 120, 100, 40))
    color_text = font.render("<   Color   >", True, BLACK)
    screen.blit(color_text, (140, 170))
    
    confirm_text1 = font.render("Press ENTER", True, BLACK)
    confirm_text2 = font.render("to confirm", True, BLACK)
    screen.blit(confirm_text1, (140, 220))
    screen.blit(confirm_text2, (140, 250))
    
    pygame.display.flip()

pygame.quit()
