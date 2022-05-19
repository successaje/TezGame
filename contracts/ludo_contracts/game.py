from collections import namedtuple
from multiprocessing.spawn import spawn_main
import smartpy as sp
import random
from painter import PainterBoard

sp.Pawn = namedtuple("Pawn", "index colour id")

class Player(sp.Contract):

    def __init__(self, colour, name, choose_pawn_delegate):
        self.init(
            colour = colour,
            choose_pawn_delegate = choose_pawn_delegate,
            name = name
        )
        sp.if self.data.name is None and self.data.choose_pawn_delegate is None:
            self.data.name = "Computer"
        self.data.finished = False

        self.data.pawns = [sp.Pawn(i, colour, colour[0].upper() + str(i))
                            sp.for i in range(1, 5)]
    @sp.offchain_view
    def __str__(self):
        sp.result("{}({})".format(self.data.name, self.data.colour))

    @sp.entry_point
    def choose_pawn(self, pawns):
        sp.if len(pawns) == 1:
            sp.index = 0
        sp.elif len(pawns) > 1:
            sp.if self.data.choose_pawn_delegate is None:
                sp.index = random.randint(0, len(pawns) -1)
            sp.else:
                sp.index = self.data.choose_pawn_delegate()
        sp.result(sp.index)

class Board(sp.Contract):
    sp.BOARD_SIZE = 56
    sp.BOARD_COLOUR_SIZE = 7

    sp.COLOUR_ORDER = ['yellow', 'blue'. 'red', 'green']

    sp.COLOUR_DISTANCE = 14

    def __init__(self):
        sp.Board.COLOUR_START = {
            colour: 1 + index * sp.BoardCOLOUT_DISTANCE
             sp.for index, colour in enumerate(sp.Board.COLOUR_ORDER)
        }
        sp.Board.COLOUR_END = {
            colour : index * sp.Board.COLOUR_DISTANCE
            sp.for index, colour in enumerate(sp.Board.COLOUR_ORDER)}
        sp.Board.COLOUR_END['yellow'] = sp.Board.BOARD_SIZE


        self.pawns_possiotion = {}
        self.painter = PainterBoard()

        self.board_pool_position = (0, 0)

    @sp.entry_point
    def set_pawn(self, pawn, position):
        self.data.pawns_possiotion[pawn] = position

    @sp.entry_point
    def put_pawn_on_board_pool(self, pawn):
        self.set_pawn(pawn, self.board_pool_position)

    @sp.entry_point
    def is_pawn_on_board_pool(self, pawn):
        sp.result(self.data.pawns_possiotion[pawn] == self.data.board_pool_position)

    @sp.entry_point
    def put_pawn_on_starting_square(self, pawn):
        start = sp.Board.COLOUR_START[pawn.colour.lower()]
        position = (sp.start, 0)
        self.set_pawn(pawn, position)

    @sp.entry_point
    def can_pawn_move(self, pawn, rolled_value):
        '''check if pawn can outside board colour size'''
        sp.common_poss,sp. private_poss = self.data.pawns_possiotion[pawn]
        sp.if private_poss + rolled_value > self.BOARD_COLOUR_SIZE:
            sp.result(False) 
        sp.result(True)

    @sp.entry_point    
    def move_pawn(self, pawn, rolled_value):
        '''change pawn position, check
        if pawn reach his color square
        '''
        sp.common_poss, sp.private_poss = self.data.pawns_possiotion[pawn]
        sp.end = self.data.COLOUR_END[pawn.colour.lower()]
        sp.if (sp.private_poss > 0):
            # pawn is already reached own final squares
            sp.private_poss += rolled_value
        sp.elif (sp.common_poss <= end and sp.common_poss + sp.rolled_value > end):
            # pawn is entering in own squares
            private_poss += rolled_value - (end - common_poss)
            common_poss = end
        sp.else:
            # pawn will be still in common square
            common_poss += rolled_value
            sp.if common_poss > self.data.BOARD_SIZE:
                sp.common_poss = sp.common_poss - self.data.BOARD_SIZE
        sp.position = sp.common_poss, sp.private_poss
        self.set_pawn(pawn, position)

    @sp.entry_point
    def does_pawn_reach_end(self, pawn):
        '''if pawn must leave game'''
        sp.common_poss, sp.private_poss = self.data.pawns_possiotion[pawn]
        if sp.private_poss == self.data.BOARD_COLOUR_SIZE:
            sp.result(True)
        sp.result(False)

    @sp.entry_point
    def get_pawns_on_same_postion(self, pawn):
        '''return list of pawns on same position'''
        sp.position = self.data.pawns_possiotion[pawn]
        sp.result[curr_pawn for curr_pawn, curr_postion in
                self.data.pawns_possiotion.items()
                if sp.position == curr_postion]

    @sp.offchain_view(pure = True)
    def paint_board(self):
        '''painter object expect dict of
        key - occupied positions and
        value - list of pawns on that position
        '''
        sp.positions = {}
        sp.for sp.pawn, sp.position in self.data.pawns_possiotion.items():
            sp.common, sp.private = sp.position
            sp.if not sp.private == Board.data.BOARD_COLOUR_SIZE:
                positions.setdefault(sp.position, []).append(pawn)
        sp.result(self.data.painter.paint(positions))


