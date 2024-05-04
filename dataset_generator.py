import chess
import chess.engine
import chess.pgn
import chess.polyglot
import csv
import random
import os

# Path to your Stockfish executable
STOCKFISH_PATH = os.environ.get('STOCKFISH_PATH')
OPENING_BOOK_PATH = os.environ.get('OPENING_BOOK_PATH')

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

def track_piece_counts(board):
    """Tracks the counts of knights and bishops on each side."""
    white_knights = len(board.pieces(chess.KNIGHT, chess.WHITE))
    white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
    black_knights = len(board.pieces(chess.KNIGHT, chess.BLACK))
    black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))
    return {
        "white_knights": white_knights,
        "white_bishops": white_bishops,
        "black_knights": black_knights,
        "black_bishops": black_bishops
    }
import chess

def control_of_center(moves):
    board = chess.Board()
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    white_control_scores = []
    black_control_scores = []
    
    for move in moves:
        board.push(move)
        white_control = 0
        black_control = 0
        for square in center_squares:
            if board.is_attacked_by(chess.WHITE, square):
                white_control += 1
            if board.is_attacked_by(chess.BLACK, square):
                black_control += 1
        white_control_scores.append(white_control)
        black_control_scores.append(black_control)

    # Calculate average control
    avg_white_control = sum(white_control_scores) / len(white_control_scores) if white_control_scores else 0
    avg_black_control = sum(black_control_scores) / len(black_control_scores) if black_control_scores else 0

    return avg_white_control, avg_black_control


def calculate_piece_activity(moves):
    board = chess.Board()
    white_control_counts = []
    black_control_counts = []
    
    for move in moves:
        board.push(move)
        white_control = 0
        black_control = 0
        
        # Loop over all squares and check if they are attacked by white or black
        for square in chess.SQUARES:
            if board.is_attacked_by(chess.WHITE, square):
                white_control += 1
            if board.is_attacked_by(chess.BLACK, square):
                black_control += 1
                
        white_control_counts.append(white_control)
        black_control_counts.append(black_control)

    # Calculate average control for white and black
    avg_white_control = sum(white_control_counts) / len(white_control_counts) if white_control_counts else 0
    avg_black_control = sum(black_control_counts) / len(black_control_counts) if black_control_counts else 0

    return avg_white_control, avg_black_control

def average_piece_evaluation(moves, evaluation_interval):
    """Evaluates the average number of knights and bishops every 'evaluation_interval' moves."""
    board = chess.Board()
    counts = []
    for i, move in enumerate(moves):
        board.push(move)
        if (i + 1) % evaluation_interval == 0 or (i + 1) == len(moves):
            counts.append(track_piece_counts(board))

    # Initialize sums
    sum_counts = {
        "white_knights": 0,
        "white_bishops": 0,
        "black_knights": 0,
        "black_bishops": 0
    }

    # Sum all counts
    for count in counts:
        for key in sum_counts:
            sum_counts[key] += count[key]

    # Calculate averages
    num_evaluations = len(counts)
    if num_evaluations > 0:
        avg_counts = {key: value / num_evaluations for key, value in sum_counts.items()}
    else:
        avg_counts = sum_counts  # Avoid division by zero; only possible if moves are fewer than interval and none evaluated

        # Sum all counts
    for count in counts:
        for key in sum_counts:
            sum_counts[key] += count[key]

    # Calculate averages and ratios
    num_evaluations = len(counts)
    if num_evaluations > 0:
        avg_counts = {key: value / num_evaluations for key, value in sum_counts.items()}
        white_knight_to_bishop_ratio = avg_counts["white_knights"] / avg_counts["white_bishops"] if avg_counts["white_bishops"] != 0 else float('inf')
        black_knight_to_bishop_ratio = avg_counts["black_knights"] / avg_counts["black_bishops"] if avg_counts["black_bishops"] != 0 else float('inf')
    else:
        # Avoid division by zero; only possible if moves are fewer than interval and none evaluated
        white_knight_to_bishop_ratio = float('inf')
        black_knight_to_bishop_ratio = float('inf')

    return white_knight_to_bishop_ratio, black_knight_to_bishop_ratio


