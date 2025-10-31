🏦 Batonics Technical Assessment

## Overview

A lightweight real-time order book reconstruction system.
It streams Market-By-Order (MBO) data over TCP, rebuilds the book, and saves periodic snapshots to SQLite for analysis or visualization.

## Features

1. Real-time TCP streaming (sender + receiver)
2. Order book updates (add / modify / cancel / trade)
3. Periodic top-depth snapshots
4. SQLite persistence (self-contained)
5. Configurable via environment variables

## Project Structure

app/
 ├── book/engine.py           # Order book logic
 ├── mbo/parser.py            # CSV line parser
 ├── storage/sqlite_client.py # SQLite persistence
 ├── streaming/tcp_sender.py  # Sends MBO stream
 ├── streaming/tcp_receiver.py# Receives + saves snapshots
 └── config.py                # Configuration
data/
 ├── raw/CLX5_mbo.dbn
 └── processed/CLX5_mbo.txt
convert_dbn_to_text.py        # Converts .dbn to .txt
requirements.txt


## Quick Start
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start TCP sender (simulated exchange feed)
python -m app.streaming.tcp_sender

# 4. Start TCP receiver (reconstructs + stores)
python -m app.streaming.tcp_receiver

## Config (from app/config.py)

| Variable         | Default                 | Description        |
| ---------------- | ----------------------- | ------------------ |
| `TCP_HOST`       | 127.0.0.1               | TCP host           |
| `TCP_PORT`       | 9999                    | TCP port           |
| `SNAPSHOT_EVERY` | 500                     | Snapshot frequency |
| `DB_PATH`        | orderbook_snapshots.db  | SQLite database    |
| `OUTPUT_JSON`    | reconstructed_book.json | JSON snapshot file |

## Console:

Inserted snapshot at ts=1758718526.281799

## JSON Snapshot (reconstructed_book.json):

{"instrument":"CLX5","ts":1758718526.281799,
 "bids":[[66.65,18.0],[66.45,18.0],...],
 "asks":[[64.82,2.0],[64.83,3.0],...]}

## View Data in SQLite

sqlite3 orderbook_snapshots.db
.headers on
.mode column
SELECT COUNT(*), MAX(ts) FROM orderbook_snapshots;
.exit