# Bank Demo App

## Table of Contents
- [Backend Install Instructions](#backend-install-instructions)
- [Frontend Install Instructions](#frontend-install-instructions)
- [Run the Backend locally](#run-the-backend-locally)
- [Demo Data](#demo-data)
- [Run backend tests](#run-backend-tests)
- [Run the Web App locally](#run-the-web-app-locally)
- [Improvements](#improvements)
- [API Reference](#api-reference)
  - [Create User](#create-user)
  - [Create Account](#create-account)
  - [Transfer Funds](#transfer-funds)
  - [Get Account Balance](#get-account-balance)
  - [Get Account Transfer History](#get-account-transfer-history)
  - [Get Users](#get-users)

## Backend Install Instructions:
    - pip install -r requirements.txt

## Frontend Install Instructions:
From within the `/frontend` directory:
```bash
npm install
```

### Run the Backend locally
From within the `/app` directory:
```bash
fastapi dev main.py
```

The backend will run at http://localhost:8000 by default.

### Demo Data
Some users, accounts, and transfers are preloaded in schema.sql. schema.sql is executed on server startup in the init_db() function.
- John (user_id=1)
    - account_name="John's checking", account_id=1, balance=1000 ($10)
    - account_name="John's savings", account_id=2, balance=100 ($1)
- Paul (user_id=2) has accont_name="Paul's account", account_id=3, balance=500 ($5)
- Example transfer: John transfers 50 ($0.50) to Paul

### Run Backend Integration tests
From within the `/app` directory:
```bash
pytest
```

### Run the Web App locally
From within the `/frontend` directory:
```bash
npm run dev
```

The web app will run at http://localhost:5173 by default

The web app is setup to hit http://localhost:8000 for the backend endpoints. To change the target URL, set the VITE_ROOT_URL variable in `.env.local` (dev) or `.env.production` (prod)

## Improvement Areas:
    - Add authentication, use JWTs
    - More structured logging instead of using print statements
    - Build out further endpoints
        - PUT, DELETE for users, accounts, transfers
        - GET for users/{user_id}, accounts/{account_id}
    - Hold common repeated requests in an in-memory data structure on server
        - get balance
        - get transfers per account
    - Use error codes for better frontend error messages

# API Reference

### Note: All money values are stored as cents but displayed as dollars

### Create User
**POST** `/users`

Request:
```json
{
    "username": "user_123"
}
```

```bash
curl --location 'http://localhost:8000/users' \
--header 'Content-Type: application/json' \
--data '{
   "username": "user_123"
}'
```

Response:
```json
{
    "user_id": 1, 
    "username": "user_123"
}
```

**Error Codes:**
- 422: Missing required field (Handled by Pydantic validation)
- 400: Blank username
- 500: Unknown error

### Create Account
**POST** /accounts

Request:
```json
{
    "account_name": "account_123", 
    "user_id": 1, 
    "balance": 100
}
```

```bash
curl --location 'http://localhost:8000/accounts' \
--header 'Content-Type: application/json' \
--data '{
    "account_name": "account_123",
    "user_id": 1,
    "balance": 100
}'
```

Response:
```json
{
    "account_id": 1, 
    "account_name": "account_123", 
    "user_id": 1, 
    "balance": 100
}
```

**Error Codes:**
- 422: Missing required field (Handled by Pydantic validation)
- 400: Negative input balance
- 404: Unable to find input user
- 409: Duplicate account name
- 500: Unknown error

### Transfer Funds
**POST** /transfers

Request:
```json
{
    "sender_id": 1, 
    "receiver_id": 2, 
    "transfer_amount": 100
}
```

Note: sender_id and receiver_id are account_ids

```bash
curl --location 'http://localhost:8000/transfers' \
--header 'Content-Type: application/json' \
--data '{
    "sender_id": 1,
    "receiver_id": 2,
    "transfer_amount": 100
}'
```

Response:
```json
{
    "transfer_id": 1, 
    "sender_id": 1, 
    "receiver_id": 2, 
    "transfer_amount": 100, 
    "sender_resulting_balance": 100, 
    "receiver_resulting_balance": 200
}
```

**Error Codes:**
- 422: Missing required field (Handled by Pydantic validation)
- 400: Sender_id and receiver_id are the same or sender lacks requisite funds
- 404: Sender or receiver account not found
- 500: Unknown error

### Get Account Balance
**GET** /accounts/{account_id}/balance

```bash
curl --location 'http://localhost:8000/accounts/1/balance'
```

Response:
```json
{
    "account_id": 1,
    "balance": 100
}
```

**Error Codes:**
- 422: Missing required field (Handled by Pydantic validation)
- 404: Unable to find account
- 500: Unknown error

### Get Account Transfer History
**GET** /accounts/{account_id}/transfer_history

```bash
curl --location 'http://localhost:8000/accounts/1/transfer_history'
```

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

**Error Codes:**
- 422: Missing required field (Handled by Pydantic validation)
- 404: Unable to find account
- 500: Unkown error

### Get Users
**GET** /users

```bash
curl --location 'http://localhost:8000/users'
```

Response:
```json
[
    {
        "user_id": 1,
        "username": "John",
        "accounts": [
            {
                "account_id": 1,
                "account_name": "John's checking",
                "balance": 1000
            }
        ]
    }
]
```

**Error Codes:**
- 500: Unknown error
