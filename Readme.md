# Agent Creator

A self-expanding multi-agent system built with [Microsoft AutoGen](https://github.com/microsoft/autogen) that dynamically generates, registers, and runs AI agents at runtime, then puts them to work brainstorming Agentic AI business ideas together.

## What it does

1. **A `Creator` agent** reads a template agent file (`agent.py`) and uses an LLM to write brand-new Python agent code with a unique persona, sector focus, and personality.
2. **Each generated agent** is immediately compiled, dynamically imported, and registered into the AutoGen gRPC runtime, no restart required.
3. **Agents brainstorm business ideas**, and with some probability they bounce their idea off another randomly chosen agent for a second opinion and refinement.
4. The final ideas are saved as Markdown files.

Up to 20 agents are spawned concurrently. Every run produces a different set of agents and ideas.

## Architecture

```
world.py          ← entry point; sets up gRPC runtime, fires off tasks
creator.py        ← Creator agent: generates agent code via LLM, registers it
agent.py          ← template agent (creative entrepreneur persona)
messages.py       ← shared Message dataclass + helper to pick a random peer
test_run/         ← example output: 20 generated agents + 20 business ideas
```

### How an agent comes to life

```
world.py
  └─ send_message("agent{i}.py") → Creator
        └─ GPT-4o-mini generates new Agent class (Python code)
        └─ writes agent{i}.py to disk
        └─ importlib.import_module("agent{i}")
        └─ Agent.register(runtime, ...)     ← live in the runtime
        └─ send_message("Give me an idea") → new agent
              └─ agent thinks, maybe asks a peer for refinement
              └─ returns final idea
  └─ idea saved to idea{i}.md
```

All 20 `create_and_message` coroutines run concurrently via `asyncio.gather`.

## Example output

See [`test_run/`](test_run/) for a complete run with 20 auto-generated agents. A few samples:

| Agent   | Sector focus           | Idea highlight                                        |
| ------- | ---------------------- | ----------------------------------------------------- |
| agent1  | Real Estate + Crypto   | Tokenized fractional real estate with smart contracts |
| agent8  | Agriculture + IoT      | AI-driven precision farming cooperatives              |
| agent14 | Mental Health + Gaming | Gamified therapy platforms with adaptive AI coaches   |

## Setup

**Prerequisites**

- Python 3.10+
- OpenAI API key (set `OPENAI_API_KEY` in a `.env` file)

**Install dependencies**

```bash
pip install autogen-core autogen-agentchat autogen-ext[openai,grpc] python-dotenv
```

**Run**

```bash
python world.py
```

This spins up a local gRPC host on `localhost:50051`, creates up to 20 agents, and writes `idea1.md` … `idea20.md` to disk.

## Configuration

| Variable                                 | Where                          | Description                                         |
| ---------------------------------------- | ------------------------------ | --------------------------------------------------- |
| `HOW_MANY_AGENTS`                        | `world.py:9`                   | Number of agents to spawn (default: 20)             |
| `CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER` | `agent.py:25`                  | Probability an agent consults a peer (default: 0.5) |
| `model`                                  | `agent.py:31`, `creator.py:39` | LLM model used (default:`gpt-4o-mini`)              |
| `temperature`                            | same                           | Controls creativity of generated agents / ideas     |

## Key concepts demonstrated

- **Self-modifying agent systems** — agents that write and spawn other agents
- **Dynamic module loading** — `importlib.import_module` to hot-load generated code
- **AutoGen gRPC distributed runtime** — `GrpcWorkerAgentRuntimeHost` + `GrpcWorkerAgentRuntime`
- **Agent-to-agent messaging** — `send_message` between peers for iterative idea refinement
- **Concurrent agent orchestration** — `asyncio.gather` for parallel execution
