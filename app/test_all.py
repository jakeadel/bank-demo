import pytest
from fastapi.testclient import TestClient

from .main import app, create_conn 

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
    res = client.post("/users", json={"username": "Test 1"})
    assert res.status_code == 200
    assert res.json() == {"user_id": 1, "username": "Test 1"}

    res = client.post("/users", json={"username": "Test 2"})
    assert res.status_code == 200
    assert res.json() == {"user_id": 2, "username": "Test 2"}


def test_create_account():
    bad_res = client.post(
        "/accounts",
        json={
            "user_id": 999, 
            "account_name": "Bad", 
            "balance": 10
        }
    )
    assert bad_res.status_code == 404

    res = client.post(
        "/accounts", 
        json={
            "user_id": 1,
            "account_name": "My account", 
            "balance": 10
        }
    )
    print("HERE", res.json())
    assert res.status_code == 200
    assert res.json() == {
        "user_id": 1,
        "account_id": 1,
        "account_name": "My account",
        "balance": 10
    }

    res = client.post(
        "/accounts", 
        json={
            "user_id": 1, 
            "account_name": "#2 account", 
            "balance": 2000
        }
    )
    assert res.status_code == 200
    assert res.json() == {
        "user_id": 1,
        "account_id": 2,
        "account_name": "#2 account",
        "balance": 2000
    }


def test_transfer_funds():
    insufficient_res = client.post(
        "/transfers",
        json={
            "sender_id": 1,
            "receiver_id": 2,
            "transfer_amount": 100
        }
    )
    assert insufficient_res.status_code == 400

    bad_user_res = client.post(
        "/transfers",
        json={
            "sender_id": 999,
            "receiver_id": 2,
            "transfer_amount": 100
        }
    )
    assert bad_user_res.status_code == 404

    res = client.post(
        "/transfers",
        json={
            "sender_id": 2,
            "receiver_id": 1,
            "transfer_amount": 200
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
    account_dne_res = client.get("/accounts/0/balance")
    assert account_dne_res.status_code == 404

    res = client.get("/accounts/1/balance")
    assert res.status_code == 200
    assert res.json() == {"account_id": 1, "balance": 210}


def test_transfer_history():
    none_res = client.get("/accounts/0/transfer_history")
    none_res.status_code == 404

    res = client.get("/accounts/1/transfer_history")
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
