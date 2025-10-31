import asyncio, time
from app.config import READER_PATH, TCP_HOST, TCP_PORT, STREAM_RATE

async def send_mbo(reader_path, host, port, rate):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, reader_path, rate),
        host, port
    )
    print(f"TCP server started on {host}:{port}, streaming {reader_path}")
    async with server:
        await server.serve_forever()

async def handle_client(reader, writer, reader_path, rate):
    """Handle a connected receiver client and stream MBO data."""
    with open(reader_path, "rb") as f:
        start = time.time()
        sent = 0
        while chunk := f.readline():
            writer.write(chunk)
            print(f"Sending: {chunk.strip()}")
            sent += 1
            # simple rate limiter
            if sent % rate == 0:
                elapsed = time.time() - start
                if elapsed < 1:
                    await asyncio.sleep(1 - elapsed)
                start = time.time()
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    print("Finished streaming MBO data.")

if __name__ == "__main__":
    asyncio.run(
        send_mbo(
            reader_path=READER_PATH, 
            host=TCP_HOST, 
            port=TCP_PORT, 
            rate=STREAM_RATE
        )
    )