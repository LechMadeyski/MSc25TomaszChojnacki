import csv
from typing import Any, Generator, Optional
import os
from pathlib import Path
import git
import pandas as pd
from .datatypes import TestInfo


class Dataset:
    def __init__(self, *, runs_path: Path, repo_path: Path, rc_map: dict[str, str] | Path) -> None:
        self._run_dict: dict[str, list[dict[str, Any]]] = (
            pd.read_csv(runs_path)
            .rename(columns={"travisJobId": "run_id", "testName": "name"})
            .sort_values(["run_id", "index"])
            .astype({"run_id": str})
            .drop_duplicates(["run_id", "name"])
            .groupby("run_id", sort=False)
            .apply(
                lambda x: x[["name", "duration", "failures"]].to_dict("records"),
                include_groups=False,
            )
            .to_dict()
        )

        self._repo_path = repo_path
        self._repo = git.Repo(repo_path)

        if isinstance(rc_map, dict):
            self._rc_map = rc_map
        elif isinstance(rc_map, Path):
            self._rc_map = self.preload_rc_map(rc_map)
        else:
            raise ValueError

    @classmethod
    def preload_rc_map(cls, rc_map_path: Path) -> dict[str, str]:
        with open(rc_map_path) as f:
            reader = csv.reader(f)
            return {run_id: commit_id for run_id, commit_id in reader}

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
            except:
                pass
        return None

    def runs(self) -> Generator[tuple[str, list[TestInfo]], None, None]:
        for run_id, test_cases in self._run_dict.items():
            if len(test_cases) == 0:
                continue
            commit_id = self._rc_map.get(run_id)
            if commit_id is None:
                continue
            try:
                self._repo.git.checkout(commit_id, force=True)
            except:
                continue

            for tc in test_cases:
                tc["content"] = self._read_content(tc["name"])
                if tc["content"] is None:
                    break
            if any(tc["content"] is None for tc in test_cases):
                continue

            yield (
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
