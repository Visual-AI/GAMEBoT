from .board import Board


def rowcol2pos(row, col):
    if row % 2 == 0:
        col = (col - 1) // 2
    else:
        col = col // 2
    return row * 4 + col + 1


def pos2rowcol(pos):
    row = (pos - 1) // 4
    col = (pos - 1) % 4
    if row % 2 == 0:
        col = col * 2 + 1
    else:
        col = col * 2
    return row, col


class Game:

    def __init__(self):
        self.board = Board()
        self.moves = []
        self.consecutive_noncapture_move_limit = 20
        self.moves_since_last_capture = 0

    def move_with_rowcol(self, start_row, start_col, end_row, end_col):
        start_pos = rowcol2pos(start_row, start_col)
        end_pos = rowcol2pos(end_row, end_col)
        self.move([start_pos, end_pos])

        return self

    def move(self, move):
        if move not in self.get_possible_moves():
            raise ValueError('The provided move is not possible')

        self.board = self.board.create_new_board_from_move(move)
        self.moves.append(move)
        self.moves_since_last_capture = 0 if self.board.previous_move_was_capture else self.moves_since_last_capture + 1

        return self

    def move_limit_reached(self):
        return self.moves_since_last_capture >= self.consecutive_noncapture_move_limit

    def is_over(self):
        return self.move_limit_reached() or not self.get_possible_moves()

    def get_winner(self):
        if self.whose_turn() == 1 and not self.board.count_movable_player_pieces(1):
            return 2
        elif self.whose_turn() == 2 and not self.board.count_movable_player_pieces(2):
            return 1
        else:
            return 0

    def get_possible_moves(self):
        return self.board.get_possible_moves()

    def whose_turn(self):
        return self.board.player_turn

    def get_algorithm_move(self):
        """
        Analyzes the current board state and returns the best move based on strategic principles.
        Returns: tuple of (start_position, end_position)
        """
        possible_moves = self.get_possible_moves()
        if not possible_moves:
            return None

        # Get current board state
        board_matrix = self.board.print_board()
        current_player = self.whose_turn()
        king_row = 0 if current_player == 2 else 7  # Black aims for row 0, White for row 7

        # Helper function to evaluate center control
        def center_score(pos):
            row, col = pos2rowcol(pos)
            # Center squares (2,3,4,5 columns) are worth more
            return 3 if 2 <= col <= 5 else 1

        def analyze_move(move):
            start_pos, end_pos = move
            start_row, start_col = pos2rowcol(start_pos)
            end_row, end_col = pos2rowcol(end_pos)
            score = 0

            # 1. Center Control
            score += center_score(end_pos)

            # 2. King Potential
            if end_row == king_row:
                score += 10

            # 3. Avoid Worthless Die
            # Check if move puts piece in immediate danger without compensation
            # piece = self.board.searcher.get_piece_by_position(start_pos)
            # new_board = self.board.create_new_board_from_move(move)
            # if new_board.get_possible_capture_moves():
            #     capturing_piece = new_board.searcher.get_piece_by_position(end_pos)
            #     if capturing_piece and not new_board.get_possible_capture_moves():
            #         score -= 8

            # 4. King Row Protection
            if current_player == 1:  # White
                if start_row == 0 and (start_col == 1 or start_col == 5):
                    score -= 3
            else:  # Black
                if start_row == 7 and (start_col == 2 or start_col == 6):
                    score -= 3

            # 5. Formation Strength
            nearby_friendly = 0
            for dr in [-1, 1]:
                for dc in [-1, 1]:
                    check_row, check_col = end_row + dr, end_col + dc
                    if 0 <= check_row < 8 and 0 <= check_col < 8:
                        piece_at_pos = self.board.searcher.get_piece_by_position(rowcol2pos(check_row, check_col))
                        if piece_at_pos and piece_at_pos.player == current_player:
                            nearby_friendly += 1
            score += nearby_friendly * 2

            return score

        # Analyze all possible moves
        move_scores = {}
        king_moves = []
        vulnerable_moves = []
        sacrifice_moves = []

        for move in possible_moves:
            score = analyze_move(move)
            move_scores[move] = score

            # Check for king creation
            _, end_row = pos2rowcol(move[1])
            if end_row == king_row:
                king_moves.append(move)

            # Check for vulnerable positions
            new_board = self.board.create_new_board_from_move(move)
            if new_board.get_possible_capture_moves():
                vulnerable_moves.append(move)

            # Check for sacrifice opportunities (Two-for-One Shot)
            if len(new_board.get_possible_capture_moves()) >= 2:
                sacrifice_moves.append(move)

        # # Output intermediate thinking results
        print(
            f"[Intermediate Thinking Results 1: {', '.join(str(pos2rowcol(m[0])) + '->' + str(pos2rowcol(m[1])) for m in king_moves) if king_moves else 'None'}]")
        print(
            f"[Intermediate Thinking Results 2: {', '.join(str(pos2rowcol(m[0])) + '->' + str(pos2rowcol(m[1])) for m in vulnerable_moves) if vulnerable_moves else 'None'}]")
        print(
            f"[Intermediate Thinking Results 3: {', '.join(str(pos2rowcol(m[0])) + '->' + str(pos2rowcol(m[1])) for m in sacrifice_moves) if sacrifice_moves else 'None'}]")

        # Select best move
        best_move = max(move_scores.items(), key=lambda x: x[1])[0]
        return best_move
