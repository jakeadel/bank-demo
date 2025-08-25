# Bank Demo App


## Install instructions:
    - pip3 install "fastapi[standard]"
    - requirements.txt
    - Run tests: pytest /app

Run with: fastapi dev main.py

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

Error codes:
    - 400: blank username
    - 500: unknown error

### Create Account
Request:
```json
{"account_name": "account_123", "user_id": 1, "balance": 100}
```
Note: balance is in Cents

Response:
```json
{"account_id": 1, "account_name": "account_123", "user_id": 1, "balance": 100}
```

