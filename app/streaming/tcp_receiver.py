import asyncio, json, os, time
from app.book.engine import OrderBook
from app.mbo.parser import parse_csv_line
from app.storage.sqlite_client import persist_snapshot, init_schema
from app.config import INSTRUMENT_DEFAULT, SNAPSHOT_EVERY, OUTPUT_JSON, TOP_DEPTH, TCP_HOST, TCP_PORT

async def receive_mbo(host, port):
    # Initialize SQLite schema
    init_schema()

    reader, writer = await asyncio.open_connection(host, port)
    book = OrderBook()

    # Read header first to get column index map
    header_line = await reader.readline()
    header_cols = [h.strip() for h in header_line.decode("utf-8").rstrip("\n").split(",")]
    header = {name: i for i, name in enumerate(header_cols)}

    # Debug: read and parse 5 sample lines to verify the parser output
    # for _ in range(5):
    #     line = await reader.readline()
    #     parsed = parse_csv_line(header, line.decode("utf-8"))
    #     print(parsed)
    
    # return 

    count = 0 
    last_snapshot = time.time()

    try:
        while True:
            line = await reader.readline()
            if not line:
                break

            # Parse one MBO record 
            evt = parse_csv_line(header, line.decode("utf-8"))
            if not evt:
                continue

            instrument = evt.get("instrument") or INSTRUMENT_DEFAULT
            ts = evt["ts"]
            act = evt["action"]

            # --- Order Book Logic ---
            if act == "ADD":
                book.on_add(evt["order_id"], evt["side"], evt["price"], evt["size"], evt["ts"])
            elif act == "MOD":
                book.on_modify(evt["order_id"], evt["price"], evt["size"], evt["ts"])
            elif act == "CXL":
                book.on_cancel(evt["order_id"])
            elif act == "TRD":
               book.on_trade(evt["order_id"], evt["size"], evt["ts"]) 
            elif act == "FILL":
                book.on_trade(evt["order_id"], evt["size"], evt["ts"])
            elif act == "CLR":
                book.clear()
            # ------------------------

            count += 1

            # periodic snapshot (by count or time)
            if count % SNAPSHOT_EVERY == 0 or (time.time() - last_snapshot >= 1.0):
                snap = book.to_json_obj(instrument, ts, depth=TOP_DEPTH)

                # Write atomically to JSON file
                tmp_file = OUTPUT_JSON + ".tmp"
                with open(tmp_file, "w") as f:
                    json.dump(snap, f, separators=(",", ":"))
                os.replace(tmp_file, OUTPUT_JSON)
                last_snapshot = time.time()

                # Persist snapshot to SQLite
                persist_snapshot(snap)

    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(receive_mbo(host=TCP_HOST, port=TCP_PORT))