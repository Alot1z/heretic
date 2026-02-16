# SPDX-License-Identifier: AGPL-3.0-or-later

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .types import ApiCaller, BranchResponse


@dataclass(slots=True)
class BranchExecutor:
    """Parallel branch dispatcher for API calls."""

    max_workers: int = 3

    def execute(self, prompts: list[str], call_api: ApiCaller) -> list[BranchResponse]:
        responses: list[BranchResponse] = []

        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(prompts))) as pool:
            futures = {pool.submit(call_api, prompt): prompt for prompt in prompts}

            for future in as_completed(futures):
                prompt = futures[future]
                try:
                    content = future.result()
                    responses.append(BranchResponse(prompt=prompt, content=content))
                except Exception as error:  # noqa: BLE001
                    responses.append(
                        BranchResponse(prompt=prompt, content=None, error=str(error))
                    )

        return responses
