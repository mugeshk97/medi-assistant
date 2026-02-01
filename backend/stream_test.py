import asyncio
import httpx


async def test_stream():
    url = "http://localhost:8000/api/v1/chat"
    data = {
        "message": "Count to 5 quickly",
        "thread_id": "stream_test_1",
        "user_id": "user_123",
    }

    print(f"Connecting to {url}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, json=data) as response:
            print(f"Status: {response.status_code}")
            async for chunk in response.aiter_text():
                print(f"Chunk: {chunk}", end="|", flush=True)


if __name__ == "__main__":
    asyncio.run(test_stream())
