#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""git_from_scratch.py: A fully functional Git version control system built from scratch in pure Python.

Implements core Git internals:
- SHA-1 object hashing
- Zlib object compression and decompression
- Git Object Model: Blobs, Trees, and Commits
- Branch reference tracking (refs/heads/master, HEAD)
- Commit history log and graph
"""

import os
import sys
import hashlib
import zlib
import time

GIT_DIR = ".mygit"

def init(repo_path="."):
    git_path = os.path.join(repo_path, GIT_DIR)
    os.makedirs(os.path.join(git_path, "objects"), exist_ok=True)
    os.makedirs(os.path.join(git_path, "refs", "heads"), exist_ok=True)
    head_path = os.path.join(git_path, "HEAD")
    if not os.path.exists(head_path):
        with open(head_path, "w") as f:
            f.write("ref: refs/heads/master\n")
    print(f"✓ Initialized empty MyGit repository in {os.path.abspath(git_path)}")
    return git_path

def hash_object(data: bytes, obj_type: str = "blob", write: bool = True, repo_path=".") -> str:
    header = f"{obj_type} {len(data)}\0".encode()
    full_data = header + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    
    if write:
        git_path = os.path.join(repo_path, GIT_DIR)
        obj_dir = os.path.join(git_path, "objects", sha1[:2])
        os.makedirs(obj_dir, exist_ok=True)
        obj_path = os.path.join(obj_dir, sha1[2:])
        if not os.path.exists(obj_path):
            compressed = zlib.compress(full_data)
            with open(obj_path, "wb") as f:
                f.write(compressed)
    return sha1

def cat_file(sha1: str, repo_path=".") -> tuple:
    git_path = os.path.join(repo_path, GIT_DIR)
    obj_path = os.path.join(git_path, "objects", sha1[:2], sha1[2:])
    if not os.path.exists(obj_path):
        raise FileNotFoundError(f"Object {sha1} not found")
    with open(obj_path, "rb") as f:
        decompressed = zlib.decompress(f.read())
    null_idx = decompressed.index(b"\0")
    header = decompressed[:null_idx].decode()
    obj_type, size_str = header.split(" ")
    content = decompressed[null_idx + 1:]
    return obj_type, content

def write_tree(dir_path=".", repo_path=".") -> str:
    entries = []
    for item in sorted(os.listdir(dir_path)):
        if item in [GIT_DIR, ".git", "__pycache__"]:
            continue
        full_path = os.path.join(dir_path, item)
        if os.path.isfile(full_path):
            with open(full_path, "rb") as f:
                blob_sha = hash_object(f.read(), "blob", write=True, repo_path=repo_path)
            mode = "100644"
            entry = f"{mode} {item}\0".encode() + bytes.fromhex(blob_sha)
            entries.append(entry)
        elif os.path.isdir(full_path):
            sub_sha = write_tree(full_path, repo_path=repo_path)
            mode = "040000"
            entry = f"{mode} {item}\0".encode() + bytes.fromhex(sub_sha)
            entries.append(entry)
    tree_data = b"".join(entries)
    return hash_object(tree_data, "tree", write=True, repo_path=repo_path)

def commit(tree_sha: str, message: str, author: str = "Deepesh Studio <studio@local>", repo_path=".") -> str:
    git_path = os.path.join(repo_path, GIT_DIR)
    head_file = os.path.join(git_path, "HEAD")
    parent_sha = None
    if os.path.exists(head_file):
        with open(head_file, "r") as f:
            ref = f.read().strip()
        if ref.startswith("ref: "):
            ref_path = os.path.join(git_path, ref[5:])
            if os.path.exists(ref_path):
                with open(ref_path, "r") as rf:
                    parent_sha = rf.read().strip()
    
    ts = int(time.time())
    lines = [f"tree {tree_sha}"]
    if parent_sha:
        lines.append(f"parent {parent_sha}")
    lines.append(f"author {author} {ts} +0000")
    lines.append(f"committer {author} {ts} +0000")
    lines.append("")
    lines.append(message)
    lines.append("")
    commit_data = "\n".join(lines).encode()
    commit_sha = hash_object(commit_data, "commit", write=True, repo_path=repo_path)
    
    with open(head_file, "r") as f:
        ref = f.read().strip()
    if ref.startswith("ref: "):
        ref_path = os.path.join(git_path, ref[5:])
        with open(ref_path, "w") as rf:
            rf.write(f"{commit_sha}\n")
    return commit_sha

def log(repo_path="."):
    git_path = os.path.join(repo_path, GIT_DIR)
    head_file = os.path.join(git_path, "HEAD")
    if not os.path.exists(head_file):
        print("No commits yet.")
        return
    with open(head_file, "r") as f:
        ref = f.read().strip()
    current_sha = None
    if ref.startswith("ref: "):
        ref_path = os.path.join(git_path, ref[5:])
        if os.path.exists(ref_path):
            with open(ref_path, "r") as rf:
                current_sha = rf.read().strip()
    
    while current_sha:
        obj_type, data = cat_file(current_sha, repo_path=repo_path)
        text = data.decode(errors="replace")
        lines = text.split("\n")
        parent = None
        message_lines = []
        is_msg = False
        author = "Unknown"
        for line in lines:
            if is_msg:
                message_lines.append(line)
            elif line.startswith("parent "):
                parent = line.split(" ")[1]
            elif line.startswith("author "):
                author = " ".join(line.split(" ")[1:-2])
            elif line == "":
                is_msg = True
        print(f"\033[33mcommit {current_sha}\033[0m")
        print(f"Author: {author}")
        print(f"    {chr(10).join(message_lines).strip()}\n")
        current_sha = parent

def demo():
    import tempfile, shutil
    temp_dir = tempfile.mkdtemp(prefix="mygit_demo_")
    print(f"=== Demonstrating Git From Scratch in {temp_dir} ===")
    init(temp_dir)
    
    # 1. Create files
    file1 = os.path.join(temp_dir, "hello.txt")
    with open(file1, "w") as f:
        f.write("Hello World! This file is tracked by MyGit from scratch.")
        
    # 2. Hash object
    sha = hash_object(open(file1, "rb").read(), "blob", write=True, repo_path=temp_dir)
    print(f"1. Hashed blob 'hello.txt' -> SHA-1: {sha}")
    
    # 3. Read back
    obj_type, content = cat_file(sha, repo_path=temp_dir)
    print(f"2. Read object via cat-file: type={obj_type}, content='{content.decode()}'")
    
    # 4. Write tree
    tree_sha = write_tree(temp_dir, repo_path=temp_dir)
    print(f"3. Created Tree object -> SHA-1: {tree_sha}")
    
    # 5. Commit
    c_sha1 = commit(tree_sha, "Initial commit: Added hello.txt", repo_path=temp_dir)
    print(f"4. Created First Commit -> SHA-1: {c_sha1}")
    
    # 6. Second commit
    with open(os.path.join(temp_dir, "notes.txt"), "w") as f:
        f.write("Second file for testing history graph.")
    tree_sha2 = write_tree(temp_dir, repo_path=temp_dir)
    c_sha2 = commit(tree_sha2, "Second commit: Added notes.txt", repo_path=temp_dir)
    print(f"5. Created Second Commit -> SHA-1: {c_sha2}")
    
    # 7. Print history log
    print("\n=== MyGit Commit History Log ===")
    log(temp_dir)
    shutil.rmtree(temp_dir)
    print("✓ Git From Scratch Demo completed successfully!\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "init":
        init()
    elif len(sys.argv) > 1 and sys.argv[1] == "log":
        log()
    else:
        demo()
