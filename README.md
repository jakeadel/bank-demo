# Bank Demo App


## Install instructions:
    - pip3 install "fastapi[standard]"
    - requirements.txt
    - Run tests: pytest /app

Run with: from within /app, fastapi dev main.py


## Notes:
    - Money is held in Cents

## Improvements:
    - Add authentication, use JWT tokens
    - More structured logging
    - Build out further endpoints
        - PUT, DELETE for users, accounts, transfers
    - 


# API Reference

### Create User
**POST** `/users`

Request:
```json
{"username": "user_123"}
```

Response:
```json
{"user_id": 1, "username": "user_123"}
```

**Error codes:**
    - 422: missing required field
    - 400: blank username
    - 500: unknown error

### Create Account
**POST** /accounts

Request:
```json
{"account_name": "account_123", "user_id": 1, "balance": 100}
```
Note: balance is in Cents

Response:
```json
{"account_id": 1, "account_name": "account_123", "user_id": 1, "balance": 100}
```

**Error codes:**
- 422: missing required field
- 400: negative input balance
- 404: unable to find input user
- 409: duplicate account name
- 500: unknown error

### Transfer Funds
**POST** /transfers

Request:
```json
{"sender_id": 1, "receiver_id": 2, "transfer_amount": 100}
```

Note: sender_id and receiver_id are account_ids

Note: transfer_amount is in Cents

Response:
```json
{"transfer_id": 1, "sender_id": 1, "receiver_id": 2, "transfer_amount": 100, "sender_resulting_balance": 100, "receiver_resulting_balance": 200}
```



### Get Account Balance
**GET** /accounts/{account_id}/balance

Response:
```json
{
    "account_id": 1,
    "balance": 100
}
```

## Get Account Transfers
**GET** /accounts/{account_id}/transfer_history

Response:
```json
{
    "account_id": 1,
    "transfers": [
        {
            "transfer_id": 1,
            "account_role": "sender",
            "sender_id": 1,
            "receiver_id": 2,
            "transfer_amount": 15,
            "resulting_balance": 115,
            "transfer_time": "2025-08-25 21:49:59"
        }
    ]
}
```
