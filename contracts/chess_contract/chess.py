# Chess
# Example for ILLUSTRATIVE PURPOSE ONLY

import smartpy as sp

cl = sp.io.import_template("chess_logic.py")

t_status = sp.TVariant(
    play            = sp.TUnit,
    force_play      = sp.TUnit,
    finished        = sp.TBounded(["draw", "player_1_won", "player_2_won"]),
    claim_stalemate = sp.TUnit,
)


class Chess(sp.Contract):
    def __init__(self, player1, player2):
        self.init(
            board_state = cl.initial_board_state(),
            draw_offer  = sp.set(),
            metadata    = sp.big_map(),
            players     = sp.set([player1, player2]),
            players_map = sp.map({-1: player2, 1: player1}),
            status      = sp.variant("play", sp.unit),
        )

        self.init_type(sp.TRecord(
            board_state = cl.Types.t_board_state,
            draw_offer  = sp.TSet(sp.TAddress),
            metadata    = sp.TBigMap(sp.TString, sp.TBytes),
            players     = sp.TSet(sp.TAddress),
            players_map = sp.TMap(sp.TInt, sp.TAddress),
            status      = t_status,
        ))

        list_of_views = [self.build_fen]
        metadata_base = {
            "version": "alpha 0.1",
            "description" : (
                """Example of a chess game contract.\n
                   Given as an ILLUSTRATIVE PURPOSE ONLY
                """
            ),
            "interfaces": ["TZIP-016"],
            "authors": [
                "SmartPy <https://smartpy.io>"
            ],
            "homepage": "https://smartpy.io",
            "views": list_of_views,
            "source": {
                "tools": ["SmartPy"],
                "location": "https://gitlab.com/SmartPy/smartpy/-/blob/master/python/templates/state_channel_games/game_platform.py"
            },
        }
        self.init_metadata("metadata_base", metadata_base)

    # Offchain views #

    @sp.offchain_view(pure = True)
    def build_fen(self):
        """Return the state of the board chess in the fen standard"""
        sp.result(cl.Lambda_ready.build_fen(self.data.board_state))

    # Private lambdas #

    @sp.private_lambda(wrap_call = True)
    def get_movable_to(self, params):
        """ Return player's list of pieces that are capable to move on a cell.
            ASSUME That the cell doesn't contain a piece owned by `player`.
            ASSUME That the cell contains a piece owned by opponent if `pawn_eating` is True
            Don't take into account "En passant".
            Don't take into account if the move/take is illegal because player would be in check after it.

            Params:
                i, j (sp.TInt): cell's coordinates
                player (sp.TInt): attacking player
                deck: current deck
                pawn_eating (sp.TBool): if pawn_eating is True: pawns are eating else: moving
        """
        sp.result(
            sp.set_type_expr(
                cl.Lambda_ready.get_movable_to(params),
                sp.TList(sp.TRecord(i = sp.TInt, j = sp.TInt))
            )
        )

    @sp.private_lambda(with_storage = "read-write")
    def move_piece(self, params):
        sp.set_type(params.move, cl.Types.t_move)
        board_state, is_draw = cl.Lambda_ready.move_piece(self.data.board_state, params.move, params.get_movable_to)
        sp.result((board_state, is_draw))

    # Entry points #

    @sp.entry_point
    def giveup(self):
        """Giveup the game."""
        sp.verify(~self.data.status.is_variant("finished"))
        with sp.if_(sp.sender == self.data.players_map[-1]):
            self.data.status = sp.variant("finished", sp.bounded("player_1_won"))
        with sp.else_():
            with sp.if_(sp.sender == self.data.players_map[1]):
                self.data.status = sp.variant("finished", sp.bounded("player_2_won"))
            with sp.else_():
                sp.failwith("Wrong player")

    @sp.entry_point
    def threefold_repetition_claim(self, fullMove1, fullMove2):
        """ Claim draw by 3 repeated moves by giving 2 fullMove numbers identical to the current move.

            A player may claim a draw if the same position occured three times.
            Two positions are by definition "the same" if:
                - the same types of pieces occupy the same squares
                - the same player has the move
                - the remaining castling rights are the same and the possibility to capture en passant is the same.
            The repeated positions need not occur in succession.

            The `threefold_repetition_claim` entry point can only be called before playing a move.
            Players can claim threefold repetition after having done a move by using the `play` entry point.

            Fullmove start at 1 and is incremented only after both players_map played one time.
        """
        sp.verify(~self.data.status.is_variant("finished"), message = "Game finished")
        sp.verify(self.data.players_map[self.data.board_state.nextPlayer] == sp.sender, message = "Wrong player")
        previousFullMove = sp.eif(self.data.board_state.nextPlayer == 1, sp.as_nat(self.data.board_state.fullMove - 1), self.data.board_state.fullMove)
        cl.verify_repeat(self.data.board_state, self.data.board_state.nextPlayer * -1, sp.set([fullMove1, fullMove2, previousFullMove]))
        self.data.status = sp.variant("finished", sp.bounded("draw"))

    @sp.entry_point
    def offer_draw(self):
        """ Offer / acccept a draw agrement
            A player may offer a draw at any stage.
            If the opponent accepts, the game is a draw.
            A draw offering cannot be retracted.
            A draw offering is denied by calling the `deny_draw` entry point  or by playing a move.
        """
        sp.verify(~self.data.status.is_variant("finished"), message = "Game finished")
        sp.verify(self.data.players.contains(sp.sender), "Wrong player")
        self.data.draw_offer.add(sp.sender)
        with sp.if_(sp.len(self.data.draw_offer) == 2):
            self.data.status = sp.variant("finished", sp.bounded("draw"))

    @sp.entry_point
    def claim_stalemate(self):
        sp.verify(sp.sender == self.data.players_map[self.data.board_state.nextPlayer], "Wrong player")
        sp.verify(self.data.status.is_variant("play"))
        self.data.status = sp.variant("claim_stalemate", sp.unit)
        self.data.board_state.nextPlayer *= -1

    @sp.entry_point
    def answer_stalemate(self, answer):
        sp.set_type(answer, sp.TVariant(accept = sp.TUnit, refuse = cl.Types.t_move))
        sp.verify(sp.sender == self.data.players_map[self.data.board_state.nextPlayer], "Wrong player")
        sp.verify(self.data.status.is_variant("claim_stalemate"))
        with answer.match_cases() as answer:
            with answer.match("accept"):
                self.data.status = sp.variant("finished", sp.bounded("draw"))
            with answer.match("refuse") as refuse_move:
                cl.Lambda_ready.move_piece(self.data.board_state, refuse_move, self.get_movable_to)
                self.data.board_state.nextPlayer *= -1
                self.data.status = sp.variant("force_play", sp.unit)

    @sp.entry_point
    def play(self, move):
        """
            move: Record(f: Record(i: Nat, j: Nat), t: Record(i: Nat, j: Nat))
                f: from cell
                t: destination cell

            claim_repeat: Option(TPair(TNat, TNat))
                Perform a threefold repetition claim after the move has been done
                params: 2 other identical fullMove number

            promotion: Option(Nat):
                2: ROOK
                3: KNIGHT
                4: BISHOP
                5: QUEEN
        """
        sp.verify(sp.sender == self.data.players_map[self.data.board_state.nextPlayer], "Wrong player")
        sp.verify(self.data.status.is_variant("play") | self.data.status.is_variant("force_play"))
        board_state, is_draw = sp.match_pair(cl.Lambda_ready.move_piece(self.data.board_state, move, self.get_movable_to))
        board_state = sp.compute(board_state)
        board_state.nextPlayer *= -1
        self.data.board_state = board_state
        with sp.if_(is_draw):
            self.data.status = sp.variant("finished", sp.bounded("draw"))
        self.data.draw_offer = sp.set()

    @sp.entry_point
    def claim_checkmate(self):
        board_state = sp.local("board_state", self.data.board_state).value
        with sp.if_(cl.is_checkmate(board_state, self.get_movable_to)):
            self.data.status = sp.eif(board_state.nextPlayer == 1, sp.variant("finished", sp.bounded("player_2_won")), sp.variant("finished", sp.bounded("player_1_won")))
        with sp.else_():
            sp.failwith("NotCheckmate")

    # Test utils #

    def html_of_state(self):
        col_names = ['a','b','c','d','e','f','g','h']
        row_names = [1,2,3,4,5,6,7,8]
        abbrev = ['.', 'p', 'R', 'N', 'B', 'Q', 'K']
        rows = [''.join("%s%s" % (' ' if int(x) == 0 else ('w' if 0 < int(x) else 'b'), abbrev[abs(int(x))]) for x in row) for row in self.data.board_state.deck]
        res = '<pre>%s</pre>' % '\n'.join(reversed(rows))
        res += '\n White King='
        king_col = col_names[self.data.board_state.kings[1].j]
        king_row = row_names[self.data.board_state.kings[1].i]
        res += '%s%s' % (king_col, king_row)
        res += '\t Black King='
        king_col = col_names[self.data.board_state.kings[-1].j]
        king_row = row_names[self.data.board_state.kings[-1].i]
        res += '%s%s' % (king_col, king_row)
        return res

