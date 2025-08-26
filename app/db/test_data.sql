
-- Test data
INSERT INTO users (user_id, username) VALUES (1, "John");
INSERT INTO users (user_id, username) VALUES (2, "Paul");

INSERT INTO accounts (account_name, user_id, balance) VALUES ("John's checking", 1, 1000);
INSERT INTO accounts (account_name, user_id, balance) VALUES ("John's savings", 1, 100);
INSERT INTO accounts (account_name, user_id, balance) VALUES ("Paul's account", 2, 500);

INSERT INTO transfers(sender, receiver, transfer_amount, sender_resulting_balance, receiver_resulting_balance)
    VALUES (1, 3, 50, 1000, 500);
