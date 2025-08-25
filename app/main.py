import traceback
from threading import Lock
import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Should this be in an init file or something?
DB_PATH = "./db/bank.db"
SCHEMA_PATH = "./db/schema.sql"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

transfer_lock = Lock()

def create_conn():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    except Exception as e:
        print("Exception in create_conn")
        traceback.print_exc()

    try:
        yield conn
    finally:
        if conn:
            conn.close()


class CreateUserRequest(BaseModel):
    username: str

@app.post("/users")
def create_user(req: CreateUserRequest, conn=Depends(create_conn)):
    # Logical for this to create an account along with a user. Actually, I don't think so
    username = req.username
    if username == "":
        raise HTTPException(status_code=400, detail="username cannot be blank")

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username) VALUES (?);",
            (username,)
        )
        conn.commit()
        user_id = cursor.lastrowid

        return {"user_id": user_id, "username": username}
    except Exception as e:
        print("Error in create_user")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to create user")


class CreateAccountRequest(BaseModel):
    account_name: str = None
    user_id: int
    balance: int

@app.post("/accounts")
def create_account(req: CreateAccountRequest, conn=Depends(create_conn)):
    account_name = req.account_name
    user_id = req.user_id
    balance = req.balance
    account_id = None

    if (balance < 0):
        raise HTTPException(
            status_code=400, 
            detail="Account balance must not be negative"
        )

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username FROM users WHERE user_id = ?;",
            (user_id,)
        )
        username_res = cursor.fetchone()
        if username_res == None:
            raise HTTPException(status_code=404, detail="Unable to find specified user")

        username = username_res[0]

        if account_name == None:
            cursor.execute(
                "SELECT COUNT(account_id) FROM accounts WHERE user_id = ?;",
                (user_id,)    
            )
            count = cursor.fetchone()[0]
            account_name = f"{username} Account #{int(count)+1}"
        else:
            cursor.execute(
                """
                    SELECT account_id FROM accounts 
                    WHERE account_name = ? AND user_id = ?;
                """,
                (account_name, user_id,)
            )
            res = cursor.fetchone()
            if res != None:
                raise HTTPException(status_code=409, detail="Duplicate account name")

        cursor.execute(
            """
                INSERT INTO accounts (account_name, user_id, balance)
                VALUES (?, ?, ?);
            """,
            (account_name, user_id, balance,)
        )
        account_id = cursor.lastrowid
        conn.commit()

        return {
            "account_id": account_id,
            "account_name": account_name, 
            "user_id": user_id,
            "balance": balance
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception in create_account, user_id: {user_id}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to create account")


def perform_transfer(sender_id, receiver_id, transfer_amount, conn):
    cursor = conn.cursor()
    cursor.execute("BEGIN")

    sender_balance = get_balance(sender_id, conn)
    receiver_balance = get_balance(receiver_id, conn)

    if sender_balance == None:
        raise HTTPException(status_code=404, detail="Sender account not found")
    if receiver_balance == None:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    sender_resulting_balance = sender_balance - transfer_amount
    receiver_resulting_balance = receiver_balance + transfer_amount

    if sender_resulting_balance < 0:
        raise HTTPException(
            status_code=422,
            detail="Sender account lacks requisite funds"
        )
    
    set_balance(sender_id, sender_resulting_balance, conn)
    set_balance(receiver_id, receiver_resulting_balance, conn)

    # Log the transfer
    cursor.execute(
        """
            INSERT INTO transfers (sender, receiver, transfer_amount,
            sender_resulting_balance, receiver_resulting_balance)
            VALUES (?, ?, ?, ?, ?);
        """, 
        (sender_id, receiver_id, transfer_amount,
        sender_resulting_balance, receiver_resulting_balance)
    )

    transfer_id = cursor.lastrowid
    conn.commit()

    return {
        "transfer_id": transfer_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "transfer_amount": transfer_amount,
        "sender_resulting_balance": sender_resulting_balance,
        "receiver_resulting_balance": receiver_resulting_balance
    }


class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: int

@app.post("/transfers")
def transfer_funds(req: TransferRequest, conn=Depends(create_conn)):
    sender_id = req.sender_id
    receiver_id = req.receiver_id
    transfer_amount = req.amount
    
    if sender_id == receiver_id:
        raise HTTPException(
            status_code=400, 
            detail="Sender and Receiver must be different accounts"
        )
    # Disallow simultaneous transfers
    with transfer_lock:
        try:
            return perform_transfer(sender_id, receiver_id, transfer_amount, conn)    
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            print(f"Exception in transfer_money, sender_id: {sender_id}, receiver_id: {receiver_id}")
            traceback.print_exc()
            conn.rollback()
            raise HTTPException(status_code=500, detail="Unable to transfer funds")


def set_balance(account_id: int, balance: int, conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?;",
        (balance, account_id)
    )


def get_balance(account_id: int, conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT balance FROM accounts WHERE account_id = ?;",
        (account_id,)
    )
    res = cursor.fetchone()
    
    if res == None:
        return None
    
    return res[0]


@app.get("/accounts/{account_id}/balance")
def get_account_balance(account_id: int, conn=Depends(create_conn)):
    try:
        balance = get_balance(account_id, conn)
        if balance == None:
            raise HTTPException(
                status_code=404,
                detail="Unable to find specified account"
            )

        return {"account_id": account_id, "balance": balance}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception in get_account_balance, account_id: {account_id}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail="Unable to get account balance"
        )


