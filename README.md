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

### 4. Import Flows on Another Machine (ONE COMMAND!)

**IMPORTANT**: After cloning/pulling this repository, flows are NOT automatically loaded into Langflow. You must import them.

The import script is **smart** and will:
- ✅ Check if Langflow is running (on port 7860)
- ✅ Detect existing folders or create a new one
- ✅ Import all flows to the correct folder automatically
- ✅ Skip flows that already exist

#### Quick Import (Just 3 Steps!)

```bash
# 1. Start Langflow (runs on port 7860)
uv run langflow run

# 2. Generate API key in Langflow UI
# Go to http://localhost:7860 → Settings → API Keys → Generate new key

# 3. Run ONE command to import everything!
python import_flows.py --api-key YOUR_API_KEY
```

**That's it!** The script will:
- Find your existing folder (or create "Voxhive Flows" folder)
- Import all 26 flows to that folder
- Open your browser to see the flows

To force re-import all flows:
```bash
python import_flows.py --api-key YOUR_API_KEY --force
```

#### After Import

**Remember**: All API keys were removed for security. After importing flows, you need to:
1. Open each imported flow in Langflow UI
2. Find the Agent/OpenAI component
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

The smart import script will automatically detect or create a folder and import all flows there.

### "Flows are failing with API key errors"

API keys are removed from exported flows for security. You need to add your own OpenAI API key to each imported flow in the Langflow UI.

### "Langflow won't start - port 7860 already in use"

If you see an error about port 7860 being in use:

```bash
# Find what's using port 7860
lsof -i :7860

# Kill the process if it's an old Langflow instance
kill -9 <PID>

# Or just use a different terminal - you might already have Langflow running!
```

### "Import script says Langflow is not running"

Make sure Langflow is running before importing:
```bash
uv run langflow run
```

Then in a new terminal, run the import script.