# Tests
if "templates" not in __name__:
    player1 = sp.test_account('player1')
    player2 = sp.test_account('player2')
    def play(f, t, promotion = sp.none, claim_repeat = sp.none):
        return sp.record(f = f, t = t, promotion = promotion, claim_repeat = claim_repeat)

    @sp.add_test(name = "Chess - Adams Michael vs Sedgwick David")
    def test():
        c1 = Chess(player1.address, player2.address)

        sc = sp.test_scenario()
        sc.h1(" Adams, Michael vs. Sedgwick, David 1-0 London: Lloyds Bank op: 1984.??.??")
        sc += c1

        # Adams, Michael vs. Sedgwick, David 1-0
        # London: Lloyds Bank op: 1984.??.??
        sc.verify(c1.build_fen() == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        c1.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        sc.verify(c1.build_fen() == 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1')
        c1.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 5, j = 4))).run(sender = player2)
        sc.verify(c1.build_fen() == 'rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2')
        c1.play(play(f = sp.record(i = 1, j = 3), t = sp.record(i = 3, j = 3))).run(sender = player1)
        sc.verify(c1.build_fen() == 'rnbqkbnr/pppp1ppp/4p3/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3 0 2')
        c1.play(play(f = sp.record(i = 6, j = 3), t = sp.record(i = 4, j = 3))).run(sender = player2)
        sc.verify(c1.build_fen() == 'rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6 0 3')
        c1.play(play(f = sp.record(i = 0, j = 1), t = sp.record(i = 1, j = 3))).run(sender = player1)
        sc.verify(c1.build_fen() == 'rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPPN1PPP/R1BQKBNR b KQkq - 1 3')
        c1.play(play(f = sp.record(i = 7, j = 6), t = sp.record(i = 5, j = 5))).run(sender = player2)
        sc.verify(c1.build_fen() == 'rnbqkb1r/ppp2ppp/4pn2/3p4/3PP3/8/PPPN1PPP/R1BQKBNR w KQkq - 2 4')
        c1.play(play(f = sp.record(i = 3, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player1)
        sc.verify(c1.build_fen() == 'rnbqkb1r/ppp2ppp/4pn2/3pP3/3P4/8/PPPN1PPP/R1BQKBNR b KQkq - 0 4')
        c1.play(play(f = sp.record(i = 5, j = 5), t = sp.record(i = 6, j = 3))).run(sender = player2)
        sc.verify(c1.build_fen() == 'rnbqkb1r/pppn1ppp/4p3/3pP3/3P4/8/PPPN1PPP/R1BQKBNR w KQkq - 1 5')
        c1.play(play(f = sp.record(i = 1, j = 5), t = sp.record(i = 3, j = 5))).run(sender = player1)
        sc.verify(c1.build_fen() == 'rnbqkb1r/pppn1ppp/4p3/3pP3/3P1P2/8/PPPN2PP/R1BQKBNR b KQkq f3 0 5')
        c1.play(play(f = sp.record(i = 6, j = 2), t = sp.record(i = 4, j = 2))).run(sender = player2)
        sc.verify(c1.build_fen() == 'rnbqkb1r/pp1n1ppp/4p3/2ppP3/3P1P2/8/PPPN2PP/R1BQKBNR w KQkq c6 0 6')
        c1.play(play(f = sp.record(i = 1, j = 2), t = sp.record(i = 2, j = 2))).run(sender = player1)
        sc.verify(c1.build_fen() == 'rnbqkb1r/pp1n1ppp/4p3/2ppP3/3P1P2/2P5/PP1N2PP/R1BQKBNR b KQkq - 0 6')
        c1.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r1bqkb1r/pp1n1ppp/2n1p3/2ppP3/3P1P2/2P5/PP1N2PP/R1BQKBNR w KQkq - 1 7')
        c1.play(play(f = sp.record(i = 1, j = 3), t = sp.record(i = 2, j = 5))).run(sender = player1)
        sc.verify(c1.build_fen() == 'r1bqkb1r/pp1n1ppp/2n1p3/2ppP3/3P1P2/2P2N2/PP4PP/R1BQKBNR b KQkq - 2 7')
        c1.play(play(f = sp.record(i = 4, j = 2), t = sp.record(i = 3, j = 3))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r1bqkb1r/pp1n1ppp/2n1p3/3pP3/3p1P2/2P2N2/PP4PP/R1BQKBNR w KQkq - 0 8')
        c1.play(play(f = sp.record(i = 2, j = 2), t = sp.record(i = 3, j = 3))).run(sender = player1)
        sc.verify(c1.build_fen() == 'r1bqkb1r/pp1n1ppp/2n1p3/3pP3/3P1P2/5N2/PP4PP/R1BQKBNR b KQkq - 0 8')
        c1.play(play(f = sp.record(i = 6, j = 5), t = sp.record(i = 5, j = 5))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r1bqkb1r/pp1n2pp/2n1pp2/3pP3/3P1P2/5N2/PP4PP/R1BQKBNR w KQkq - 0 9')
        c1.play(play(f = sp.record(i = 0, j = 5), t = sp.record(i = 2, j = 3))).run(sender = player1)
        sc.verify(c1.build_fen() == 'r1bqkb1r/pp1n2pp/2n1pp2/3pP3/3P1P2/3B1N2/PP4PP/R1BQK1NR b KQkq - 1 9')
        c1.play(play(f = sp.record(i = 7, j = 5), t = sp.record(i = 3, j = 1))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r1bqk2r/pp1n2pp/2n1pp2/3pP3/1b1P1P2/3B1N2/PP4PP/R1BQK1NR w KQkq - 2 10')
        sc.verify(c1.data.board_state.check == True)
        c1.play(play(f = sp.record(i = 0, j = 2), t = sp.record(i = 1, j = 3))).run(sender = player1)
        sc.verify(c1.data.board_state.check == False)
        sc.verify(c1.build_fen() == 'r1bqk2r/pp1n2pp/2n1pp2/3pP3/1b1P1P2/3B1N2/PP1B2PP/R2QK1NR b KQkq - 3 10')
        c1.play(play(f = sp.record(i = 7, j = 3), t = sp.record(i = 5, j = 1))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r1b1k2r/pp1n2pp/1qn1pp2/3pP3/1b1P1P2/3B1N2/PP1B2PP/R2QK1NR w KQkq - 4 11')
        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 1, j = 4))).run(sender = player1)
        sc.verify(c1.build_fen() == 'r1b1k2r/pp1n2pp/1qn1pp2/3pP3/1b1P1P2/3B1N2/PP1BN1PP/R2QK2R b KQkq - 5 11')
        c1.play(play(f = sp.record(i = 5, j = 5), t = sp.record(i = 4, j = 4))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r1b1k2r/pp1n2pp/1qn1p3/3pp3/1b1P1P2/3B1N2/PP1BN1PP/R2QK2R w KQkq - 0 12')
        c1.play(play(f = sp.record(i = 3, j = 5), t = sp.record(i = 4, j = 4))).run(sender = player1)
        sc.verify(c1.build_fen() == 'r1b1k2r/pp1n2pp/1qn1p3/3pP3/1b1P4/3B1N2/PP1BN1PP/R2QK2R b KQkq - 0 12')
        c1.play(play(f = sp.record(i = 7, j = 4), t = sp.record(i = 7, j = 6))).run(sender = player2) # Castle
        sc.verify(c1.build_fen() == 'r1b2rk1/pp1n2pp/1qn1p3/3pP3/1b1P4/3B1N2/PP1BN1PP/R2QK2R w KQ - 1 13')
        c1.play(play(f = sp.record(i = 1, j = 0), t = sp.record(i = 2, j = 0))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 1), t = sp.record(i = 6, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 1, j = 2))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 5), t = sp.record(i = 2, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 3, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 1), t = sp.record(i = 3, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 4), t = sp.record(i = 0, j = 2))).run(sender = player1) # O-O-O
        sc.verify(c1.build_fen() == 'r1b3k1/pp1nb1pp/4p3/3pP3/3q4/P2B1P2/1PQB3P/2KR3R b - - 1 17')
        c1.play(play(f = sp.record(i = 6, j = 3), t = sp.record(i = 4, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 3), t = sp.record(i = 6, j = 7))).run(sender = player1) # check
        sc.verify(c1.build_fen() == 'r1b3k1/pp2b1pB/4p3/3pn3/3q4/P4P2/1PQB3P/2KR3R b - - 0 18')
        sc.verify(c1.data.board_state.check == True)
        c1.play(play(f = sp.record(i = 7, j = 6), t = sp.record(i = 7, j = 7))).run(sender = player2)
        sc.verify(c1.data.board_state.check == False)
        c1.play(play(f = sp.record(i = 0, j = 2), t = sp.record(i = 0, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 3), t = sp.record(i = 3, j = 7))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 3), t = sp.record(i = 2, j = 2))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 5, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 3, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 4, j = 4), t = sp.record(i = 3, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 2), t = sp.record(i = 5, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 7), t = sp.record(i = 5, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 6, j = 7), t = sp.record(i = 2, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 1), t = sp.record(i = 4, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 2), t = sp.record(i = 1, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 2), t = sp.record(i = 6, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 7), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 3), t = sp.record(i = 7, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 0, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 4), t = sp.record(i = 6, j = 5))).run(sender = player2)
        sc.verify(c1.build_fen() == 'r6k/p4bp1/4pq2/1p1p4/2n2P2/P2B4/1P2Q2P/1K2R1R1 w - - 6 27')
        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 0), t = sp.record(i = 7, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 4), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 2), t = sp.record(i = 5, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 6), t = sp.record(i = 6, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 3), t = sp.record(i = 4, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 6, j = 6), t = sp.record(i = 4, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 2), t = sp.record(i = 6, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 3), t = sp.record(i = 4, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 4), t = sp.record(i = 4, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 6), t = sp.record(i = 4, j = 7))).run(sender = player1) # Abandon
        sc.show(c1.build_fen())
        sc.verify(c1.build_fen() == '7k/p1r2b2/5q2/1p1p1p1R/5P2/P7/1P2Q2P/1K4R1 b - - 1 32')
        sc.verify(c1.data.board_state.check == True)
        c1.play(play(f = sp.record(i = 6, j = 5), t = sp.record(i = 4, j = 7))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 4, j = 7))).run(sender = player1)
        sc.show(c1.build_fen())
        c1.play(play(f = sp.record(i = 5, j = 5), t = sp.record(i = 5, j = 7))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 7), t = sp.record(i = 5, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 2), t = sp.record(i = 6, j = 7))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 7), t = sp.record(i = 7, j = 5))).run(sender = player1)

    @sp.add_test(name = "Chess - Vachier Lagrave Maxime vs Bacrot Etienne")
    def test():
        c1 = Chess(player1.address, player2.address)

        sc = sp.test_scenario()
        sc.h1("Vachier Lagrave,M (2579) vs. Bacrot,E (2705) 1/2-1/2")
        sc += c1

        # Vachier Lagrave,M (2579) vs. Bacrot,E (2705) 1/2-1/2
        c1.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 5), t = sp.record(i = 4, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 0), t = sp.record(i = 5, j = 0))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 3), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 4), t = sp.record(i = 0, j = 6))).run(sender = player1)
        sc.verify(c1.build_fen() == 'r1bqkbnr/1pp2ppp/p1p5/4p3/4P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 5')
        c1.play(play(f = sp.record(i = 6, j = 5), t = sp.record(i = 5, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 3), t = sp.record(i = 3, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 4, j = 4), t = sp.record(i = 3, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 3, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 4, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 3, j = 3), t = sp.record(i = 2, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 3), t = sp.record(i = 0, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 5), t = sp.record(i = 0, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 2), t = sp.record(i = 3, j = 6))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 5), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 6), t = sp.record(i = 6, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 1), t = sp.record(i = 2, j = 2))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 4), t = sp.record(i = 7, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 2), t = sp.record(i = 3, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 4, j = 2), t = sp.record(i = 3, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 1), t = sp.record(i = 4, j = 0))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 5), t = sp.record(i = 4, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 0, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 1), t = sp.record(i = 4, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 0), t = sp.record(i = 3, j = 0))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 6), t = sp.record(i = 6, j = 4))).run(sender = player2)
        sc.verify(c1.build_fen() == '2kr3r/2pbn1pp/p4p2/Npb5/P1p1PB2/2N2P2/1PP3PP/R2R1K2 w - - 1 16')
        c1.play(play(f = sp.record(i = 3, j = 0), t = sp.record(i = 4, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 3), t = sp.record(i = 4, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 3, j = 5), t = sp.record(i = 1, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 7), t = sp.record(i = 7, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 2), t = sp.record(i = 4, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 0), t = sp.record(i = 4, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 1), t = sp.record(i = 2, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 2), t = sp.record(i = 2, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 0), t = sp.record(i = 2, j = 1))).run(sender = player1)
        c1.play(play(f = sp.record(i = 4, j = 2), t = sp.record(i = 5, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 3), t = sp.record(i = 2, j = 2))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 3), t = sp.record(i = 0, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 0), t = sp.record(i = 0, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 2), t = sp.record(i = 4, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 5, j = 3))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 1), t = sp.record(i = 6, j = 0))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 3), t = sp.record(i = 5, j = 0))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 2), t = sp.record(i = 6, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 0), t = sp.record(i = 5, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 1), t = sp.record(i = 6, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 3, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 2), t = sp.record(i = 6, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 4), t = sp.record(i = 5, j = 0))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 7, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 4), t = sp.record(i = 5, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 6), t = sp.record(i = 5, j = 5))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 0), t = sp.record(i = 5, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 2), t = sp.record(i = 5, j = 3))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 5), t = sp.record(i = 5, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 4), t = sp.record(i = 6, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 7), t = sp.record(i = 4, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 3), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 2), t = sp.record(i = 0, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 3), t = sp.record(i = 3, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 4), t = sp.record(i = 1, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 2), t = sp.record(i = 2, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 1, j = 5), t = sp.record(i = 2, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 2, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 7), t = sp.record(i = 6, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 0), t = sp.record(i = 5, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 6, j = 7), t = sp.record(i = 5, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 6, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 7), t = sp.record(i = 6, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 2), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 6, j = 7), t = sp.record(i = 5, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 6, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 7), t = sp.record(i = 6, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 2), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 6, j = 7), t = sp.record(i = 5, j = 7))).run(sender = player1)
        sc.verify(c1.build_fen() == '8/8/1bk4R/1pp5/8/1N2rP2/2P3PP/5K2 b - - 10 40')

    @sp.add_test(name = "Chess - Promotion")
    def test():
        c1 = Chess(player1.address, player2.address)

        sc = sp.test_scenario()
        sc.h1("Promotion")
        sc += c1

        c1.play(play(f = sp.record(i = 1, j = 6), t = sp.record(i = 3, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 1), t = sp.record(i = 4, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 3, j = 6), t = sp.record(i = 4, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 4, j = 1), t = sp.record(i = 3, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 4, j = 6), t = sp.record(i = 5, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 3, j = 1), t = sp.record(i = 2, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 5, j = 6), t = sp.record(i = 6, j = 7))).run(sender = player1)
        c1.play(play(f = sp.record(i = 2, j = 1), t = sp.record(i = 1, j = 0))).run(sender = player2)
        c1.play(play(f = sp.record(i = 6, j = 7), t = sp.record(i = 7, j = 6), promotion = sp.some(5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 1, j = 0), t = sp.record(i = 0, j = 1), promotion = sp.some(3))).run(sender = player2)
        sc.show(c1.build_fen())
        sc.verify(c1.build_fen() == 'rnbqkbQr/p1ppppp1/8/8/8/8/1PPPPP1P/RnBQKBNR w KQkq - 0 6')

    @sp.add_test(name = "Chess - 3 times repeat")
    def test():
        c1 = Chess(player1.address, player2.address)

        sc = sp.test_scenario()
        sc.h1("3 times repeat")
        sc.h2("After move")
        sc += c1

        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1), claim_repeat = sp.some((0, 3)))).run(sender = player2, valid = False, exception = sp.pair("NotSameMove", sp.record(fullMove = 3)))
        c1.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1), claim_repeat = sp.some((0, 4)))).run(sender = player2)
        sc.verify(c1.data.status == sp.variant("finished", sp.bounded("draw")))

        sc.h2("Previous move")
        c2 = Chess(player1.address, player2.address)
        sc += c2

        c2.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c2.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c2.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c2.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1))).run(sender = player2)
        c2.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c2.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c2.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c2.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1))).run(sender = player2)
        c2.play(play(f = sp.record(i = 0, j = 6), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c2.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c2.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 0, j = 6))).run(sender = player1)
        c2.play(play(f = sp.record(i = 5, j = 2), t = sp.record(i = 7, j = 1))).run(sender = player2)
        c2.threefold_repetition_claim(fullMove1 = 0, fullMove2 = 5).run(sender = player1, valid = False, exception = sp.pair("NotSameMove", sp.record(fullMove = 5)))
        c2.threefold_repetition_claim(fullMove1 = 0, fullMove2 = 4).run(sender = player1)
        sc.verify(c2.data.status == sp.variant("finished", sp.bounded("draw")))

    @sp.add_test(name = "Chess - Checkmate")
    def test():
        sc = sp.test_scenario()
        sc.h1("Checkmate")

        sc.h2("Scholar's mate")
        c1 = Chess(player1.address, player2.address)
        sc += c1

        c1.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        c1.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 5), t = sp.record(i = 3, j = 2))).run(sender = player1)
        c1.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c1.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 4, j = 7))).run(sender = player1)
        c1.claim_checkmate().run(valid = False)
        c1.play(play(f = sp.record(i = 6, j = 0), t = sp.record(i = 4, j = 0))).run(sender = player2)
        c1.claim_checkmate().run(valid = False)
        c1.play(play(f = sp.record(i = 4, j = 7), t = sp.record(i = 6, j = 5))).run(sender = player1)
        c1.claim_checkmate()

        sc.h2("King eat the attacking piece")
        c2 = Chess(player1.address, player2.address)
        sc += c2

        c2.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        c2.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player2)
        c2.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 2, j = 5))).run(sender = player1)
        c2.play(play(f = sp.record(i = 7, j = 1), t = sp.record(i = 5, j = 2))).run(sender = player2)
        c2.play(play(f = sp.record(i = 2, j = 5), t = sp.record(i = 6, j = 5))).run(sender = player1)
        c2.claim_checkmate().run(valid = False)

        sc.h2("Suffocating King")
        c3 = Chess(player1.address, player2.address)
        sc += c3

        c3.play(play(f = sp.record(i = 0, j = 1), t = sp.record(i = 2, j = 2))).run(sender = player1)
        c3.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player2)
        c3.play(play(f = sp.record(i = 2, j = 2), t = sp.record(i = 4, j = 3))).run(sender = player1)
        c3.play(play(f = sp.record(i = 7, j = 6), t = sp.record(i = 6, j = 4))).run(sender = player2)
        c3.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        c3.play(play(f = sp.record(i = 6, j = 6), t = sp.record(i = 5, j = 6))).run(sender = player2)
        c3.play(play(f = sp.record(i = 4, j = 3), t = sp.record(i = 5, j = 5))).run(sender = player1)
        sc.show(c3.build_fen())
        c3.claim_checkmate()

        sc.h2("Obstructing column")
        c4 = Chess(player1.address, player2.address)
        sc += c4

        c4.play(play(f = sp.record(i = 0, j = 1), t = sp.record(i = 2, j = 2))).run(sender = player1)
        c4.play(play(f = sp.record(i = 6, j = 4), t = sp.record(i = 4, j = 4))).run(sender = player2)
        c4.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        c4.play(play(f = sp.record(i = 6, j = 0), t = sp.record(i = 4, j = 0))).run(sender = player2)
        c4.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 4, j = 7))).run(sender = player1)
        c4.play(play(f = sp.record(i = 4, j = 0), t = sp.record(i = 3, j = 0))).run(sender = player2)
        c4.play(play(f = sp.record(i = 4, j = 7), t = sp.record(i = 4, j = 4))).run(sender = player1)
        c4.claim_checkmate().run(valid = False)

        sc.h2("Obstructing diagonal")
        c5 = Chess(player1.address, player2.address)
        sc += c5

        c5.play(play(f = sp.record(i = 1, j = 4), t = sp.record(i = 3, j = 4))).run(sender = player1)
        c5.play(play(f = sp.record(i = 6, j = 5), t = sp.record(i = 4, j = 5))).run(sender = player2)
        c5.play(play(f = sp.record(i = 0, j = 3), t = sp.record(i = 4, j = 7))).run(sender = player1)
        c5.claim_checkmate().run(valid = False)
        c5.play(play(f = sp.record(i = 6, j = 6), t = sp.record(i = 5, j = 6))).run(sender = player2)
        c5.play(play(f = sp.record(i = 1, j = 7), t = sp.record(i = 2, j = 7))).run(sender = player1)
        c5.play(play(f = sp.record(i = 6, j = 7), t = sp.record(i = 5, j = 7))).run(sender = player2)
        c5.play(play(f = sp.record(i = 4, j = 7), t = sp.record(i = 5, j = 6))).run(sender = player1)
        c5.claim_checkmate()
        sc.verify_equal(c5.data.status, sp.variant("finished", sp.bounded("player_1_won")))

    sp.add_compilation_target("chess", Chess(sp.address("tz1_PLAYER_1"), sp.address("tz1_PLAYER_2")))
