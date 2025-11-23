import pytest
from fastapi.testclient import TestClient
from raglint.dashboard.app import app
from raglint.dashboard import models
from raglint.dashboard.database import SessionLocal
from raglint.dashboard.app import get_current_user_from_cookie

@pytest.mark.asyncio
async def test_datasets_endpoints(test_db):
    # Mock User
    mock_user = models.User(id="test_id", email="test@example.com")
    
    # Override dependency
    app.dependency_overrides[get_current_user_from_cookie] = lambda: mock_user
    
    from raglint.dashboard.database import get_db, SessionLocal, engine
    print(f"DEBUG: Overrides: {app.dependency_overrides.keys()}")
    print(f"DEBUG: get_db in overrides: {get_db in app.dependency_overrides}")
    print(f"DEBUG: Engine URL: {engine.url}")
    
    try:
        with TestClient(app) as client:
            # 1. List Datasets (Empty)
            response = client.get("/datasets")
            assert response.status_code == 200
            assert "Datasets" in response.text
            
            # 2. Create Dataset (JSON)
            file_content = b'[{"query": "q1", "ground_truth": "a1"}, {"query": "q2", "ground_truth": "a2"}]'
            files = {"file": ("test.json", file_content, "application/json")}
            data = {"name": "Test Dataset", "description": "A test dataset"}
            
            response = client.post("/datasets", data=data, files=files, follow_redirects=False)
            assert response.status_code == 303
            
            # 3. Verify in DB
            async with SessionLocal() as session:
                from sqlalchemy import select
                result = await session.execute(select(models.Dataset).where(models.Dataset.name == "Test Dataset"))
                dataset = result.scalar_one()
                assert dataset is not None
                
                result = await session.execute(select(models.DatasetItem).where(models.DatasetItem.dataset_id == dataset.id))
                items = result.scalars().all()
                assert len(items) == 2
                
            # 4. View Detail
            response = client.get(f"/datasets/{dataset.id}")
            assert response.status_code == 200
            assert "Test Dataset" in response.text
            assert "q1" in response.text
            
    finally:
        app.dependency_overrides.clear()
