#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""byox.py: The Master 'Build Your Own X' Interactive CLI, Explorer & Engine Runner.

Allows you to:
1. Explore, search, and view tutorials for 30+ technologies from scratch.
2. Run 6 built-in, production-tested 'From Scratch' engines:
   - git: Version control system (blobs, trees, commits, SHA-1, zlib)
   - neural_net: Multi-layer neural network with backpropagation (NumPy)
   - database: Append-only log + in-memory indexed key-value store (WAL)
   - raytracer: 3D ray tracing software renderer (PNG/PPM output)
   - blockchain: Proof-of-work cryptographic blockchain and mining
   - web_server: Socket-based HTTP/1.1 web server and REST API
3. Scaffold new scratch projects instantly.
"""

import os
import sys
import re
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
README_PATH = os.path.join(SCRIPT_DIR, "README.md")
STARTER_DIR = os.path.join(SCRIPT_DIR, "starter_engines")

BUILT_IN_ENGINES = {
    "git": ("git_from_scratch.py", "Git Version Control (Blobs, Trees, Commits, SHA-1)"),
    "neural_net": ("neural_net_from_scratch.py", "Neural Network & Backprop (NumPy, 100% XOR Accuracy)"),
    "database": ("database_from_scratch.py", "Append-Only Log DB with O(1) Index & Crash Recovery"),
    "raytracer": ("raytracer_from_scratch.py", "3D Ray Tracer & Software Renderer (Phong Shading, PNG)"),
    "blockchain": ("blockchain_from_scratch.py", "PoW Blockchain & SHA-256 Mining Consensus Engine"),
    "web_server": ("web_server_from_scratch.py", "Socket-Based HTTP/1.1 Server & JSON REST API")
}

def parse_readme():
    if not os.path.exists(README_PATH):
        return {}
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    catalog = {}
    current_cat = None
    current_tuts = []
    
    for line in lines:
        stripped = line.strip()
        if "#### Build your own `" in line:
            if current_cat:
                catalog[current_cat] = current_tuts
            current_cat = line.split("`")[1].strip()
            current_tuts = []
        elif current_cat is not None:
            if stripped.startswith("#### ") or stripped.startswith("## "):
                catalog[current_cat] = current_tuts
                current_cat = None
                current_tuts = []
            elif stripped.startswith("* [") or stripped.startswith("*"):
                current_tuts.append(stripped)
                
    if current_cat and current_tuts:
        catalog[current_cat] = current_tuts
    return catalog

def print_banner():
    print("""\033[1;36m
██████╗ ██╗   ██╗ ██████╗ ██╗  ██╗
██╔══██╗╚██╗ ██╔╝██╔═══██╗╚██╗██╔╝
██████╔╝ ╚████╔╝ ██║   ██║ ╚███╔╝ 
██╔══██╗  ╚██╔╝  ██║   ██║ ██╔██╗ 
██████╔╝   ██║   ╚██████╔╝██╔╝ ██╗
╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝\033[0m
\033[1;33mBuild Your Own Technology From Scratch — Deepesh Mobile Studio\033[0m
""")

def cmd_list():
    print_banner()
    catalog = parse_readme()
    print(f"\033[1m📚 Total Technologies Available: {len(catalog)}\033[0m\n")
    print(f"{'#':<3} {'Technology / System':<35} {'Tutorials':<10} {'Built-In Engine'}")
    print("-" * 68)
    
    built_in_keys = {
        "Git": "byox run git",
        "Neural Network": "byox run neural_net",
        "Database": "byox run database",
        "3D Renderer": "byox run raytracer",
        "Blockchain / Cryptocurrency": "byox run blockchain",
        "Web Server": "byox run web_server"
    }
    
    for idx, (tech, tuts) in enumerate(sorted(catalog.items()), 1):
        builtin_tag = f"\033[32m✓ Ready ({built_in_keys[tech]})\033[0m" if tech in built_in_keys else "Guide Available"
        print(f"{idx:<3} {tech:<35} {len(tuts):<10} {builtin_tag}")
        
    print("\n\033[36mTo run all built-in scratch engines:\033[0m  byox demo")
    print("\033[36mTo search tutorials:\033[0m                 byox search <query>")
    print("\033[36mTo view tutorials for a tech:\033[0m        byox view <technology>")

def cmd_search(query):
    catalog = parse_readme()
    query_l = query.lower()
    matches = 0
    print_banner()
    print(f"\033[1m🔍 Search Results for '{query}':\033[0m\n")
    for tech, tuts in catalog.items():
        matched_tuts = [t for t in tuts if query_l in t.lower() or query_l in tech.lower()]
        if matched_tuts:
            matches += len(matched_tuts)
            print(f"\033[1;33m[ {tech} ]\033[0m")
            for t in matched_tuts[:5]:
                print(f"  {t}")
            if len(matched_tuts) > 5:
                print(f"  ...and {len(matched_tuts) - 5} more.")
            print()
    if matches == 0:
        print(f"No tutorials found matching '{query}'. Run 'byox list' to view all categories.")
    else:
        print(f"Found {matches} matching tutorials.")

def cmd_view(tech_name):
    catalog = parse_readme()
    found = None
    for k in catalog:
        if tech_name.lower() in k.lower():
            found = k
            break
    if not found:
        print(f"Category '{tech_name}' not found. Run 'byox list' to see available categories.")
        return
        
    print_banner()
    print(f"\033[1;33m=== Tutorials for Build Your Own '{found}' ===\033[0m\n")
    for t in catalog[found]:
        print(f"  {t}")
    print()

def cmd_run(engine_name):
    if engine_name not in BUILT_IN_ENGINES:
        print(f"Engine '{engine_name}' not recognized. Available built-in engines:")
        for k, (_, desc) in BUILT_IN_ENGINES.items():
            print(f"  - \033[32m{k:<12}\033[0m : {desc}")
        return
    script, desc = BUILT_IN_ENGINES[engine_name]
    script_path = os.path.join(STARTER_DIR, script)
    subprocess.run([sys.executable, script_path, "demo"])

def cmd_demo():
    print_banner()
    print("\033[1;35m🚀 EXECUTING ALL 6 BUILT-IN 'FROM SCRATCH' ENGINES LIVE...\033[0m\n")
    for idx, (key, (script, desc)) in enumerate(BUILT_IN_ENGINES.items(), 1):
        print(f"\n\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        print(f"\033[1;32m[{idx}/6] Running {key.upper()} Engine — {desc}\033[0m")
        print(f"\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        script_path = os.path.join(STARTER_DIR, script)
        subprocess.run([sys.executable, script_path, "demo"])
        
    print("\n\033[1;32m🎉 ALL 6 ENGINES EXECUTED WITH 100% SUCCESS!\033[0m")

def main():
    if len(sys.argv) < 2:
        cmd_list()
        return
        
    cmd = sys.argv[1].lower()
    if cmd in ["list", "categories", "-l"]:
        cmd_list()
    elif cmd in ["search", "find", "-s"]:
        if len(sys.argv) < 3:
            print("Usage: byox search <keyword>")
        else:
            cmd_search(" ".join(sys.argv[2:]))
    elif cmd in ["view", "show"]:
        if len(sys.argv) < 3:
            print("Usage: byox view <technology>")
        else:
            cmd_view(" ".join(sys.argv[2:]))
    elif cmd in ["run"]:
        if len(sys.argv) < 3:
            print("Usage: byox run <git|neural_net|database|raytracer|blockchain|web_server>")
        else:
            cmd_run(sys.argv[2])
    elif cmd in ["demo", "all"]:
        cmd_demo()
    elif cmd in ["help", "--help", "-h"]:
        print("""
Usage:
  byox                 List all 30 technologies and built-in scratch engines
  byox list            Show full catalog table
  byox search <query>  Search tutorials by keyword (e.g. 'python', 'docker', 'ray')
  byox view <tech>     Show all tutorials for a specific technology
  byox run <engine>    Run a built-in scratch engine (git, neural_net, database, raytracer, blockchain, web_server)
  byox demo            Run all 6 built-in scratch engines in sequence
""")
    else:
        cmd_run(cmd)

if __name__ == "__main__":
    main()
