import smartpy as sp
import random

cl = sp.io.import _template("ludo_logic.py")

t_status = sp.TVariant(
    play = sp.TUnit,
    won = sp.TBounded(["player_1_won", "player_2_won", "player_3_won", "player_4_won"]), 
    lost =  sp.TBounded(["player_1_lost", "player_2_lost", "player_3_lost", "player_4_lost"]),  
)

class Ludo(sp.Contract):
    def __init__(self, player1, player2, player3, player4):
        self.init(
            board_state = cl.initial_board_state(), #coming soon
            give_up = sp.set(),
            metadata = sp.big_map(),
            players = sp.set([player1, player2, player3, player4]),
            players_map = sp.map({-1: player2, 1: player1, -2: player3, 2: player4}),
            staus = sp.variant("play", sp.unit)
        )

        self.init_type(sp.TRecord(
            board_state = cl.Types.t_board_state, #coming soon
            give_up  = sp.TSet(sp.TAddress),
            metadata    = sp.TBigMap(sp.TString, sp.TBytes),
            players     = sp.TSet(sp.TAddress),
            players_map = sp.TMap(sp.TInt, sp.TAddress),
            status      = t_status,
        ))

    @sp.private_lambda
    def get_movable_to(self, params):
        sp.result(
            sp.set_type_expr(
                cl.Lamda_ready.get_movable_to(params),
                sp.TList(sp.TRecord(side_1 = sp.TInt, side_2 = sp.TInt))
            )
        )

    @sp.private_lambda(with_storage = "read-write")
    def move_piece(self, params):
        sp.set_type(params.move, cl.Types.t_move)
        board_state, is_draw = cl.Lambda_ready.move_piece(self.data.board_state, params.move, params.get_movable_to)
        sp.result((board_state, is_draw))

    @sp.entry_point
    def giveup(self):
        """Giveup the game."""
        sp.verify(~self.data.status.is_variant("lost"))
        with sp.if_(sp.sender == self.data.players_map[-1]):
            self.data.status = sp.variant("lost", sp.bounded("player_2_lost"))

        with sp.elif_(sp.sender == self.data.players_map[-2]):
            self.data.status  = sp.variant("lost", sp.bounded("player_3_lost"))

        with sp.elif_(sp.sender == self.data.players_map[2]):
            self.data.status = sp.variant("lost", sp.bounded("player_4_lost"))

        with sp.else_():
            with sp.if_(sp.sender == self.data.players_map[1]):
                self.data.status = sp.variant("lost", sp.bounded("player_1_lost"))
                
            with sp.else_():
                sp.failwith("Wrong player")

    @sp.entry_point
    def rollTheDice(self):




class Player:
    name = None
    score = None
    no_of_sixes = None
    __dice_role_outcome = []

    def __init__(self, Name):
        self.name = Name
        self.dice_role_outcome = []
        self.score = 0
        self.no_of_sixes = 0

    def getScore(self):
        self.score = sum(self.dice_role_outcome)
        return self.score

    def get_no_of_sixes(self):
        self.no_of_sixes = self.dice_role_outcome.count(6)
        return self.no_of_sixes

    def rollTheDice(self):
        self.__dice_role_outcome.append(random.randint(1,6)) 
        print(self.__dice_role_outcome[-1])


player1 = Player("Hashirama")
player1.rollTheDice()



