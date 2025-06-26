import asyncio
import sys


async def main():
    import barcode_blitz
    await barcode_blitz.engine.play()


if __name__ == "__main__":
    if sys.platform != 'emscripten':
        asyncio.run(main())
