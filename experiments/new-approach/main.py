import os
import random
from git import Repo
import pandas as pd
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

REPO_PATH = "./LittleProxy"
repo = Repo(REPO_PATH)

print("Loading dict...")
job_to_commit = pd.read_csv("tr_all_built_commits.csv")
job_to_commit = pd.Series(job_to_commit["git_commit_id"].values, index=job_to_commit["tr_job_id"]).to_dict()

print("Loading model...")
model = SentenceTransformer("Salesforce/SFR-Embedding-Code-400M_R", trust_remote_code=True)

print("Loading cases...")
df = pd.read_csv("adamfisk@LittleProxy.csv")
runs = df.groupby("travisJobId").apply(lambda x: x[["testName", "failures"]].to_dict("records"), include_groups=False).to_dict()

def apfd(ordering):
    n = len(ordering)
    m = 0
    s = 0
    for i, tc in enumerate(ordering):
        if tc["failures"] > 0:
            m += 1
            s += i + 1
    if m == 0:
        return float("nan")
    return 1 - (s / (n * m)) + (1 / (2 * n))

def dst(e1, e2):
    return 1 - abs(cos_sim(e1, e2))

def proposed(test_cases: list[dict]):
    for tc1 in test_cases:
        print(".", end="", flush=True)
        tc1["embedding"] = model.encode(tc1["content"][tc1["content"].find("class"):])
    # Find start
    start = max(test_cases, key=lambda tc: min(dst(tc["embedding"], tc2["embedding"]) for tc2 in test_cases if tc["testName"] != tc2["testName"]))
    prioritized = [start]
    queue = test_cases.copy()
    queue.remove(start)
    while queue:
        candidate = max(queue, key=lambda tc: min(dst(tc["embedding"], tc2["embedding"]) for tc2 in prioritized))
        prioritized.append(candidate)
        queue.remove(candidate)
    return prioritized

apfd_base = []
apfd_rand = []
apfd_prop = []
print("Calculating APFD...")
for run_id, test_cases in runs.items():
    if sum(tc["failures"] for tc in test_cases) == 0:
        continue
    if run_id not in job_to_commit:
        continue
    commit_id = job_to_commit[run_id]

    repo.git.checkout(commit_id)
    for tc in test_cases:
        path = f"{REPO_PATH}/src/test/java/{tc['testName'].replace('.', '/')}.java"
        if not os.path.exists(path):
            print(f"!!! Test case {tc['testName']} does not exist")
            continue
        with open(path, "r") as f:
            content = f.read()
            tc["content"] = content

    base_order = test_cases.copy()
    random_order = test_cases.copy()
    random.shuffle(random_order)
    proposed_order = proposed(test_cases.copy())
    apfd_base.append(apfd(base_order))
    apfd_rand.append(apfd(random_order))
    apfd_prop.append(apfd(proposed_order))
    print(f"Run ID: {run_id}, Commit ID: {commit_id}, APFD_base: {apfd(base_order):.3}, APFD_rand: {apfd(random_order):.3}, APFD_prop: {apfd(proposed_order):.3}")

print(f"APFD_base: {sum(apfd_base) / len(apfd_base):.3}, APFD_rand: {sum(apfd_rand) / len(apfd_rand):.3}, APFD_prop: {sum(apfd_prop) / len(apfd_prop):.3}")