def format_transfers(transfer_rows, account_id):
    transfers = []
    for row in transfer_rows:
        account_role = "sender" if row[1] == account_id else "receiver"
        transfers.append({
            "transfer_id": row[0],
            "account_role": account_role,
            "sender_id": row[1],
            "receiver_id": row[2],
            "transfer_amount": row[3],
            "resulting_balance": row[4] if account_role == "sender" else row[5],
            "transfer_time": row[6]
        })
    
    return transfers


@app.get("/accounts/{account_id}/transfer_history")
def get_transfer_history(account_id: int, conn=Depends(create_conn)):
    cursor = conn.cursor()
    transfers = None

    try:
        balance = cursor.execute(
            "SELECT account_id FROM accounts WHERE account_id = ?;",
            (account_id,)
        ).fetchone()
        if balance == None:
            raise HTTPException(
                status_code=404,
                detail="Unable to find specified account"
            )

        cursor.execute(
            """
                SELECT transfer_id, sender, receiver,
                transfer_amount, sender_resulting_balance,
                receiver_resulting_balance, transfer_time
                FROM transfers
                WHERE sender = ? OR receiver = ?
                ORDER BY transfer_id ASC;
            """,
            (account_id, account_id,)
        )
        res = cursor.fetchall()
        transfers = format_transfers(res, account_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception in get_transfer_history, account_id: {account_id}", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to get transfer history")

    return {
        "account_id": account_id, 
        "transfers": transfers
    }


### Extra funtionality for web app ###

def format_accounts(account_rows):
    user_accounts = {}

    try:
        for row in account_rows:
            account = {
                "account_id": row[2],
                "account_name": row[3],
                "balance": row[4]
            }

            if row[0] in user_accounts:
                user_accounts[row[0]]["accounts"].append(account)
            else:
                user = {
                    "user_id": row[0],
                    "username": row[1]
                }

                # Avoid accounts full of None if user has no accounts
                if (account["account_id"]):
                    user["accounts"] = [account]

                user_accounts[row[0]] = user

        return list(user_accounts.values()) # No need for the keys
    except Exception as e:
        print("Error in formatAccounts", e)
        traceback.print_exc()


@app.get("/users")
def get_all_users(conn=Depends(create_conn)):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
                SELECT u.user_id, u.username, a.account_id, a.account_name,
                       a.balance
                FROM users u
                LEFT JOIN accounts a ON u.user_id = a.user_id;
            """, ()
        )
        res = cursor.fetchall()
        users = format_accounts(res)
        return users
    except Exception as e:
        print("Exception in get_all_users:", e)
        raise HTTPException(
            status_code=500, 
            detail="Unable to return all user info"
        )


@app.get("/health")
def health():
    return "Healthy"


@app.on_event("startup")
def init_db():
    generator = create_conn()
    conn = next(generator)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r') as file:
        cursor.executescript(file.read())

    conn.commit()
    conn.close()
