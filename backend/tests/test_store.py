"""US-B1: atomic JSON artifacts and GET /experiments/{id}/artifacts/{name}."""

from fastapi.testclient import TestClient

from app.main import app
from app.store import experiment_dir, read_artifact, write_artifact


def test_atomic_write_five_files(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    eid = "exp_test"
    for name in ("experiment", "roster", "run_a", "run_b", "attribution"):
        write_artifact(eid, name, {"name": name}, root=tmp_path)
    folder = experiment_dir(eid, tmp_path)
    for name in ("experiment", "roster", "run_a", "run_b", "attribution"):
        assert (folder / f"{name}.json").is_file()
        assert read_artifact(eid, name, root=tmp_path)["name"] == name
    leftovers = list(folder.glob("*.json.*")) + list(folder.glob("tmp*"))
    assert leftovers == []


def test_get_artifact_experiment(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    write_artifact("exp_get", "experiment", {"product_name": "Acme Analytics"}, root=tmp_path)
    client = TestClient(app)
    response = client.get("/experiments/exp_get/artifacts/experiment")
    assert response.status_code == 200
    assert response.json()["product_name"] == "Acme Analytics"
