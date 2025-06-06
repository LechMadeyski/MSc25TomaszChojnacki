import csv
import gzip
import pickle
import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, NamedTuple

import git
import pandas as pd
from tqdm import tqdm

from .datatypes import Cycle, TestCase, TestInfo, VisibleTestResult

_RTP_TORRENT_PROJECTS = [
    "Achilles",
    "DSpace",
    "HikariCP",
    "LittleProxy",
    "buck",
    "cloudify",
    "deeplearning4j",
    "dynjs",
    "graylog2-server",
    "jOOQ",
    "jade4j",
    "jcabi-github",
    "jetty.project",
    "jsprit",
    "okhttp",
    "optiq",
    "sling",
    "sonarqube",
    "titan",
    "wicket-bootstrap",
]


class CycleMapEntry(NamedTuple):
    commit_id: str
    cycle_time_s: float | None


@contextmanager
def _omit_csv_limit() -> Generator[None, Any]:
    original_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(sys.maxsize // 10)
        yield
    finally:
        csv.field_size_limit(original_limit)


class Dataset:
    def __init__(
        self, *, cycles_path: Path, repo_path: Path, cycle_map: dict[str, CycleMapEntry] | Path, cached: bool = True
    ) -> None:
        self._cycles_path = cycles_path
        self._repo_path = repo_path
        self._cycle_map = cycle_map
        self._cached = cached

    @classmethod
    def preload_cycle_map(cls, cycle_map_path: Path, *, debug: bool = False) -> dict[str, CycleMapEntry]:
        with _omit_csv_limit(), Path.open(cycle_map_path) as f:
            reader = csv.reader(f)
            first_row = next(reader)
            result: dict[str, CycleMapEntry] = {}
            if len(first_row) == 2:  # tr_all_built_commits.csv
                job_id_idx = first_row.index("tr_job_id")
                commit_id_idx = first_row.index("git_commit_id")
                if debug:
                    print("WARN: using the simplified map source, consider using full data")
                for row in tqdm(reader, desc="preload_cycle_map", leave=False, disable=not debug):
                    if row[job_id_idx] in result:
                        continue
                    result[row[job_id_idx]] = CycleMapEntry(commit_id=row[commit_id_idx], cycle_time_s=None)
            elif len(first_row) == 62:  # travistorrent_8_2_2017.csv
                job_id_idx = first_row.index("tr_job_id")
                commit_id_idx = first_row.index("git_trigger_commit")
                cycle_time_s_idx = first_row.index("tr_duration")
                project_name_idx = first_row.index("gh_project_name")
                for row in tqdm(reader, desc="preload_cycle_map", leave=False, disable=not debug):
                    if row[project_name_idx].split("/")[1] not in _RTP_TORRENT_PROJECTS:
                        continue
                    result[row[job_id_idx]] = CycleMapEntry(
                        commit_id=row[commit_id_idx],
                        cycle_time_s=float(row[cycle_time_s_idx]) if row[cycle_time_s_idx] != "NA" else None,
                    )
            else:
                raise ValueError(f"unsupported cycle map file format: {cycle_map_path}")
            return result

    @property
    def name(self) -> str:
        return self._cycles_path.stem

    def describe(self) -> None:
        data = self.cycles(debug=True)
        cycles = len(data)
        fail = sum(1 for c in data if c.is_failed) / cycles
        tests = sum(len(c.tests) for c in data) / cycles
        total_time_h = round(sum(c.cycle_time_s for c in data) / 3600)
        time_per_cycle_min = round(sum(c.cycle_time_s for c in data) / cycles / 60)
        name = self._cycles_path.stem
        print(
            f"{name[:16]: >16}: {cycles: >6} cycles, {fail:>6.1%} fail, {tests:>6.1f} tests, {total_time_h: >6} hours, {time_per_cycle_min: >3} min/cycle"  # noqa: E501
        )

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

        cycle_map = self._cycle_map if isinstance(self._cycle_map, dict) else self.preload_cycle_map(self._cycle_map)

        repo = git.Repo(self._repo_path)

        result: list[Cycle] = []
        invalid_jobs: list[str] = []
        invalid_commits: list[str] = []
        invalid_files: list[tuple[str, str]] = []
        for job_id, test_cases in tqdm(jobs_dict.items(), desc="cycles", leave=False, disable=not debug):
            commit_id = cycle_map[job_id].commit_id if job_id in cycle_map else None
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
                    cycle_time_s=cycle_map[job_id].cycle_time_s,
                )
            )

        if debug:
            if invalid_jobs:
                print(f"  INVALID JOB [{len(invalid_jobs)}], e.g. {invalid_jobs[0]}")
            if invalid_commits:
                print(f"  INVALID COMMIT [{len(invalid_commits)}], e.g. {invalid_commits[0]}")
            if invalid_files:
                print(f"  INVALID FILE [{len(invalid_files)}], e.g. {invalid_files[0]}")

        self._save_pickle(result)
        return result

    def _load_pickle(self) -> list[Cycle] | None:
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

    def _read_content(self, name: str) -> str | None:
        name = name.replace(".", "/") + ".java"
        paths = [self._repo_path / "src/test/java" / name]
        paths.extend(d / "src/test/java" / name for d in self._repo_path.iterdir() if d.is_dir())
        for path in paths:
            try:
                with Path.open(path) as f:
                    return f.read()
            except Exception:
                pass
        return None
