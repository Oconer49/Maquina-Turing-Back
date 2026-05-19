from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_machines():
    r = client.get("/api/v1/machines")
    assert r.status_code == 200
    ids = {m["id"] for m in r.json()}
    assert "even_zeros" in ids
    assert "binary_palindrome" in ids


def test_create_and_step():
    r = client.post("/api/v1/simulations", json={"machine_id": "even_zeros", "input": "1010"})
    assert r.status_code == 201
    sim_id = r.json()["simulation_id"]
    r2 = client.post(f"/api/v1/simulations/{sim_id}/step")
    assert r2.status_code == 200
    data = r2.json()
    assert "applied_transition" in data
    assert data["applied_transition"]["from"] == "q0"
    r3 = client.post(f"/api/v1/simulations/{sim_id}/run", json={"max_steps": 500})
    assert r3.status_code == 200
    assert r3.json()["final_status"] == "ACCEPTED"


def test_invalid_symbol_returns_400():
    r = client.post("/api/v1/simulations", json={"machine_id": "even_zeros", "input": "12"})
    assert r.status_code == 400


def test_step_after_finished_returns_409():
    r = client.post("/api/v1/simulations", json={"machine_id": "even_zeros", "input": ""})
    sim_id = r.json()["simulation_id"]
    client.post(f"/api/v1/simulations/{sim_id}/run", json={"max_steps": 50})
    r2 = client.post(f"/api/v1/simulations/{sim_id}/step")
    assert r2.status_code == 409


def test_machine_not_found():
    r = client.post("/api/v1/simulations", json={"machine_id": "no_existe", "input": "0"})
    assert r.status_code == 404
