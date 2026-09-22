# RIG Integration Guide (V11)

Use `rig_comm` as a drop-in outbound communications guard for any agent stack.

## Core API

```python
from rig_comm import evaluate

report = evaluate("Your team is losing 40% engineering time to architecture tax. If this is not useful, ignore this.")
print(report.can_ship, report.blocks)
```

## CommunicationGuard (framework-agnostic)

```python
from rig_comm.integrations import CommunicationGuard

guard = CommunicationGuard(channel="email", max_attempts=2)
result = guard.guard(draft_text)
```

## LangGraph adapter

```python
from rig_comm.integrations import langgraph_guard_node
next_state = langgraph_guard_node({"draft": draft_text}, text_key="draft", channel="email")
```

## CrewAI adapter

```python
from rig_comm.integrations import crewai_guard_tool
payload = crewai_guard_tool(draft_text, channel="email")
```

## AutoGen adapter

```python
from rig_comm.integrations import AutoGenRigGuard
hook = AutoGenRigGuard(channel="reply")
payload = hook.filter_reply(draft_text)
```

## OpenAI-style tool/function schema

```python
from rig_comm.integrations import openai_tool_schema, openai_tool_handler
schema = openai_tool_schema()
result = openai_tool_handler(text=draft_text, channel="email", mode="guard")
```

## MCP tool definition

```python
from rig_comm.integrations import mcp_tool_definition, mcp_tool_call
defn = mcp_tool_definition()
result = mcp_tool_call(text=draft_text, channel="email", guard=True)
```

## System-prompt injector

```python
from rig_comm import canonical_system_prompt
system_prompt = canonical_system_prompt()
```
