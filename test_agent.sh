#!/bin/bash
echo "Triggering Agent Run..."
curl -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "What is the latest version of LangGraph?"}'