def get_evaluation_score(board, engine, depth):
    # Get the evaluation score from Stockfish
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    try:
        score = info["score"].white().score() / 100  # Normalize score for white's perspective
        print(score)
    except Exception as e:
        # Handle any exceptions that occur during calculation
        score=0
        print(f"Error occurred: {e}")
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


def opposite_side_castling(moves):
    # Initialize castling flags for both colors
    white_kingside = False
    white_queenside = False
    black_kingside = False
    black_queenside = False

    # Split moves into a list for analysis
    move_list = moves.split()

    # Check for white and black castling in the move list
    for move in move_list:
        src_square = move[:2]
        target_square = move[2:4]

        # Check for White's castling
        if src_square == 'e1':
            if target_square == 'g1':
                white_kingside = True
            elif target_square == 'c1':
                white_queenside = True

        # Check for Black's castling
        if src_square == 'e8':
            if target_square == 'g8':
                black_kingside = True
            elif target_square == 'c8':
                black_queenside = True

    # Determine if opposite side castling occurred
    if (white_kingside and black_queenside) or (white_queenside and black_kingside):
        return True  # Opposite side castling occurred
    else:
        return False  # No opposite side castling


def play_game(engine, white_skill, black_skill):
    board = chess.Board()
    moves = []
    eval_after_move_15= None
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
        
                

            if len(moves) == 15:
                eval_after_move_15 = get_evaluation_score(board, engine, 12)

    game = chess.pgn.Game.from_board(board)
    game.headers["Result"] = board.result()
    return game, board, moves, eval_after_move_15 

# Function to extract features from a game
def extract_features(game, board, moves, white_skill, black_skill, eval_after_move_15):
    game_info = {}
    game_info['result'] = board.result()
    game_info['total_moves'] = board.fullmove_number
    game_info['opening'] = get_opening_from_tree(moves, openings_tree)
    game_info['winner'] = 'draw' if board.is_game_over() and board.result() == '1/2-1/2' else 'white' if '1-0' in board.result() else 'black'
    #game_info['white_rating'] = random.randint(1000, 2000)
    #game_info['black_rating'] = random.randint(1000, 2000)
    game_info['white_skill'] = white_skill
    game_info['black_skill']= black_skill
    #game_info['moves'] = ' '.join(str(move) for move in moves)   # Record first three moves
    
    parsed_moves = ' '.join(str(move) for move in moves)
    # Check if white has castled
    game_info['white_castled'] = has_castled(parsed_moves, is_white=True)
    game_info['w_knight_to_bishop'], game_info['b_knight_to_bishop'] = average_piece_evaluation(moves, evaluation_interval=3)
    game_info['w_center_control'], game_info['b_center_control'] = control_of_center(moves)
    # Check if black has castled:
    game_info['black_castled'] = has_castled(parsed_moves, is_white=False)
    game_info['opposite_side_castle'] = opposite_side_castling(parsed_moves)
    game_info['white_piece_activity'], game_info['black_piece_activity'] = calculate_piece_activity(moves)
    game_info['white_sacrifices'], game_info['black_sacrifices'] = count_sacrifices(board)
    game_info['eval_after_move_15'] = eval_after_move_15
    

    return game_info

# Main function to generate games and write to CSV
def main():
    with open('dataset.csv', 'w', newline='') as file:
        fieldnames = ['result', 'total_moves', 'opening', 'winner', 'white_skill', 'black_skill', 'white_castled', 'black_castled', 'opposite_side_castle', 'white_sacrifices', 'black_sacrifices', 'w_knight_to_bishop', 'b_knight_to_bishop', 'w_center_control', 'b_center_control', 'white_piece_activity', 'black_piece_activity', 'eval_after_move_15']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    
        for _ in range(2500):  # Number of games to play
           
            white_skill = random.randint(5,20)
            #black_skill = random.randint(5,20)
            black_skill = white_skill
            #white_skill = 12
            #black_skill = 12
            game, board, moves, eval_after_move_15 = play_game(engine, white_skill, black_skill)
            features = extract_features(game, board, moves, white_skill, black_skill, eval_after_move_15)
            writer.writerow(features)

    engine.quit()

if __name__ == "__main__":
    main()
''' 
Features:

'''
