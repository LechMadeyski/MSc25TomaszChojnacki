import csv
import gzip
import pickle
from typing import Any, Optional
import os
from pathlib import Path
import git
import pandas as pd
from tqdm import tqdm
from .datatypes import Cycle, TestCase, TestInfo, VisibleTestResult


class Dataset:
    def __init__(
        self, *, cycles_path: Path, repo_path: Path, jc_map: dict[str, str] | Path, cached: bool = True
    ) -> None:
        self._cycles_path = cycles_path
        self._repo_path = repo_path
        self._jc_map = jc_map
        self._cached = cached

    @classmethod
    def preload_jc_map(cls, jc_map_path: Path) -> dict[str, str]:
        with open(jc_map_path) as f:
            reader = csv.reader(f)
            return {job_id: commit_id for job_id, commit_id in reader}

    @property
    def name(self) -> str:
        return self._cycles_path.stem

    def describe(self) -> None:
        data = self.cycles(debug=True)
        cycles = len(data)
        fail = sum(1 for c in data if any(ti.result.fails > 0 for ti in c.tests)) / cycles
        tests = sum(len(c.tests) for c in data) / cycles
        name = self._cycles_path.stem
        print(f"{name[:16]: >16}: {cycles: >6} cycles, {fail:>6.1%} fail, {tests:>6.1f} tests")

    def cycles(self, *, debug: bool = False) -> list[Cycle]:
        if (data := self._load_pickle()) is not None:
            return data

        jobs_dict: dict[str, list[dict[str, Any]]] = (
            pd.read_csv(self._cycles_path)
            .rename(columns={"travisJobId": "job_id", "testName": "name", "duration": "time_s", "failures": "fails"})
            .astype({"job_id": str})
            .sort_values(["job_id", "index"])
            .drop_duplicates(["job_id", "name"])
            .groupby("job_id", sort=False)
            .apply(
                lambda x: x[["name", "fails", "time_s"]].to_dict("records"),
                include_groups=False,
            )
            .to_dict()
        )

        jc_map = self._jc_map if isinstance(self._jc_map, dict) else self.preload_jc_map(self._jc_map)

        repo = git.Repo(self._repo_path)

        result: list[Cycle] = []
        invalid_jobs: list[str] = []
        invalid_commits: list[str] = []
        invalid_files: list[tuple[str, str]] = []
        for job_id, test_cases in tqdm(jobs_dict.items(), desc="cycles", leave=False, disable=not debug):
            commit_id = jc_map.get(job_id)
            if commit_id is None:
                invalid_jobs.append(job_id)
                continue
            try:
                repo.git.checkout(commit_id, force=True)
            except Exception:
                invalid_commits.append(commit_id)
                continue

            for tc in test_cases:
                tc["content"] = self._read_content(tc["name"])
                if tc["content"] is None:
                    invalid_files.append((commit_id, tc["name"]))
                    break
            if any(tc["content"] is None for tc in test_cases):
                continue

            result.append(
                Cycle(
                    job_id=job_id,
                    tests=[
                        TestInfo(
                            case=TestCase(tc["name"]),
                            content=tc["content"],
                            result=VisibleTestResult(fails=tc["fails"], time_s=max(tc["time_s"], 1e-9)),
                        )
                        for tc in test_cases
                    ],
                )
            )

        if debug:
            if invalid_jobs:
                print(
                    f"  INVALID JOB [{len(invalid_jobs)}]: {invalid_jobs[:5]}{'...' if len(invalid_jobs) > 5 else ''}"
                )
            if invalid_commits:
                print(
                    f"  INVALID COMMIT [{len(invalid_commits)}]: {invalid_commits[:5]}{'...' if len(invalid_commits) > 5 else ''}"
                )
            if invalid_files:
                print(
                    f"  INVALID FILE [{len(invalid_files)}]: {invalid_files[:5]}{'...' if len(invalid_files) > 5 else ''}"
                )

        self._save_pickle(result)
        return result

    def _load_pickle(self) -> Optional[list[Cycle]]:
        if not self._cached:
            return None
        try:
            with gzip.open(f"{self._cycles_path}.pkl_gz", "rb") as f:
                return pickle.load(f)
        except Exception:
            return None

    def _save_pickle(self, data: list[Cycle]) -> None:
        if not self._cached:
            return
        try:
            with gzip.open(f"{self._cycles_path}.pkl_gz", "wb") as f:
                pickle.dump(data, f)
        except Exception:
            pass

    def _read_content(self, name: str) -> Optional[str]:
        name = name.replace(".", "/") + ".java"
        paths = [os.path.join(self._repo_path, "src/test/java", name)]
        for d in os.listdir(self._repo_path):
            d = os.path.join(self._repo_path, d)
            if os.path.isdir(d):
                paths.append(os.path.join(d, "src/test/java", name))
        for path in paths:
            try:
                with open(path) as f:
                    return f.read()
            except Exception:
                pass
        return None
