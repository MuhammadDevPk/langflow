# Langflow Flows

This directory contains exported Langflow flows in JSON format for version control.

## Purpose

Langflow stores flows in a SQLite database by default, which is not suitable for version control. This directory allows you to:
- Track changes to your flows over time
- Share flows with team members via Git
- Back up your flows
- Review flow changes in pull requests

## Flows

Current flows in this repository:
- **Main Agent**: Your primary conversational agent
- **Basic Blueprint**: Template flow for creating new agents
- **Generated Agents**: Dynamically created agent flows

## Exporting Flows

To export your current flows from Langflow to this directory:

```bash
python export_flows.py --api-key YOUR_LANGFLOW_API_KEY
```

Or set the API key as an environment variable:

```bash
export LANGFLOW_API_KEY=your_key_here
python export_flows.py
```

## Importing Flows

To import a flow back into Langflow:

1. Use the Langflow UI: Go to "Flows" → "Import" → Select the JSON file
2. Or use the API:
   ```bash
   curl -X POST "http://localhost:7860/api/v1/flows/upload/" \
     -H "x-api-key: YOUR_API_KEY" \
     -F "file=@flows/your_flow.json"
   ```

## Workflow

1. Make changes to your flows in Langflow UI
2. Export flows: `python export_flows.py`
3. Review changes: `git diff flows/`
4. Commit: `git add flows/ && git commit -m "Update flows"`
5. Push: `git push`

## Notes

- Flow files are named using the pattern: `{flow_name}_{flow_id}.json`
- The `manifest.json` file contains metadata about all exported flows
- Make sure Langflow is running when exporting flows
