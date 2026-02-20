import asyncio
import uvicorn

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def run() -> None:
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
    server = uvicorn.Server(config=config)
    tasks = (asyncio.create_task(server.serve()),)

    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


@app.get("/")
async def root():
    return {"message": "Hello World"}
