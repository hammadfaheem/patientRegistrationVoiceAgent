VALID = dict(
    first_name="Jane",
    last_name="Doe",
    date_of_birth="1990-03-03",
    sex="Female",
    phone_number="(555) 123-4567",
    address_line_1="123 Main St",
    city="Springfield",
    state="il",
    zip_code="62704",
)


async def test_create_patient_returns_201_and_envelope(client):
    resp = await client.post("/patients", json=VALID)
    assert resp.status_code == 201
    body = resp.json()
    assert body["error"] is None
    assert body["data"]["last_name"] == "Doe"
    assert body["data"]["state"] == "IL"
    assert "patient_id" in body["data"]


async def test_create_patient_with_invalid_state_returns_422(client):
    resp = await client.post("/patients", json={**VALID, "state": "ZZ"})
    assert resp.status_code == 422
    assert resp.json()["data"] is None
    assert resp.json()["error"] is not None


async def test_get_patient_by_id_round_trips(client):
    created = (await client.post("/patients", json=VALID)).json()["data"]
    resp = await client.get(f"/patients/{created['patient_id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["patient_id"] == created["patient_id"]


async def test_get_missing_patient_returns_404_envelope(client):
    resp = await client.get("/patients/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json() == {"data": None, "error": "patient 00000000-0000-0000-0000-000000000000 not found"}


async def test_list_patients_filters_by_phone_number(client):
    await client.post("/patients", json=VALID)
    await client.post("/patients", json={**VALID, "last_name": "Smith", "phone_number": "5559998888"})

    resp = await client.get("/patients", params={"phone_number": "555-123-4567"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["last_name"] == "Doe"


async def test_put_patient_partial_update(client):
    created = (await client.post("/patients", json=VALID)).json()["data"]
    resp = await client.put(f"/patients/{created['patient_id']}", json={"city": "Chicago"})
    assert resp.status_code == 200
    assert resp.json()["data"]["city"] == "Chicago"
    assert resp.json()["data"]["last_name"] == "Doe"


async def test_delete_patient_soft_deletes_and_hides_from_list(client):
    created = (await client.post("/patients", json=VALID)).json()["data"]
    resp = await client.delete(f"/patients/{created['patient_id']}")
    assert resp.status_code == 200
    assert resp.json() == {"data": None, "error": None}

    follow_up = await client.get(f"/patients/{created['patient_id']}")
    assert follow_up.status_code == 404
