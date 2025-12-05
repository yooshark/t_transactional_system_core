import asyncio

import httpx

NUM_REQUESTS = 10


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


async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [do_request(client, i) for i in range(1, NUM_REQUESTS + 1)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, status, result in results:
            print(f"Request {i}: status={status}, result={result}")


if __name__ == "__main__":
    asyncio.run(main())
