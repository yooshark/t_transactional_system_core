import asyncio

import httpx


async def do_request(client: httpx.AsyncClient, i: int):
    try:
        r = await client.post(
            "http://127.0.0.1:8000/api/transfer/",
            json={"from_wallet_id": 2, "to_wallet_id": 3, "amount": "2000.00"},
        )
        r.raise_for_status()
        return i, r.status_code, r.json()
    except httpx.HTTPStatusError as e:
        return i, e.response.status_code, e.response.text
    except httpx.RequestError as e:
        return i, None, str(e)


async def main(num_requests: int = 10):
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [do_request(client, i) for i in range(1, num_requests + 1)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, status, result in results:
            print(f"Request {i}: status={status}, result={result}")


if __name__ == "__main__":
    NUM_REQUESTS = 10

    asyncio.run(main(NUM_REQUESTS))