class Die(sp.Contract):

    MIN = 1
    MAX = 6

    @sp.onchain_view
    @staticmethod
    def throw():
        sp.result(random.randint(Die.MIN, Die.MAX))



class Game(sp.Contract):
    '''Knows the rules of the game.
    Knows for example what to do when 
    one pawn reach another
    or pawn reach end or 
    player roll six and so on
    '''

    def __init__(self):
        self.players = deque()
        self.standing = []
        self.board = Board()
        # is game finished
        self.finished = False
        # last rolled value from die (dice)
        self.rolled_value = None
        # player who last rolled die
        self.curr_player = None
        # curr_player's possible pawn to move
        self.allowed_pawns = []
        # curr_player's chosen pawn to move
        self.picked_pawn = None
        # chosen index from allowed pawn 
        self.index = None
        # jog pawn if any 
        self.jog_pawns = []

    @sp.entry_point
    def add_palyer(self, player):
        self.players.append(player)
        sp.for pawn in player.pawns:
            self.data.board.put_pawn_on_board_pool(pawn)
    
    @sp.offchain_view()
    @spawn_main
    def get_available_colours(self):
        '''if has available colour on boards'''
        sp.used = [player.colour sp.for player in self.data.players]
        available = set(self.data.board.COLOUR_ORDER) - set(used)
        sp.result(sorted(available))

    @sp.entry_point
    def _get_next_turn(self):
        '''Get next player's turn.
        It is underscore because if called 
        outside the class will break order
        '''
        sp.if not self.data.rolled_value == Die.MAX:
            self.data.players.rotate(-1)
        sp.result(self.data.players[0])

    @sp.entry_point
    def get_pawn_from_board_pool(self, player):
        '''when pawn must start'''
        sp.for pawn in player.pawns:
            sp.if self.data.board.is_pawn_on_board_pool(pawn):
                sp.result(pawn)

    @sp.entry_point
    def get_allowed_pawns_to_move(self, player, rolled_value):
        ''' return all pawns of a player which rolled value
        from die allowed to move the pawn
        '''
        sp.allowed_pawns = []
        sp.if rolled_value == Die.MAX:
            pawn = self.data.get_pawn_from_board_pool(player)
            sp.if pawn:
                sp.allowed_pawns.append(pawn)
        sp.for pawn in player.pawns:
            sp.if not self.data.board.is_pawn_on_board_pool(pawn) and\
                    self.data.board.can_pawn_move(pawn, rolled_value):
                sp.allowed_pawns.append(pawn)
        sp.result(sorted(sp.allowed_pawns, key=lambda pawn: pawn.index))

    @sp.offchain_view(pure=True)
    def get_board_pic(self):
        sp.result(self.data.board.paint_board())

    @sp.entry_point
    def _jog_foreign_pawn(self, pawn):
        sp.pawns = self.data.board.get_pawns_on_same_postion(pawn)
        sp.for p in sp.pawns:
            sp.if p.colour != pawn.colour:
                self.data.board.put_pawn_on_board_pool(p)
                self.data.jog_pawns.append(p)

    @sp.entry_point
    def _make_move(self, player, pawn):
        '''tell the board to move pawn.
        After move ask board if pawn reach end or
        jog others pawn. Check if pawn and player finished.
        '''
        sp.if self.data.rolled_value == Die.MAX and\
                self.data.board.is_pawn_on_board_pool(pawn):
            self.data.board.put_pawn_on_starting_square(pawn)
            self.data._jog_foreign_pawn(pawn)
            sp.result(
        self.data.board.move_pawn(pawn, self.rolled_value)
            )
        sp.if self.data.board.does_pawn_reach_end(pawn):
            player.pawns.remove(pawn)
            sp.if not player.pawns:
                self.data.standing.append(player)
                self.data.players.remove(player)
                sp.if len(self.data.players) == 1:
                    self.data.standing.extend(self.data.players)
                    self.data.finished = True
        sp.else:
            self.data._jog_foreign_pawn(pawn)


    @sp.entry_point
    def play_turn(self, ind=None, rolled_val=None):
        '''this is main method which must be used to play game.
        Method ask for next player's turn, roll die, ask player
        to choose pawn, move pawn.
        ind and rolled_val are suitable to be used when
        game must be replicated (recorded)
        ind is chosen index from allowed pawns
        '''
        self.data.jog_pawns = []
        self.data.curr_player = self.data._get_next_turn()
        sp.if sp.rolled_val is None:
            self.data.rolled_value = Die.throw()
        sp.else:
            self.data.rolled_value = rolled_val
        self.data.allowed_pawns = self.data.get_allowed_pawns_to_move(
            self.data.curr_player, self.data.rolled_value)
        sp.if self.data.allowed_pawns:
            sp.if sp.ind is None:
                self.data.index = self.data.curr_player.choose_pawn(
                    self.data.allowed_pawns)
            sp.else:
                self.data.index = ind
            self.data.picked_pawn = self.data.allowed_pawns[self.index]
            self.data._make_move(self.data.curr_player, self.picked_pawn)
        sp.else:
            self.data.index = -1
            self.data.picked_pawn = None

        