import csv
import gzip
import pickle
from typing import Any, Optional
import os
from pathlib import Path
import git
import pandas as pd
from tqdm import tqdm
from .datatypes import TestInfo

type DatasetRuns = list[tuple[str, list[TestInfo]]]


class Dataset:
    def __init__(self, *, runs_path: Path, repo_path: Path, rc_map: dict[str, str] | Path, cached: bool = True) -> None:
        self._runs_path = runs_path
        self._repo_path = repo_path
        self._rc_map = rc_map
        self._cached = cached

    @classmethod
    def preload_rc_map(cls, rc_map_path: Path) -> dict[str, str]:
        with open(rc_map_path) as f:
            reader = csv.reader(f)
            return {run_id: commit_id for run_id, commit_id in reader}

    @property
    def name(self) -> str:
        return self._runs_path.stem

    def describe(self) -> None:
        data = self.runs(debug=True)
        runs = len(data)
        fail = sum(1 for _, tis in data if any(ti.failures > 0 for ti in tis)) / runs
        tests = sum(len(tis) for _, tis in data) / runs
        name = self._runs_path.stem
        print(f"{name[:16]: >16}: {runs: >6} runs, {fail:>6.1%} fail, {tests:>6.1f} tests")

    def runs(self, *, debug: bool = False) -> DatasetRuns:
        if (data := self._load_pickle()) is not None:
            return data

        runs_dict: dict[str, list[dict[str, Any]]] = (
            pd.read_csv(self._runs_path)
            .rename(columns={"travisJobId": "run_id", "testName": "name"})
            .astype({"run_id": str})
            .sort_values(["run_id", "index"])
            .drop_duplicates(["run_id", "name"])
            .groupby("run_id", sort=False)
            .apply(
                lambda x: x[["name", "duration", "failures"]].to_dict("records"),
                include_groups=False,
            )
            .to_dict()
        )

        rc_map = self._rc_map if isinstance(self._rc_map, dict) else self.preload_rc_map(self._rc_map)

        repo = git.Repo(self._repo_path)

        result: DatasetRuns = []
        invalid_runs: list[str] = []
        invalid_commits: list[str] = []
        invalid_files: list[tuple[str, str]] = []
        for run_id, test_cases in tqdm(runs_dict.items(), desc="runs", leave=False, disable=not debug):
            commit_id = rc_map.get(run_id)
            if commit_id is None:
                invalid_runs.append(run_id)
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
                (
                    run_id,
                    [
                        TestInfo(
                            name=tc["name"],
                            content=tc["content"],
                            failures=tc["failures"],
                            duration_s=tc["duration"],
                        )
                        for tc in test_cases
                    ],
                )
            )

        if debug:
            if len(invalid_runs) > 0:
                print(
                    f"  INVALID RUN [{len(invalid_runs)}]: {invalid_runs[:5]}{'...' if len(invalid_runs) > 5 else ''}"
                )
            if len(invalid_commits) > 0:
                print(
                    f"  INVALID COMMIT [{len(invalid_commits)}]: {invalid_commits[:5]}{'...' if len(invalid_commits) > 5 else ''}"
                )
            if len(invalid_files) > 0:
                print(
                    f"  INVALID FILE [{len(invalid_files)}]: {invalid_files[:5]}{'...' if len(invalid_files) > 5 else ''}"
                )

        self._save_pickle(result)
        return result

    def _load_pickle(self) -> Optional[DatasetRuns]:
        if not self._cached:
            return None
        try:
            with gzip.open(f"{self._runs_path}.pkl_gz", "rb") as f:
                return pickle.load(f)
        except Exception:
            return None

    def _save_pickle(self, data: DatasetRuns) -> None:
        if not self._cached:
            return
        try:
            with gzip.open(f"{self._runs_path}.pkl_gz", "wb") as f:
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
