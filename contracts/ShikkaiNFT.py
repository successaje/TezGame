import smartpy as sp
FA2 = sp.io.import_script_from_url("https://smartpy.io/templates/fa2_lib.py")

class MinTezNft(
    FA2.Admin,
    FA2.ChangeMetadata,
    FA2.WithdrawMutez,
    FA2.MintNft,
    FA2.OnchainviewBalanceOf,
    FA2.Fa2Nft
):
    def __init__(self, admin, metadata, policy = None):
        FA2.FA2Nft.__init__(self, metadata, policy = policy)
        FA2.Admin.__init__(self, admin)

        self.update_initial_storage(
            closed = False,
            special_rights = sp.big_map({}, tkey = sp.Address, tvalue = sp.TSet(sp.Bytes))
        )

    @sp.entry_point
    def mint(self, batch):
        # Anyone can mint
        with sp.for_("action", batch) as action:
            token_id = sp.compute(self.data.nb_tokens)
            self.data.token_metadata[token_id] = sp.record(token_id = token_id, token_info  = action.metadata)
            self.data.ledger[token_id] = action.to_
            self.data.nb_tokens += 1

    @sp.entry_point
    def burn(self, batch):
        # We check the policy
        sp.verify(self.policy.supports_transfer, "FA2_TX_DENIED")
        with sp.for_("action", batch) as action:
            # We check the policy
            sp.verify(self.is_defined(action.token_id), "FA2_TOKEN_UNDEFINED")
            self.policy.check_tx_transfer_permissions(
                self, action.from_, action.from_, action.token_id
            )

    @sp.add_test(name="FA2 NFT tokens")
    def test():
        sc = sp.test_scenario()
        sc.table_of_contents()
        sc.h2("FA2")
        mintez_fa2_nft = MinTezNft(
            metadata = sp.utils.metadata_of_url("https://example.com")
        )
        sc += mintez_fa2_nft



