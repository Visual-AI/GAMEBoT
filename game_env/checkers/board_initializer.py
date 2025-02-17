from .piece import Piece

class BoardInitializer:

	def __init__(self, board):
		self.board = board

	def initialize(self):
		self.build_position_layout()
		self.set_starting_pieces()

	def build_position_layout(self):
		self.board.position_layout = {}
		position = 1

		for row in range(self.board.height):
			self.board.position_layout[row] = {}

			for column in range(self.board.width):
				self.board.position_layout[row][column] = position
				position += 1

	def set_starting_pieces(self):
		pieces = []
		starting_piece_count = self.board.width * self.board.rows_per_user_with_pieces
		player_starting_positions = {
			1: list(range(1, starting_piece_count + 1)),
			2: list(range(self.board.position_count - starting_piece_count + 1, self.board.position_count + 1))
		}

		for key, row in self.board.position_layout.items():
			for key, position in row.items():
				player_number = 1 if position in player_starting_positions[1] else 2 if position in player_starting_positions[2] else None

				if (player_number):
					pieces.append(self.create_piece(player_number, position))

		self.board.pieces = pieces

	def create_piece(self, player_number, position):
		piece = Piece()
		piece.player = player_number
		piece.position = position
		piece.board = self.board

		return piece