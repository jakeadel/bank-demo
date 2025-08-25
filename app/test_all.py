import pytest
from fastapi.testclient import TestClient

from .main import app, create_conn, get_balance, set_balance

client = TestClient(app)


def test_create_conn():
    generator = create_conn()
    conn = next(generator)
    cursor = conn.cursor()

    cursor.execute("SELECT 'test';")
    res = cursor.fetchone()
    assert res[0] == "test"

    with open("./db/schema.sql", 'r') as file:
        cursor.executescript(file.read())
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    res = cursor.fetchall()
    tables = set([table[0] for table in res])

    assert "users" in tables
    assert "accounts" in tables
    assert "transfers" in tables

    conn.commit()
    conn.close()


def test_create_user():
    res = client.post("/user", json={"username": "Test 1"})
    assert res.status_code == 200
    assert res.json() == {"user_id": 1, "username": "Test 1"}

    res = client.post("/user", json={"username": "Test 2"})
    assert res.status_code == 200
    assert res.json() == {"user_id": 2, "username": "Test 2"}


def test_create_account():
    bad_res = client.post(
        "/user/account",
        json={
            "user_id": 999, 
            "account_name": "Bad", 
            "balance": 10
        }
    )
    assert bad_res.status_code == 404

    res = client.post(
        "/user/account", 
        json={
            "user_id": 1, 
            "account_name": "My account", 
            "balance": 10
        }
    )
    assert res.status_code == 200
    assert res.json() == {
        "user_id": 1,
        "account_id": 1,
        "account_name": "My account",
        "balance": 10
    }

    res = client.post(
        "/user/account", 
        json={
            "user_id": 1, 
            "account_name": "#2 Account", 
            "balance": 2000
        }
    )
    assert res.status_code == 200
    assert res.json() == {
        "user_id": 1,
        "account_id": 2,
        "account_name": "#2 Account",
        "balance": 2000
    }


def test_transfer_funds():
    insufficient_res = client.post(
        "/transfer_funds",
        json={
            "sender_id": 1,
            "receiver_id": 2,
            "amount": 100
        }
    )
    assert insufficient_res.status_code == 422

    bad_user_res = client.post(
        "/transfer_funds",
        json={
            "sender_id": 999,
            "receiver_id": 2,
            "amount": 100
        }
    )
    assert bad_user_res.status_code == 404

    res = client.post(
        "/transfer_funds",
        json={
            "sender_id": 2,
            "receiver_id": 1,
            "amount": 200
        }
    )
    assert res.status_code == 200
    assert res.json() == {
        "transfer_id": 1,
        "sender_id": 2,
        "receiver_id": 1,
        "transfer_amount": 200,
        "sender_resulting_balance": 1800,
        "receiver_resulting_balance": 210
    }


def test_get_account_balance():
    account_dne_res = client.get("/user/account/balance?account_id=0")
    assert account_dne_res.status_code == 404

    res = client.get("/user/account/balance?account_id=1")
    assert res.status_code == 200
    assert res.json() == {"account_id": 1, "balance": 210}


def test_transfer_history():
    none_res = client.get("/user/transfer_history?account_id=0")
    none_res.status_code == 404

    res = client.get("/user/transfer_history?account_id=1")
    res.status_code == 200
    json = res.json()
    del json["transfers"][0]["transfer_time"]
    assert json == {
        "account_id": 1,
        "transfers": [
            {
                "transfer_id": 1,
                "account_role": "receiver",
                "sender_id": 2,
                "receiver_id": 1,
                "transfer_amount": 200,
                "resulting_balance": 210
            }
        ]
    }
