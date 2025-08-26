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

-- Test data
INSERT INTO users (user_id, username) VALUES (1, "John");
INSERT INTO users (user_id, username) VALUES (2, "Paul");

INSERT INTO accounts (account_name, user_id, balance) VALUES ("John's checking", 1, 1000);
INSERT INTO accounts (account_name, user_id, balance) VALUES ("John's savings", 1, 100);
INSERT INTO accounts (account_name, user_id, balance) VALUES ("Paul's account", 2, 500);

INSERT INTO transfers(sender, receiver, transfer_amount, sender_resulting_balance, receiver_resulting_balance)
    VALUES (1, 3, 50, 1000, 500);
