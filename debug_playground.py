import asyncio
from raglint.dashboard.app import playground_analyze
from raglint.dashboard.models import User
from fastapi import Request
from unittest.mock import MagicMock

async def test_endpoint():
    # Mock request
    request = MagicMock(spec=Request)
    
    # Mock user
    user = User(id="test", email="test@example.com", hashed_password="hash")
    
    print("Calling playground_analyze...")
    try:
        response = await playground_analyze(
            request=request,
            query="What is RAG?",
            contexts="RAG is Retrieval Augmented Generation.",
            response="RAG stands for Retrieval Augmented Generation.",
            user=user
        )
        print("Success!")
        print(response.body.decode())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
