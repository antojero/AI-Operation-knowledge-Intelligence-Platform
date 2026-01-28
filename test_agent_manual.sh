#!/bin/bash
# Test the agent execution manually
curl -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Research the latest advancements in AI Agents for 2025"}'
