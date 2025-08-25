DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS transfers;

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT,
    user_id INTEGER NOT NULL,
    balance INTEGER NOT NULL, -- In cents
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender INTEGER NOT NULL,
    receiver INTEGER NOT NULL,
    transfer_amount INTEGER NOT NULL,
    sender_resulting_balance INTEGER NOT NULL,
    receiver_resulting_balance INTEGER NOT NULL,
    transfer_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender) REFERENCES accounts(account_id),
    FOREIGN KEY(receiver) REFERENCES accounts(account_id)
);

/*
-- Create a couple users and accounts
INSERT INTO users (user_id, name) VALUES (1, "User 1");
INSERT INTO users (user_id, name) VALUES (2, "User 2");
INSERT INTO accounts (user_id, amount)
VALUES (1, 10000);
INSERT INTO accounts (user_id, amount);
VALUES (SELECT user_id FROM users WHERE name = "User 2", 10000);

-- come back to this later

-- Create a couple fake transactions
INSERT INTO transactions (sender, recipient, transaction_time)
VALUES()
*/