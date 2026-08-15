"""CursorSdkAdapter: one-shot AsyncAgent.prompt per decision. Architecture §6.4."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Callable, Awaitable

from app import settings
from app.agents.port import DecisionError, parse_decision_json, validate_decision
from app.agents.prompts import REPAIR_SUFFIX, render_decision_prompt
from app.contracts import AgentDecision, AgentDecisionRequest
from app.store import data_root

logger = logging.getLogger(__name__)


class DecisionStartupError(RuntimeError):
    pass


class DecisionRunError(RuntimeError):
    pass


def _strip_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def parse_agent_result(text: str) -> AgentDecision:
    return validate_decision(parse_decision_json(_strip_fence(text)))


class CursorSdkAdapter:
    def __init__(
        self,
        client: Any,
        prompt_fn: Callable[..., Awaitable[Any]] | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client
        self.prompt_fn = prompt_fn
        self.api_key = api_key if api_key is not None else settings.CURSOR_API_KEY
        self.model = model or settings.CURSOR_MODEL

    def _scratch(self, request: AgentDecisionRequest) -> Path:
        path = (
            data_root()
            / request.experiment_id
            / "scratch"
            / request.run_id.value
            / f"r{request.round}"
            / request.agent_id
        )
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _options(self, request: AgentDecisionRequest):
        from cursor_sdk import AgentOptions, LocalAgentOptions

        scratch = self._scratch(request)
        return AgentOptions(
            api_key=self.api_key,
            model=self.model,
            name=f"{request.experiment_id}:{request.run_id.value}:r{request.round}:{request.agent_id}",
            tools=[],
            local=LocalAgentOptions(cwd=str(scratch)),
        )

    async def _prompt(self, message: str, request: AgentDecisionRequest) -> Any:
        from cursor_sdk import AsyncAgent, CursorAgentError

        options = self._options(request)
        assert options.tools == []
        assert getattr(options.local, "setting_sources", None) in (None, ())
        prompt = self.prompt_fn or AsyncAgent.prompt
        try:
            result = await prompt(message, options, client=self.client)
        except CursorAgentError as err:
            raise DecisionStartupError(str(err)) from err
        logger.info("cursor agent_id=%s run.id=%s", getattr(result, "agent_id", ""), getattr(result, "id", ""))
        return result

    async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
        prompt = render_decision_prompt(request)
        result = await self._prompt(prompt, request)
        if getattr(result, "status", None) == "error":
            raise DecisionRunError(str(getattr(result, "id", "")))
        try:
            return parse_agent_result(getattr(result, "result", "") or "")
        except DecisionError:
            repaired = await self._prompt(prompt + REPAIR_SUFFIX, request)
            if getattr(repaired, "status", None) == "error":
                raise DecisionRunError(str(getattr(repaired, "id", "")))
            return parse_agent_result(getattr(repaired, "result", "") or "")
