#!/usr/bin/env python3
"""Fail when a NetworkPolicy podSelector matches no workload in the manifests.

Schema validation cannot catch a selector with a typo; such a policy is valid
but silently protects nothing.
"""
import pathlib
import sys

import yaml

MANIFEST_DIR = pathlib.Path(__file__).resolve().parent.parent / "manifests"


def load_docs():
    for path in sorted(MANIFEST_DIR.glob("*.yaml")):
        for doc in yaml.safe_load_all(path.read_text()):
            if doc:
                yield path.name, doc


def matches(selector, labels):
    return all(labels.get(k) == v for k, v in selector.get("matchLabels", {}).items())


def main():
    docs = list(load_docs())
    pod_labels = [
        d["spec"]["template"]["metadata"]["labels"]
        for _, d in docs
        if d["kind"] == "Deployment"
    ]
    errors = []
    for fname, doc in docs:
        if doc["kind"] != "NetworkPolicy":
            continue
        selector = doc["spec"]["podSelector"]
        if not selector:
            continue  # empty selector intentionally selects every pod
        if not any(matches(selector, labels) for labels in pod_labels):
            errors.append(f"{fname}: policy {doc['metadata']['name']} selects no pods: {selector}")
    for err in errors:
        print(err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
