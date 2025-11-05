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

To restore flows from this repository:
1. Clone the repository
2. In Langflow UI: Flows → Import → Select JSON file from `flows/` directory
3. Or use the API to bulk import

## Project Structure

```
.
├── flows/                  # Exported flow JSON files (Git-tracked)
├── export_flows.py         # Script to export flows from Langflow
├── progress_agent_builder_v*.py  # Custom Langflow components
├── main.py                 # Main application entry
└── README.md              # This file
```
