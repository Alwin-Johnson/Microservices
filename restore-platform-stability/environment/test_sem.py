import asyncio
sem = asyncio.Semaphore(5)

async def main():
    async with sem:
        print("Acquired!")

asyncio.run(main())
