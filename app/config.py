import os

# ================================
# General Settings
# ================================
INSTRUMENT_DEFAULT = os.getenv("INSTRUMENT_DEFAULT", "CLX5")
SNAPSHOT_EVERY = int(os.getenv("SNAPSHOT_EVERY", "500"))
TOP_DEPTH = int(os.getenv("TOP_DEPTH", "10"))

# ================================
# File Paths
# ================================
OUTPUT_JSON = os.getenv("OUTPUT_JSON", "reconstructed_book.json")
DB_PATH = os.getenv("DB_PATH", "orderbook_snapshots.db")
READER_PATH = os.getenv("READER_PATH", "data/processed/CLX5_mbo.txt")

# ================================
# TCP Streaming
# ================================
TCP_HOST = os.getenv("TCP_HOST", "127.0.0.1")
TCP_PORT = int(os.getenv("TCP_PORT", "9999"))
STREAM_RATE = int(os.getenv("STREAM_RATE", "50000"))
