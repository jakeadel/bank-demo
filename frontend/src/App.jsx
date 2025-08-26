import { useEffect, useState } from 'react'
import './index.css'

const ROOT_URL = import.meta.env.VITE_ROOT_URL;

function App() {
    const [users, setUsers] = useState([]);
    const [newUsername, setNewUsername] = useState("");

    const [newAccountUserId, setNewAccountUserId] = useState("");
    const [newAccountName, setNewAccountName] = useState("");
    const [newAccountBalance, setNewAccountBalance] = useState("");

    const [transferAmount, setTransferAmount] = useState("");
    const [senderId, setSenderId] = useState("")
    const [receiverId, setReceiverId] = useState("");

    const [updateTransfers, setUpdateTransfers] = useState(0);

    const [errorMessages, setErrorMessages] = useState([]);

    useEffect(() => {
        async function get_user_data() {
            try {
                const users = await get_users();
                setUsers(users)
            } catch (error) {
                console.log("Error grabbing user data", {error});
            }
        }
        get_user_data();
    }, []);

    function addError(message, error) {
        let errors_copy = [...errorMessages];
        errors_copy.push(`${message}, ${error}`);
        setErrorMessages(errors_copy);
    }

    async function addUser(event) {
        event.preventDefault();
        let res;
        try {
            res = await create_user(newUsername);
        } catch (error) {
            console.log("Error adding user", {error});
            addError("Error adding user", error);
            return;
        }
        const {user_id, username} = res;
        let users_copy = [...users];
        users_copy.push({user_id, username, account: []});
        setUsers(users_copy);
        setNewUsername("");
    }

    async function addAccount(event) {
        event.preventDefault();
        let res;
        try {
            res = await create_account(newAccountUserId, newAccountBalance*100, newAccountName);
        } catch (error) {
            console.log("Error adding account", {error});
            addError("Error adding account", error);
            return;
        }
        const {account_id} = res;
        let users_copy = [...users];

        for (let i = 0; i < users_copy.length; i++) {
            if (users_copy[i].user_id === parseInt(newAccountUserId)) {
                if (users_copy[i].accounts) {
                    users_copy[i].accounts.push({
                        account_id, 
                        account_name: newAccountName,
                        balance: newAccountBalance*100
                    });
                }
                else {
                    users_copy[i].accounts = [{
                        account_id, 
                        account_name: newAccountName, 
                        balance: newAccountBalance*100
                    }];
                }
            }
        }
        setUsers(users_copy);
        setNewAccountName("");
        setNewAccountBalance("");
        setNewAccountUserId("");
    }

    async function transferFunds(event) {
        // Update transfers for both accounts if possible
        event.preventDefault();
        try {
            const res = await transfer_funds(senderId, receiverId, transferAmount*100);
        } catch (error) {
            console.log("Error transferring funds", {error});
            addError("Error transferring funds", error);
            return;
        }

        let users_copy = [...users];

        for (let i = 0; i < users_copy.length; i++) {
            if (users_copy[i].accounts) {
                let accounts = users_copy[i].accounts;
                for (let j = 0; j < accounts.length; j++) {
                    if (accounts[j].account_id === parseInt(senderId) || accounts[j].account_id === parseInt(receiverId)) {
                        try {
                            const res = await get_account_balance(accounts[j].account_id);
                            const balance = res.balance;
                            users_copy[i].accounts[j].balance = balance;
                        } catch (error) {
                            console.log("Unable to refresh funds", {error});
                            addError("Unable to refresh funds", error);
                        }
                    }
                }
            }
        }
        setUsers(users_copy);
        setUpdateTransfers(updateTransfers+1);
        setTransferAmount("");
        setSenderId("");
        setReceiverId("");
    }

    return (
        <>
            <div className='dashboard'>
                <h1 className='dashboard-title'>Admin Dashboard</h1>
                <div className='dashboard-elements'>
                    <form id="add-user" onSubmit={addUser}>
                        <h3 className='action-title'>Create New User</h3>
                        <input 
                            id="username-field"
                            type="text"
                            placeholder="Enter Username"
                            value={newUsername}
                            onChange={(elem) => setNewUsername(elem.target.value)}
                        />
                        <button type="submit">Submit</button>
                    </form>
                    <form id="add-account" onSubmit={addAccount}>
                        <h3 className='action-title'>Create New Account</h3>
                        <input 
                            id="user-id-field"
                            type="text"
                            placeholder="Enter User ID"
                            value={newAccountUserId}
                            onChange={(elem) => setNewAccountUserId(elem.target.value)}
                        />
                        <input 
                            id="account-name-field"
                            type="text"
                            placeholder="Enter Account Name"
                            value={newAccountName}
                            onChange={(elem) => setNewAccountName(elem.target.value)}
                        />
                        <input 
                            id="acount-balance-field"
                            type="number"
                            step="0.01"
                            min="0"
                            placeholder="Enter Deposit Amount in Dollars"
                            value={newAccountBalance}
                            onChange={(elem) => setNewAccountBalance(elem.target.value)}
                        />
                        <button type="submit">Submit</button>
                    </form>
                    <form id="transfer-funds" onSubmit={transferFunds}>
                        <h3 className='action-title'>Transfer Funds</h3>
                        <input 
                            id="amount-field"
                            type="number"
                            step="0.01"
                            min="0"
                            placeholder="Enter Amount in Dollars"
                            value={transferAmount}
                            onChange={(elem) => setTransferAmount(elem.target.value)}
                        />
                        <input
                            id="sender-field"
                            type="number"
                            step="1"
                            placeholder="Enter Sender Account ID"
                            value={senderId}
                            onChange={(elem) => setSenderId(elem.target.value)}
                        />
                        <input
                            id="receiver-field"
                            type="number"
                            step="1"
                            placeholder="Enter Receiver Account ID"
                            value={receiverId}
                            onChange={(elem) => setReceiverId(elem.target.value)}
                        />
                        <button type="submit">Submit</button>
                    </form>
                </div>
            </div>
            <div className='users-wrapper'>
                <div className='users'>
                    <h2 className='users-title'>Users</h2>
                    
                    {users.map((user) => (
                        <User user={user} updateTransfers={updateTransfers} addError={addError}/>
                    ))}
                </div>
            </div>
            <div className='error-wrapper'>
                <div className='error-box'>Error log:</div>
                {errorMessages.map((message) => (
                    <p>{message}</p>
                ))}
            </div>
        </>
    )
}

