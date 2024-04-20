import chess
import chess.engine
import chess.pgn
import chess.polyglot
import csv
import random

# Path to your Stockfish executable
STOCKFISH_PATH = 'C:/Users/ataka/Documents/schule/stockfish/stockfish-windows-x86-64-avx2.exe'
OPENING_BOOK_PATH = 'C:/Users/ataka/Documents/schule/Human.bin'

# Initiliaze the Chess Engine
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# Dictionary of some common openings
opening_dict = {
    'e2e4 e7e5 g1f3': 'Ruy López',
    'd2d4 d7d5 c2c4': 'Queen\'s Gambit',
    'e2e4 c7c5': 'Sicilian Defense',
    'c2c4': 'English Opening'
    # Add more openings as needed
}

def get_opening(moves):
    parsed_moves =  ' '.join(str(move) for move in moves[:3])   # Record first three moves
    # move_sequence = ' '.join([str(move) for move in moves[:3]])  # Consider the first three moves
    return opening_dict.get(parsed_moves, "Unknown")

def get_evaluation_score(board, engine):
    # Get the evaluation score from Stockfish
    info = engine.analyse(board, chess.engine.Limit(depth=18))
    
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
            print('source:', src_square, 'target:', target_square)
            return False
        elif src_square == king_square and (target_square == kingside_castle or target_square == queenside_castle):
            # Castled
            print('Castled')
            return True

    # King never moved
    print('King never moved')
    return False


       
          



# Function to play a single game
def play_game(engine, white_skill, black_skill):
    board = chess.Board()
    game = chess.pgn.Game()
    node = game
    move_count = 0  # Counter for moves
    moves = []
    eval_after_move_10 = None  # Initialize evaluation score after 10 moves
    
    # Apply skill level settings
    engine.configure({"Skill Level": white_skill})  # Set skill level for White

    # Load opening book
    with chess.polyglot.open_reader(OPENING_BOOK_PATH) as reader:
        while not board.is_game_over():
            if move_count % 2 == 0:  # White's move
                engine.configure({"Skill Level": white_skill})
            else:  # Black's move
                engine.configure({"Skill Level": black_skill})
            move = None
            if move_count < 7:  # Use opening book for first 10 moves only
                try:
                    entry = reader.choice(board)
                    move = entry.move
                    print(f"Using book move: {move}")  # Debug output
                except IndexError:
                    move = None
                    print("No book move available.")  # Debug output

            if not move:  # If no book move available or past 10 moves
                result = engine.play(board, chess.engine.Limit(time=0.0001))
                move = result.move
                #print(f"Using engine move: {move}")  # Debug output       

            board.push(move)
            moves.append(move)
            node = node.add_variation(move)
            move_count += 1
            if move_count == 10:
                eval_after_move_10 = get_evaluation_score(board, engine)

    game.headers["Result"] = board.result()
    return game, board, moves, white_skill, black_skill, eval_after_move_10

# Function to extract features from a game
def extract_features(game, board, moves, white_skill, black_skill, eval_after_move_10):
    game_info = {}
    game_info['result'] = board.result()
    game_info['total_moves'] = board.fullmove_number
    game_info['opening'] = game.headers.get("Opening", "Unknown")
    game_info['winner'] = 'draw' if board.is_game_over() and board.result() == '1/2-1/2' else 'white' if '1-0' in board.result() else 'black'
    #game_info['white_rating'] = random.randint(1000, 2000)
    #game_info['black_rating'] = random.randint(1000, 2000)
    game_info['white_skill'] = white_skill
    game_info['black_skill'] = black_skill
    game_info['first_three_moves'] = ' '.join(str(move) for move in moves)   # Record first three moves
    
    parsed_moves = ' '.join(str(move) for move in moves)
    # Check if white has castled
    game_info['white_castled'] = has_castled(parsed_moves, is_white=True)
    
    # Check if black has castled
    game_info['black_castled'] = has_castled(parsed_moves, is_white=False)
    
    game_info['eval_after_move_10'] = eval_after_move_10

    return game_info

# Main function to generate games and write to CSV
def main():
    with open('chess_games_dataset.csv', 'w', newline='') as file:
        fieldnames = ['result', 'total_moves', 'opening', 'winner', 'white_skill', 'black_skill', 'first_three_moves', 'white_castled', 'black_castled', 'eval_after_move_10']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for _ in range(5):  # Number of games to play
            game, board, moves, white_skill, black_skill, eval_after_move_10 = play_game(engine, 3, 6)
            features = extract_features(game, board, moves, white_skill, black_skill, eval_after_move_10)
            writer.writerow(features)

    engine.quit()

if __name__ == "__main__":
    main()
