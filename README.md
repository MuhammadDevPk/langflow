# Voxhive Langflow Project

## Running Langflow

In project root run:
```bash
uv run langflow run
```
Then open http://localhost:7860

## Version Control for Flows

Your Langflow flows are stored in a database by default and not tracked by Git. To version control your flows:

### 1. Export Your Flows

First, get your Langflow API key:
- Open Langflow UI (http://localhost:7860)
- Go to Settings → API Keys
- Generate a new API key

Then export your flows:
```bash
# Using command line
python export_flows.py --api-key YOUR_API_KEY

# Or set environment variable
export LANGFLOW_API_KEY=your_api_key_here
python export_flows.py
```

This will save all your flows as JSON files in the `flows/` directory.

### 2. Commit to Git

```bash
git add flows/
git commit -m "Export Langflow flows"
git push
```

### 3. Update Flows After Changes

Whenever you modify flows in Langflow:
```bash
python export_flows.py
git add flows/
git commit -m "Update flows: description of changes"
git push
```

### 4. Import Flows on Another Machine

**IMPORTANT**: After cloning/pulling this repository, flows are NOT automatically loaded into Langflow. You must import them.

#### Quick Import (Recommended)

Use the import script to bulk import all flows:

```bash
# 1. Make sure Langflow is running
uv run langflow run

# 2. Get your Langflow API key
# Go to http://localhost:7860 → Settings → API Keys → Generate new key

# 3. Import all flows
python import_flows.py --api-key YOUR_API_KEY

# This will skip flows that already exist. To force re-import:
python import_flows.py --api-key YOUR_API_KEY --force
```

#### Manual Import (Alternative)

Import flows one by one through the UI:
1. Open Langflow UI at http://localhost:7860
2. Click "Flows" in the sidebar
3. Click "Import" button
4. Select JSON files from the `flows/` directory
5. Repeat for each flow you want to import

#### After Import

**Remember**: All API keys were removed for security. After importing flows, you need to:
1. Open each imported flow
2. Find the OpenAI/LLM component
3. Add your own OpenAI API key
4. Save the flow

## Project Structure

```
.
├── flows/                  # Exported flow JSON files (Git-tracked)
│   ├── Main Agent_*.json
│   ├── Basic Agent Blue Print_*.json
│   ├── Voxie Agent*.json   # Various Voxie agents
│   └── manifest.json       # Flow metadata
├── export_flows.py         # Export flows from Langflow (with secret scrubbing)
├── import_flows.py         # Import flows into Langflow
├── scrub_secrets.py        # Manually remove secrets from flow files
├── progress_agent_builder_v*.py  # Custom Langflow components
├── main.py                 # Main application entry
└── README.md               # This file
```

## Common Issues

### "I pulled the repo but see no flows in Langflow"

Flows are stored as JSON files in Git but need to be imported into Langflow's database. Run:
```bash
python import_flows.py --api-key YOUR_API_KEY
```

### "Flows are failing with API key errors"

API keys are removed from exported flows for security. You need to add your own OpenAI API key to each imported flow in the Langflow UI.
