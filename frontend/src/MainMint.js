import  {useState} from 'react';


const MainMint = ({accounts, SetAccounts }) => {
    const [mintAmount, SetMintAmount] = useState(1);
    const isConnected = Boolean(accounts[0]);

    async function handleMint() {
        
    }
}