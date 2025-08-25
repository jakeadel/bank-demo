


Install instructions:
    - pip3 install "fastapi[standard]"
    - requirements.txt

Run with: fastapi dev main.py

Extensions:
    - support multiple currencies
        - include currency parameter to transfer_money endpoint
        - convert function
    - Make more distributed
    - Would probably want to disallow duplicate account names per user

    - User uuid for user_id and account_id for security
        - Or just use jwt tokens to identify them from the frontend
        - jwt would contain user_id when decoded

Maybe split routes into user/account, user/account/balance user/account/transactions or something

Need to write tests!

Write a little spec
