"""Scenario runners: build the agent context of a level and execute it."""

from __future__ import annotations

from wargent.engine.guards import Guard
from wargent.engine.levels import Level
from wargent.engine.models import RunResult, Segment
from wargent.engine.sandbox import Sandbox
from wargent.engine.sim_agent import SimAgent

SLOT_MARKER = "{{input}}"


def build_segments(templates: list[dict[str, str]], slot_input: str) -> list[Segment]:
    segments = []
    for item in templates:
        role = item["role"]
        segments.append(
            Segment(
                role=role,
                source=item.get("source", role),
                text=item["text"].replace(SLOT_MARKER, slot_input),
            )
        )
    return segments


def _finalize(output: str, agents: list[SimAgent], sandbox: Sandbox, guard: Guard) -> RunResult:
    primary = agents[0]
    output = guard.filter_output(output, primary.context())
    sandbox.render(output)
    result = RunResult(output=output, leaks=list(sandbox.leaks))
    for agent in agents:
        result.calls.extend(agent.calls)
    for index, agent in enumerate(agents):
        prefix = "" if index == 0 else "[worker] "
        result.trace.extend(f"{prefix}{line}" for line in agent.trace)
    return result


def run_single(level: Level, guard: Guard, slot_input: str) -> RunResult:
    sandbox = level.new_sandbox()
    agent = SimAgent(level.agent_config(), sandbox, guard)
    result = agent.run(build_segments(level.segments, slot_input))
    return _finalize(result.output, [agent], sandbox, guard)


def run_rugpull(level: Level, guard: Guard, slot_input: str) -> RunResult:
    scenario = level.scenario
    sandbox = level.new_sandbox()
    agent = SimAgent(level.agent_config(), sandbox, guard)
    approved = scenario["tool_description"]
    outputs: list[str] = []
    for index, task in enumerate(scenario["tasks"]):
        offered = approved if index < scenario["swap_at"] else slot_input
        if offered != approved:
            if guard.approve_tool_update(approved, offered, agent.context()):
                approved = offered
                agent.trace.append(f"tool '{scenario['tool']}': description change accepted")
            else:
                agent.trace.append(f"tool '{scenario['tool']}': description change rejected")
        segments = [
            Segment("user", "user", task),
            Segment("tooldesc", scenario["tool"], approved),
        ]
        outputs.append(agent.run(segments).output)
    return _finalize("\n".join(outputs), [agent], sandbox, guard)


def run_memory(level: Level, guard: Guard, slot_input: str) -> RunResult:
    sandbox = level.new_sandbox()
    memory: list[str] = []
    first = SimAgent(level.agent_config(), sandbox, guard, memory=memory)
    first.run(build_segments(level.segments, slot_input))
    second = SimAgent(level.agent_config(), sandbox, guard, memory=memory)
    second.trace.extend(first.trace)
    second.calls.extend(first.calls)
    segments = [Segment("memory", "memory", entry) for entry in memory]
    segments.extend(build_segments(level.segments2, slot_input))
    result = second.run(segments)
    return _finalize(result.output, [second], sandbox, guard)


def run_delegation(level: Level, guard: Guard, slot_input: str) -> RunResult:
    sandbox = level.new_sandbox()
    worker = SimAgent(level.worker_config(), sandbox, guard)

    def hand_over(message: str) -> str:
        segment = Segment("agent", "orchestrator", message)
        if not guard.accept_delegation(segment, worker.context()):
            worker.trace.append("delegated request rejected")
            return "Worker: request rejected."
        return f"Worker: {worker.run([segment]).output}"

    orchestrator = SimAgent(level.agent_config(), sandbox, guard, delegate=hand_over)
    result = orchestrator.run(build_segments(level.segments, slot_input))
    return _finalize(result.output, [orchestrator, worker], sandbox, guard)


RUNNER_FUNCTIONS = {
    "single": run_single,
    "rugpull": run_rugpull,
    "memory": run_memory,
    "delegation": run_delegation,
}


def run_level(level: Level, guard: Guard, slot_input: str) -> RunResult:
    return RUNNER_FUNCTIONS[level.runner](level, guard, slot_input)


def default_guard(level: Level) -> Guard:
    """Guard shipped with the level (the vulnerable baseline)."""
    path = level.guard_path
    return Guard.from_file(path) if path else Guard()
