import chess
import chess.engine
import chess.pgn
import chess.polyglot
import csv
import random

# Path to your Stockfish executable
STOCKFISH_PATH = 'C:/Users/ataka/Documents/schule/stockfish/stockfish-windows-x86-64-avx2.exe'
OPENING_BOOK_PATH = 'C:/Users/ataka/Documents/schule/gm2001.bin'

# Initiliaze the Chess Engine
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

openings_tree = {
    'e2e4': {
        'name': 'King\' s Pawn Opening',
        'e7e5': {
            'g1f3': 'Ruy López',
            'f1c4': 'Italian Game',
            'f2f4': 'King\'s Gambit',
            'b1c3': 'Vienna Game',
        },
        'c7c5': {
            'name': 'Sicilian Defense',
            'g1e2': 'Closed Sicilian',
            'g1f3': 'Open Sicilian',
            'f1b5': 'Rossolimo Sicilian',
        },
        'e7e6': {
            'd2d4': 'French Defense',
            'b1c3': 'French, Two Knights Variation',
        },
        'c7c6': {
            'd2d4': 'Caro-Kann Defense',
        },
        'g8f6': {
            'e4e5': 'Alekhine\'s Defense',
        }
    },
    'd2d4': {
        'name':'Queen\'s Pawn Opening',
        'd7d5': {
            'c2c4': 'Queen\'s Gambit',
            'b1c3': 'Veresov Attack',
            'g1f3': 'Queen\'s Pawn Game',
        },
        'g8f6': {
            'c2c4': 'Indian Game',
            'b1c3': 'Trompowsky Attack',
            'g1f3': 'Indian Defense',
        },
        'e7e6': {
            'c2c4': 'Nimzo-Indian Defense',
            'g1f3': 'Queen\'s Indian Defense',
        }
    },
    'c2c4': {
        'name': 'English Opening',
        'e7e5': 'English Opening',
        'g8f6': {
            'b1c3': 'English, Mikenas-Carls Variation',
            'g2g3': 'English, King\'s Indian Variation',
        },
        'e7e6': 'English, Agincourt Defense',
        'c7c5': 'English, Symmetrical Variation',
    },
    'g1f3': {
        'name':'Reti Opening',
        'd7d5': 'Reti Opening',
        'g8f6': {
            'c2c4': 'Reti, King\'s Indian Attack',
            'b2b3': 'Nimzo-Larsen Attack',
        }
    },
    'b1c3': {
        'name': 'Dunst Opening',
        'd7d5': 'Dunst Opening',
        'g8f6': 'Nimzowitsch Defense',
    },
    'b2b3':{
        'name': 'Larsen\'s Opening'
    },
    'f2f4':{
        'name': 'Bird\'s Opening'
    },
    'g2g3':{
        'name': 'Benko\'s Opening'
    },
}


def get_opening(moves):
    for length in range(1, min(3, len(moves)) + 1):  # Check up to the first three moves or fewer if not available
        parsed_moves = ' '.join(str(move) for move in moves[:length])
        if parsed_moves in opening_dict:
            return opening_dict[parsed_moves]
    return "Unknown"

def get_opening_from_tree(moves, opening_tree):
    current_dict = opening_tree
    last_known_opening = "Unknown"  # Track the last known opening

    for move in moves:
        move_uci = move.uci()  # Ensure the move is in UCI format
        if move_uci in current_dict:
            next_step = current_dict[move_uci]
            if isinstance(next_step, dict):
                current_dict = next_step
                # Update last known opening if it's a named opening
                if 'name' in current_dict:
                    last_known_opening = current_dict['name']
            else:
                # Directly found the opening name
                return next_step
        else:
            # No further specific move match, return last known opening if any
            break
    
    return last_known_opening


def piece_value(piece):
    """Returns the value of the piece."""
    if piece is None:
        return 0
    piece_type = chess.PIECE_TYPES.index(piece.piece_type) + 1
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    return values.get(piece_type, 0)

def count_sacrifices(board):
    """Counts the sacrifices made by white and black."""
    white_sacrifices = 0
    black_sacrifices = 0
    move_stack = list(board.move_stack)  # Get all moves made in the game so far
    board.reset()  # Reset the board to replay the moves
    
    for move in move_stack:
        if board.is_capture(move):
            moving_piece = board.piece_at(move.from_square)
            captured_piece = board.piece_at(move.to_square)
            if moving_piece and captured_piece:
                moving_value = piece_value(moving_piece)
                captured_value = piece_value(captured_piece)
                if moving_value > captured_value:
                    if moving_piece.color == chess.WHITE:
                        #white_sacrifices += 1
                        white_sacrifices += moving_value - captured_value
                    else:
                        #black_sacrifices += 1
                        black_sacrifices += moving_value - captured_value
        board.push(move)  # Make the move on the board
    
    return white_sacrifices, black_sacrifices

def calculate_control(board):
    """Calculate control of central and key squares by each player."""
    central_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    white_control = 0
    black_control = 0

    for square in central_squares:
        white_control += len(board.attackers(chess.WHITE, square))
        black_control += len(board.attackers(chess.BLACK, square))

    return white_control, black_control

