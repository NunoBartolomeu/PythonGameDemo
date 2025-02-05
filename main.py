import pygame

from base_classes import Board, Player, Piece, TileType
from turn_logic import update_player_board, remove_ghost_pieces
from board_gen import BOARD_WIDTH, BOARD_HEIGHT, generate_game
from draw_config import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, BACKGROUND_COLOR, draw_board, selected_piece, draw_possible_moves, handle_click

def main():
    selected_piece = None

    pygame.init()
    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
    clock = pygame.time.Clock()
    
    board_state, players = generate_game(["Player 1", "Player 2"])
    current_view = board_state
    current_player = players[0]

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_board(screen, current_view, current_player)

        if selected_piece:
            draw_possible_moves(screen, current_view, selected_piece)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[1] // TILE_SIZE, event.pos[0] // TILE_SIZE
                selected_piece = handle_click(board_state, x, y, selected_piece)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    current_view = board_state  # Show full board state
                elif event.key == pygame.K_1:
                    current_view = players[0].board  # Show Player 1's board
                    current_player = players[0]
                elif event.key == pygame.K_2:
                    current_view = players[1].board  # Show Player 2's board
                    current_player = players[1]
                elif event.key == pygame.K_RETURN:
                    remove_ghost_pieces(board_state)
                    update_player_board(players[0], board_state)
                    update_player_board(players[1], board_state)

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()