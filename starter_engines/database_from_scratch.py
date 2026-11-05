#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""database_from_scratch.py: An Append-Only Log & In-Memory Indexed Key-Value Database built from scratch.

Implements core Database & Storage Engine internals:
- Append-Only Write-Ahead Log (WAL) persistence to disk
- In-memory byte-offset index (O(1) lookups like Bitcask/Redis AOF)
- Crash recovery (replaying WAL to reconstruct the index)
- Tombstone markers for soft deletes
- Log compaction (cleaning up stale keys)
- Simple SQL-like WHERE query interface
"""

import os
import sys
import json
import struct
import tempfile

class DatabaseFromScratch:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.index = {}  # key -> byte offset in db_file
        self._load_or_create()

    def _load_or_create(self):
        if not os.path.exists(self.db_file):
            open(self.db_file, "w").close()
            return
        
        # Replay WAL to rebuild index
        with open(self.db_file, "rb") as f:
            while True:
                offset = f.tell()
                len_bytes = f.read(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                record_len = struct.unpack(">I", len_bytes)[0]
                record_data = f.read(record_len)
                record = json.loads(record_data.decode("utf-8"))
                
                key = record["k"]
                if record["d"]:  # deleted / tombstone
                    self.index.pop(key, None)
                else:
                    self.index[key] = offset

    def set(self, key: str, value: any):
        record = json.dumps({"k": key, "v": value, "d": False}).encode("utf-8")
        with open(self.db_file, "ab") as f:
            offset = f.tell()
            f.write(struct.pack(">I", len(record)))
            f.write(record)
            f.flush()
        self.index[key] = offset

    def get(self, key: str):
        if key not in self.index:
            return None
        offset = self.index[key]
        with open(self.db_file, "rb") as f:
            f.seek(offset)
            record_len = struct.unpack(">I", f.read(4))[0]
            record = json.loads(f.read(record_len).decode("utf-8"))
            return record["v"]

    def delete(self, key: str):
        if key not in self.index:
            return False
        record = json.dumps({"k": key, "v": None, "d": True}).encode("utf-8")
        with open(self.db_file, "ab") as f:
            f.write(struct.pack(">I", len(record)))
            f.write(record)
            f.flush()
        del self.index[key]
        return True

    def query(self, **filters):
        results = []
        for key in list(self.index.keys()):
            val = self.get(key)
            if isinstance(val, dict):
                match = all(val.get(k) == v for k, v in filters.items())
                if match:
                    results.append({"_key": key, **val})
        return results

    def compact(self):
        compact_file = self.db_file + ".compact"
        new_index = {}
        with open(compact_file, "wb") as f_out:
            for key in sorted(self.index.keys()):
                val = self.get(key)
                record = json.dumps({"k": key, "v": val, "d": False}).encode("utf-8")
                offset = f_out.tell()
                f_out.write(struct.pack(">I", len(record)))
                f_out.write(record)
                new_index[key] = offset
        os.replace(compact_file, self.db_file)
        self.index = new_index

def demo():
    temp_dir = tempfile.mkdtemp(prefix="mydb_demo_")
    db_path = os.path.join(temp_dir, "studio_store.db")
    print(f"=== Demonstrating Database From Scratch at {db_path} ===")
    
    db = DatabaseFromScratch(db_path)
    
    # 1. Insert records
    print("\n1. Inserting records into WAL storage:")
    db.set("user:101", {"name": "Satyender", "role": "Director", "channel": "Deepesh Studio"})
    db.set("user:102", {"name": "Alex", "role": "Video Editor", "channel": "Vox Explainer"})
    db.set("user:103", {"name": "Sara", "role": "Motion Designer", "channel": "Deepesh Studio"})
    print("  ✓ Stored user:101, user:102, user:103 to append-only log.")
    
    # 2. Retrieve records via in-memory O(1) index
    print("\n2. Direct O(1) Index Lookup:")
    val = db.get("user:101")
    print(f"  db.get('user:101') -> {val}")
    
    # 3. Update record
    print("\n3. Updating user:102 (appends new record to log):")
    db.set("user:102", {"name": "Alex Rivera", "role": "Senior Editor", "channel": "Vox Explainer"})
    print(f"  db.get('user:102') -> {db.get('user:102')}")
    
    # 4. SQL-like query
    print("\n4. Filter Query (WHERE channel='Deepesh Studio'):")
    matches = db.query(channel="Deepesh Studio")
    for m in matches:
        print(f"  Found: {m['_key']} -> {m['name']} ({m['role']})")
        
    # 5. Crash Recovery Test
    print("\n5. Testing Crash Recovery (Re-opening database file from disk):")
    db_recovered = DatabaseFromScratch(db_path)
    print(f"  Rebuilt index entries: {len(db_recovered.index)}")
    print(f"  db_recovered.get('user:103') -> {db_recovered.get('user:103')}")
    
    # 6. Compaction
    size_before = os.path.getsize(db_path)
    db.compact()
    size_after = os.path.getsize(db_path)
    print(f"\n6. Log Compaction: {size_before} bytes -> {size_after} bytes (Stale keys purged)")
    
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ Database From Scratch Demo completed successfully!\n")

if __name__ == "__main__":
    demo()
