import pdb, string
from random import choice


class Othello:
    def __init__(self):
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.board[3][3] = 1
        self.board[3][4] = -1
        self.board[4][3] = -1
        self.board[4][4] = 1
        self.current_player = 1

    def print_board(self, with_coords=True):
        # print()
        board_info = f"\n\nYou are the {['White', 'Black'][self.current_player == 1]} player. Choose the best move.  " + '\nThe current board is: \n'
        # print('The current board is: ')
        for i in range(8):
            for j in range(8):
                if with_coords:
                    cur = 'O'
                else:
                    cur = '_'
                if self.board[i][j] == 1:
                    cur = 'B'
                elif self.board[i][j] == -1:
                    cur = 'W'
                # print('({},{}):{}'.format(chr(ord('A')+i), j+1, cur), end=' ')
                if with_coords:
                    board_info += '({},{}):{} '.format(chr(ord('A') + j), i + 1, cur)
                else:
                    board_info += '{} '.format(cur)

            # print()
            board_info += '\n'
        # for i, row in enumerate(self.board):
        # print(f"{i} | {' '.join(['.' if x == 0 else 'B' if x == 1 else 'W' for x in row])}")
        #     print(' '.join(['.' if x == 0 else 'B' if x == 1 else 'W' for x in row]))
        # print("   ----------------")
        board_info += '\n'
        # print(board_info, end='')
        return board_info

    def have_valid_moves(self):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.find_flippable_pieces(row, col):
                    valid_moves.append((row, col))
        return valid_moves

    def move_with_hint(self):
        board_info = self.print_board()
        valid_moves = self.have_valid_moves()
        # valid_moves = self.find_flippable_pieces()
        board_info += 'Valid moves are '
        for move in valid_moves:
            board_info += '({},{}) '.format(chr(ord('A') + move[1]), move[0] + 1)
        board_info += '.\n'
        return board_info

    def force_move(self):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.find_flippable_pieces(row, col):
                    valid_moves.append((row, col))
        move = choice(valid_moves)
        return chr(ord('A') + move[1]), move[0] + 1

    def find_flippable_pieces(self, row, col):
        if self.board[row][col] != 0:
            return []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        flippable = []
        for dx, dy in directions:
            x, y = row + dx, col + dy
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == -self.current_player:
                temp = []
                while 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == -self.current_player:
                    temp.append((x, y))
                    x += dx
                    y += dy
                if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == self.current_player:
                    flippable.extend(temp)
        return flippable

    def is_valid_move(self, row, col):
        return len(self.find_flippable_pieces(row, col)) > 0

    def make_move(self, col, row):
        col = ord(col) - ord('A')
        row = int(row) - 1
        print(f'''Player {["White", "Black"][self.current_player == 1]} to move.''')
        self.print_board()
        flippable = self.find_flippable_pieces(row, col)
        # pdb.set_trace()
        if not flippable:
            return False

        self.board[row][col] = self.current_player
        for x, y in flippable:
            self.board[x][y] = self.current_player

        self.current_player *= -1
        return True

    def get_score(self):
        white_count = 0
        black_count = 0
        for row in self.board:
            for cell in row:
                if cell == 1:
                    black_count += 1
                elif cell == -1:
                    white_count += 1
        return black_count, white_count

    def get_algorithm_move(self):
        """
        Determines the best move based on strategic analysis of the current board state.
        Returns: tuple (column_letter, row_number) representing the chosen move
        """

        def evaluate_corner_control(row, col):
            corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
            if (row, col) in corners:
                return 100  # Highest priority for corner moves

            # Penalize moves adjacent to corners unless corner is already taken
            corner_adjacents = {
                (0, 0): [(0, 1), (1, 0), (1, 1)],
                (0, 7): [(0, 6), (1, 7), (1, 6)],
                (7, 0): [(6, 0), (7, 1), (6, 1)],
                (7, 7): [(6, 7), (7, 6), (6, 6)]
            }

            for corner, adjacents in corner_adjacents.items():
                if (row, col) in adjacents:
                    if self.board[corner[0]][corner[1]] == 0:  # Corner is empty
                        return -50  # Heavily penalize moves next to empty corners
                    else:
                        return 0  # Neutral if corner is already taken
            return 0

        def evaluate_edge_control(row, col):
            if row in [0, 7] or col in [0, 7]:
                return 30  # Good bonus for edge moves
            return 0

        def evaluate_piece_stability(row, col):
            score = 0
            # Check if the move would create stable positions
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in directions:
                x, y = row + dx, col + dy
                if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == self.current_player:
                    score += 2  # Bonus for connecting to own pieces
            return score

        def evaluate_frontier(row, col):
            score = 0
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            frontier_count = 0

            # Count potential new frontier pieces
            for dx, dy in directions:
                x, y = row + dx, col + dy
                if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == 0:
                    frontier_count += 1

            return -2 * frontier_count  # Penalize moves that create more frontier pieces

        def evaluate_wedge(row, col):
            if row not in [0, 7] and col not in [0, 7]:
                return 0  # Not an edge move

            # Check for wedge opportunities on edges
            if row == 0 or row == 7:
                # Check horizontally
                # Look left
                left_opponent = 0
                x = col - 1
                if x >= 0:
                    if self.board[row][x] == -self.current_player:
                        left_opponent += 1
                # Look right
                right_opponent = 0
                x = col + 1
                if x < 8:
                    if self.board[row][x] == -self.current_player:
                        right_opponent += 1

                if left_opponent > 0 and right_opponent > 0:
                    return 80  # High bonus for creating a wedge

            if col == 0 or col == 7:
                # Check vertically
                # Look up
                up_opponent = 0
                y = row - 1
                if y >= 0:
                    if self.board[y][col] == -self.current_player:
                        up_opponent += 1

                # Look down
                down_opponent = 0
                y = row + 1
                if y < 8:
                    if self.board[y][col] == -self.current_player:
                        down_opponent += 1

                if up_opponent > 0 and down_opponent > 0:
                    return 80  # High bonus for creating a wedge

            return 0

        def evaluate_mobility(row, col):
            # Temporarily make the move
            original_board = [row[:] for row in self.board]
            self.board[row][col] = self.current_player
            flippable = self.find_flippable_pieces(row, col)
            for x, y in flippable:
                self.board[x][y] = self.current_player

            # Count opponent's possible moves
            self.current_player *= -1
            opponent_moves = len(self.have_valid_moves())

            # Restore the board state
            self.board = original_board
            self.current_player *= -1

            return -2 * opponent_moves  # Penalize moves that give opponent more options

        # Get all valid moves
        valid_moves = self.have_valid_moves()
        if not valid_moves:
            return None

        # Evaluate each move
        best_score = float('-inf')
        best_move = None

        for row, col in valid_moves:
            score = 0
            score += evaluate_corner_control(row, col)
            score += evaluate_edge_control(row, col)
            score += evaluate_piece_stability(row, col)
            score += evaluate_frontier(row, col)
            score += evaluate_wedge(row, col)
            score += evaluate_mobility(row, col)

            if score > best_score:
                best_score = score
                best_move = (row, col)
        print(valid_moves)
        print(best_move)
        # Convert to game notation (e.g., 'A1')
        return (chr(ord('A') + best_move[1]), best_move[0] + 1)


if __name__ == '__main__':
    game = Othello()
    print(game.print_board())
    for _ in range(62):
        col, row = game.get_algorithm_move()
        game.make_move([0], col, row)
        print(game.print_board(with_coords=False))