function User({user, updateTransfers, addError}) {
    return (
        <div className='user' key={user.id}>
            <div className='user-info'>
                <h2 className='user-elem'>Username: {user.username}, ID: {user.user_id}</h2>
            </div>
            
            {user.accounts?.length > 0 && (
                <div className='accounts'>
                    <h2 className='accounts-title'>Accounts</h2>
                    <div className='headers'>
                        <span className='header-elem'>Account ID</span>
                        <span className='header-elem'>Name</span>
                        <span className='header-elem'>Balance</span>
                    </div>
                    {user.accounts?.map((account) => (
                        <Account account={account} updateTransfers={updateTransfers} addError={addError} />
                    ))}
                </div>
            )}
            
        </div>
    );
}

function Account({account, updateTransfers, addError}) {
    const [showTransfers, setShowTransfers] = useState(false);
    const [transfers, setTransfers] = useState([]);

    useEffect(() => {
        if (showTransfers) {
            (async () => {
                let res;
                try {
                    res = await get_transfer_history(account.account_id);
                    setTransfers(res.transfers);
                }
                catch (error) {
                    console.log("Unable to get transfers", {error})
                    addError("Unable to get transfers", error);
                }
            })();
        }
    }, [showTransfers, updateTransfers]);

    async function handleSeeTransfers() {
        if (showTransfers) {
            setShowTransfers(false);
            return;
        }
        let res;
        try {
            res = await get_transfer_history(account.account_id);
        }
        catch (error) {
            console.log("Unable to get transfers", {error});
            addError("Unable to get transfers", error);
            return;
        }
        setTransfers(res.transfers);
        setShowTransfers(true);
    }

    return (
        <div className='account' key={account.account_id}>
            <div className='account-row'>
                <span className='row-elem'>{account.account_id}</span>
                <span className='row-elem'>{account.account_name}</span>
                <span className='row-elem balance'>{formatMoney(account.balance)}</span>
                <span className='row-elem'>
                    <button className='action-button' onClick={handleSeeTransfers}>Transfer History</button>
                </span>
            </div>
            {showTransfers && (
                <div className='transfers-wrapper'>
                    <h3 className='transfers-title'>Transfers</h3>
                    <div className='transfer-headers'>
                        <span className='header-elem'>Transfer ID</span>
                        <span className='header-elem'>Role</span>
                        <span className='header-elem'>Sender Account</span>
                        <span className='header-elem'>Receiver Account</span>
                        <span className='header-elem'>Amount</span>
                        <span className='header-elem'>Resulting Balance</span>
                        <span className='header-elem large-elem'>Timestamp</span>
                    </div>
                    <div className='transfer-rows'>
                        {transfers?.length > 0 && transfers.map((transfer) => (
                            <Transfer transfer={transfer} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function Transfer({transfer}) {
    return (
        <div className='transfer-row'>
            <span className='row-elem'>{transfer.transfer_id}</span>
            <span className='row-elem'>{transfer.account_role}</span>
            <span className='row-elem'>{transfer.sender_id}</span>
            <span className='row-elem'>{transfer.receiver_id}</span>
            <span className='row-elem'>{formatMoney(transfer.transfer_amount)}</span>
            <span className='row-elem'>{formatMoney(transfer.resulting_balance)}</span>
            <span className='row-elem large-elem'>{transfer.transfer_time}</span>
        </div>
    );
}

function formatMoney(cents) {
    return `$${parseFloat(cents / 100).toFixed(2)}`
}

async function create_user(username) {
    const url = ROOT_URL + "/users";
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username})
    });
    if (res.ok) {
        const data = await res.json();
        return data;
    }
    else {
        throw new Error(res.statusText);
    }
}

async function create_account(user_id, balance, account_name=null) {
    const url = ROOT_URL + "/accounts";

    let body = {user_id, balance};
    if (account_name) {
        body["account_name"] = account_name
    }
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });
    if (res.ok) {
        const data = await res.json();
        return data;
    }
    else {
        throw new Error(res.statusText);
    }
}

async function transfer_funds(sender_id, receiver_id, amount) {
    const url = ROOT_URL + "/transfers";

    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({sender_id, receiver_id, transfer_amount: amount})
    });
    if (res.ok) {
        const data = await res.json();
        return data;
    }
    else {
        throw new Error(res.statusText);
    }
}

async function get_account_balance(account_id) {
    const url = ROOT_URL + `/accounts/${account_id}/balance`;
    const res = await fetch(url);
    if (res.ok) {
        const data = await res.json();
        return data;
    }
    else {
        throw new Error(res.statusText);
    }
}

async function get_transfer_history(account_id) {
    const url = ROOT_URL + `/accounts/${account_id}/transfer_history`;
    const res = await fetch(url);
    if (res.ok) {
        const data = await res.json();
        return data;
    }
    else {
        throw new Error(res.statusText);
    }
    
}

async function get_users() {
    const url = ROOT_URL + '/users';
    const res = await fetch(url);
    const data = await res.json();
    return data;
}

export default App;
