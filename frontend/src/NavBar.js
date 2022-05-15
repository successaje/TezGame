import React from 'react';

const NavBar = ({ accounts, setAccounts }) => {
    const isConnected = Boolean(accounts[0]);

    async function connectWallet() {
        try {
          if(!wallet) await createWallet();
          await wallet.requestPermissions({
            network: {
              type: NetworkType.ITHACANET,
              rpcUrl: "https://ithacanet.tezos.marigold.dev"
            }
          });
          // gets user's address
          const userAddress = await wallet.getPKH();
          await setup(userAddress);
        } catch (error) {
          console.log(error);
        }


    }

    return (
        <div>

        {/*Left side - Social Media Icons */}
        <div>Facebook</div>
        <div>Twitter</div>
        <div>Email</div>

        {/*Right Side - Section and  Connect*/}
        <div>About</div>
        <div>Mint</div>
        <div>Team</div>

        {/* Connetc */}
        {isConnected ? (
            <p>Connected</p>
        ) : (
            <button onClick = {connectWallet}>Connetc</button>
        )}
        </div>    
    );
};