def average_positional_imbalance(moves):
    """Calculate average imbalance over the course of a game."""
    board = chess.Board()
    imbalances = []
    total_imbalance = 0
    num_evaluated_positions = 0

    for move in moves:
        board.push(move)
        white_control, black_control = calculate_control(board)
        imbalance = abs(white_control - black_control)
        imbalances.append(imbalance)
        total_imbalance += imbalance
        num_evaluated_positions += 1

    if num_evaluated_positions > 0:
        average_imbalance = total_imbalance / num_evaluated_positions
    else:
        average_imbalance = 0  # In case of no moves

    return average_imbalance

def get_evaluation_score(board, engine, depth):
    # Get the evaluation score from Stockfish
    info = engine.analyse(board, chess.engine.Limit(depth= depth))
    
    score = info["score"].white().score()/100  # Normalize score for white's perspective
    return score

def has_castled(moves, is_white):
    king_square = 'e1' if is_white else 'e8'
    kingside_castle = 'g1' if is_white else 'g8'
    queenside_castle = 'c1' if is_white else 'c8'

    move_list = moves.split()
    for move in move_list:
        # Split the move into its source and target squares
        src_square = move[:2]
        target_square = move[2:4]
                                         
        if src_square == king_square and target_square != kingside_castle and target_square != queenside_castle:
            # King moved but didn't castle
           # print('source:', src_square, 'target:', target_square)
            return False
        elif src_square == king_square and (target_square == kingside_castle or target_square == queenside_castle):
            # Castled
            print('Castled')
            return True

    # King never moved
    print('King never moved')
    return False


def play_game(engine, white_skill, black_skill):
    board = chess.Board()
    moves = []
    eval_after_move_10 = None
    eval_after_move_20 = None
    # Apply skill level settings
    engine.configure({"Skill Level": white_skill})  # Set skill level for White


    with chess.polyglot.open_reader(OPENING_BOOK_PATH) as reader:
        while not board.is_game_over():

            if len(moves) % 2 == 0:  # White's move
                engine.configure({"Skill Level": white_skill})
            else:  # Black's move
                engine.configure({"Skill Level": black_skill})
            move = None

            if len(moves) < 7: # Length of opening
                try:
                    entry = reader.choice(board)
                    move = entry.move
                    print(f"Entry: {entry}, Using book move: {move.uci()}")  # Debug output
                except IndexError:
                    move = engine.play(board, chess.engine.Limit(time=0.0001)).move
                    print("No book move available, using engine move.")  # No book move available
            else:
                move = engine.play(board, chess.engine.Limit(time=0.0001)).move
                print(f"Using engine move: {move.uci()}")  # Debug output

            board.push(move)
            moves.append(move)
            if len(moves) == 10:
                eval_after_move_10 = get_evaluation_score(board, engine, 16)
            elif len(moves) == 20:
                eval_after_move_20 = get_evaluation_score(board, engine, 16)


    game = chess.pgn.Game.from_board(board)
    game.headers["Result"] = board.result()
    return game, board, moves, eval_after_move_10, eval_after_move_20

# Function to extract features from a game
def extract_features(game, board, moves, white_skill, black_skill, eval_after_move_10, eval_after_move_20):
    game_info = {}
    game_info['result'] = board.result()
    game_info['total_moves'] = board.fullmove_number
    game_info['opening'] = get_opening_from_tree(moves, openings_tree)
    game_info['winner'] = 'draw' if board.is_game_over() and board.result() == '1/2-1/2' else 'white' if '1-0' in board.result() else 'black'
    #game_info['white_rating'] = random.randint(1000, 2000)
    #game_info['black_rating'] = random.randint(1000, 2000)
    game_info['white_skill'] = white_skill
    game_info['black_skill'] = black_skill
    game_info['first_three_moves'] = ' '.join(str(move) for move in moves)   # Record first three moves
    
    parsed_moves = ' '.join(str(move) for move in moves)
    # Check if white has castled
    game_info['white_castled'] = has_castled(parsed_moves, is_white=True)
    game_info['overall_imbalance'] = average_positional_imbalance(moves)
   
    # Check if black has castled
    game_info['black_castled'] = has_castled(parsed_moves, is_white=False)
    game_info['white_sacrifices'], game_info['black_sacrifices'] = count_sacrifices(board)
    game_info['eval_after_move_10'] = eval_after_move_10
    game_info['eval_after_move_20'] = eval_after_move_20

    return game_info

# Main function to generate games and write to CSV
def main():
    with open('chess_games_dataset.csv', 'w', newline='') as file:
        fieldnames = ['result', 'total_moves', 'opening', 'winner', 'white_skill', 'black_skill', 'first_three_moves', 'white_castled', 'black_castled', 'white_sacrifices', 'black_sacrifices', 'overall_imbalance', 'eval_after_move_10', 'eval_after_move_20']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for _ in range(15):  # Number of games to play
           
            #white_skill = random.randint(5,20)
            #black_skill = random.randint(5,20)
            white_skill = 12
            black_skill = 12
            game, board, moves, eval_after_move_10, eval_after_move_20 = play_game(engine, white_skill, black_skill)
            features = extract_features(game, board, moves, white_skill, black_skill, eval_after_move_10, eval_after_move_20)
            writer.writerow(features)

    engine.quit()

if __name__ == "__main__":
    main()
