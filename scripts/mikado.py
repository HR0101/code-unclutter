#!/usr/bin/env python3
"""
scripts/mikado.py - Mikado Method Dependency Tracker for code-unclutter (No.98)
Maintains a goal-oriented dependency graph for architectural refactorings.
"""

import argparse
import json
from pathlib import Path

MIKADO_FILE = Path(".mikado_graph.json")


def load_graph():
    if MIKADO_FILE.exists():
        with open(MIKADO_FILE) as f:
            return json.load(f)
    return {"goal": "", "nodes": {}}


def save_graph(data):
    with open(MIKADO_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_goal(goal_text):
    data = load_graph()
    data["goal"] = goal_text
    data["nodes"] = {"root": {"title": goal_text, "status": "pending", "prerequisites": []}}
    save_graph(data)
    print(f"[GOAL] Mikado Goal Set: {goal_text}")


def add_prerequisite(parent_id, task_title):
    data = load_graph()
    if parent_id not in data["nodes"]:
        print(f"[NG] Parent node '{parent_id}' not found.")
        return

    node_id = f"task_{len(data['nodes'])}"
    data["nodes"][node_id] = {
        "title": task_title,
        "status": "pending",
        "parent": parent_id,
        "prerequisites": []
    }
    data["nodes"][parent_id]["prerequisites"].append(node_id)
    save_graph(data)
    print(f"[+] Added prerequisite '{node_id}': {task_title} (blocks '{parent_id}')")


def complete_task(task_id):
    data = load_graph()
    if task_id in data["nodes"]:
        data["nodes"][task_id]["status"] = "done"
        save_graph(data)
        print(f"[OK] Completed task '{task_id}'.")
    else:
        print(f"[NG] Task '{task_id}' not found.")


def show_tree():
    data = load_graph()
    if not data["goal"]:
        print("No active Mikado graph. Initialize with: mikado.py goal '<target>'")
        return

    print(f"[TREE] Mikado Graph: {data['goal']}")

    def print_node(node_id, indent=0):
        node = data["nodes"].get(node_id)
        if not node:
            return
        status_icon = "[OK]" if node["status"] == "done" else "[PENDING]"
        print(f"{'  ' * indent}{status_icon} [{node_id}] {node['title']}")
        for child in node.get("prerequisites", []):
            print_node(child, indent + 1)

    print_node("root")


def main():
    parser = argparse.ArgumentParser(description="Mikado Method CLI")
    sub = parser.add_subparsers(dest="command")

    g_p = sub.add_parser("goal")
    g_p.add_argument("text", help="Ultimate refactoring objective")

    a_p = sub.add_parser("add")
    a_p.add_argument("parent", help="Parent task ID that requires this prerequisite")
    a_p.add_argument("text", help="Prerequisite task description")

    c_p = sub.add_parser("done")
    c_p.add_argument("id", help="Task ID completed")

    sub.add_parser("status")

    args = parser.parse_args()

    if args.command == "goal":
        set_goal(args.text)
    elif args.command == "add":
        add_prerequisite(args.parent, args.text)
    elif args.command == "done":
        complete_task(args.id)
    elif args.command == "status":
        show_tree()
    else:
        show_tree()


if __name__ == "__main__":
    main()
