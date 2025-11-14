import aiohttp
import asyncio

async def test():
    url = "https://www3.septa.org/api/TrainView/index.php"

    fields = ["SOURCE", "dest", "orig_train", "next_station", "last_stop"]
    stations = set()

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()

            for train in data:
                for f in fields:
                    name = train.get(f)
                    if name:
                        stations.add(name)
        print("\n".join(sorted(stations)))




asyncio.run(test())