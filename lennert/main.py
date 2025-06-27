import asyncio
import sys


async def main():
    import space_typer as game
    await game.engine.play()

if __name__ == "__main__":
    if sys.platform != 'emscripten':
        asyncio.run(main())
