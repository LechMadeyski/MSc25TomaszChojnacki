from typing import Any, Generator, Optional
import git
import pandas as pd
from .datatypes import TestInfo


class TcpDataset:
    def __init__(self, runs_path: str, repo_path: str, run_to_commit_path: str):
        self._run_dict: dict[str, list[dict[str, Any]]] = (
            pd.read_csv(runs_path)
            .sort_values(["travisJobId", "index"])
            .astype({"travisJobId": "str"})
            .groupby("travisJobId", sort=False)
            .apply(
                lambda x: x[["testName", "duration", "failures"]].to_dict("records"),
                include_groups=False,
            )
            .to_dict()
        )

        self._repo_path = repo_path
        self._repo = git.Repo(repo_path)

        rtc_df = pd.read_csv(run_to_commit_path)
        self._run_to_commit: dict[str, str] = pd.Series(
            rtc_df["git_commit_id"].astype("str").values,
            index=rtc_df["tr_job_id"].astype("str"),
        ).to_dict()

    def _read_content(self, name: str) -> Optional[str]:
        try:
            with open(
                f"{self._repo_path}/src/test/java/{name.replace('.', '/')}.java", "r"
            ) as f:
                return f.read()
        except:
            return None

    def runs(self) -> Generator[tuple[str, list[TestInfo]], None, None]:
        self._repo.git.checkout(".")
        for run_id, test_cases in self._run_dict.items():
            if run_id not in self._run_to_commit:
                continue
            commit_id = self._run_to_commit[run_id]
            self._repo.git.checkout(commit_id)

            for tc in test_cases:
                tc["content"] = self._read_content(tc["testName"])
            if any(tc["content"] is None for tc in test_cases):
                continue

            yield (
                run_id,
                [
                    TestInfo(
                        name=tc["testName"],
                        content=tc["content"],
                        failures=tc["failures"],
                        duration_s=tc["duration"],
                    )
                    for tc in test_cases
                ],
            )
