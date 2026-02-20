#!/usr/bin/env python3
"""
VAPI to Langflow Unified Agent Converter
Consolidates a VAPI workflow into a single "Unified Agent" node in Langflow.
This approach handles complex routing and logic via a comprehensive system prompt
rather than visual edges, avoiding Langflow's conditional routing limitations.

Author: Google Deepmind Agent
Date: 2025-11-23
"""

import json
import uuid
import copy
import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Import the new builder
try:
    from unified_agent_builder import UnifiedAgentBuilder
except ImportError:
    # Fallback if running from a different directory context
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from unified_agent_builder import UnifiedAgentBuilder

class VAPIToLangflowUnified:
    """Converts VAPI workflows to a single Unified Agent Langflow flow."""

    def __init__(self, template_path: Optional[str] = None):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.template_path = template_path or self._find_template()
        self.template_flow = self._load_template()
        self.component_library = self._extract_component_templates()

    def _find_template(self) -> str:
        """Find a suitable template flow."""
        # flows directory is a sibling of vapi_converter (both in agent_management)
        script_dir = Path(__file__).parent
        flows_dir = script_dir.parent / "flows"
        
        candidates = [
            flows_dir / "Basic Agent Blue Print_db0fbfd2-0d14-4088-a001-23a950623b1e.json",
            flows_dir / "Main Agent_5ba25e7a-91aa-4259-8d4a-e54fe42f1df5.json"
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        
        # Fallback
        json_files = list(flows_dir.glob("*.json")) if flows_dir.exists() else []
        if json_files:
            return str(json_files[0])
        raise FileNotFoundError(f"No template flow found in {flows_dir}")

    def _load_template(self) -> Dict:
        with open(self.template_path, 'r') as f:
            return json.load(f)

    def _extract_component_templates(self) -> Dict[str, Dict]:
        library = {}
        nodes = self.template_flow.get('data', {}).get('nodes', [])
        for node in nodes:
            node_type = node.get('data', {}).get('type')
            if node_type and node_type not in library:
                library[node_type] = copy.deepcopy(node)
        
        # Ensure we have essential components
        if 'OpenAIModel' not in library and 'Agent' in library:
             library['OpenAIModel'] = library['Agent'] # Fallback
             
        return library

    def _clone_component(self, component_type: str) -> Dict:
        if component_type not in self.component_library:
            # Try fallback
            if component_type == 'OpenAIModel':
                 # Look for any model-like component
                 for key in self.component_library:
                     if 'Model' in key or 'Agent' in key:
                         return self._clone_component(key)
            raise ValueError(f"Component '{component_type}' not found in template.")
            
        cloned = copy.deepcopy(self.component_library[component_type])
        new_id = f"{component_type}-{uuid.uuid4().hex[:5]}"
        cloned['id'] = new_id
        if 'data' in cloned:
            cloned['data']['id'] = new_id
        return cloned

    def convert(self, vapi_json_path: str, output_path: Optional[str] = None) -> str:
        print(f"Loading VAPI workflow: {vapi_json_path}")
        with open(vapi_json_path, 'r') as f:
            vapi_data = json.load(f)

        # 1. Build the Unified System Prompt
        builder = UnifiedAgentBuilder(vapi_data)
        system_prompt = builder.build_system_prompt()
        print("✓ Generated Unified System Prompt")

        # 2. Create Flow Structure
        workflow_name = vapi_data.get('workflow', {}).get('name', 'Unified Agent')
        new_flow = {
            "name": f"{workflow_name} (Unified)",
            "description": "Unified Agent handling all VAPI logic via system prompt",
            "id": str(uuid.uuid4()),
            "data": {
                "nodes": [], 
                "edges": [],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            },
            "is_component": False,
            "updated_at": "2025-11-23T00:00:00Z",
            "mcp_enabled": True,
            "icon": None,
            "icon_bg_color": None,
            "gradient": None,
            "webhook": False,
            "endpoint_name": None,
            "tags": [],
            "locked": False,
            "access_type": "PRIVATE"
        }

        # 3. Create Nodes
        # 3. Create Nodes
        # ChatInput
        chat_input = self._clone_component('ChatInput')
        chat_input['position'] = {'x': 0, 'y': 0}
        new_flow['data']['nodes'].append(chat_input)
        
        # OpenAI Model (The Unified Agent)
        agent_node = self._clone_component('OpenAIModel')
        agent_node['position'] = {'x': 400, 'y': 0}
        
        # Inject System Prompt
        template = agent_node.get('data', {}).get('node', {}).get('template', {})
        
        if 'system_message' in template:
            template['system_message']['value'] = system_prompt
        elif 'system_prompt' in template:
            template['system_prompt']['value'] = system_prompt
        elif 'prompt' in template:
            template['prompt']['value'] = system_prompt
            
        # Set Model Name to GPT-4o
        if 'model_name' in template:
            template['model_name']['value'] = 'gpt-4o'
        
        # Inject API Key
        if self.openai_api_key:
            if 'api_key' in template:
                template['api_key']['value'] = self.openai_api_key
            elif 'openai_api_key' in template:
                template['openai_api_key']['value'] = self.openai_api_key
            
        new_flow['data']['nodes'].append(agent_node)
        
        # ChatOutput
        chat_output = self._clone_component('ChatOutput')
        chat_output['position'] = {'x': 800, 'y': 0}
        new_flow['data']['nodes'].append(chat_output)

        # Calendar Tool Node (Custom Component)
        # We create a generic CustomComponent node and populate it with our tool code
        calendar_tool_code = ""
        try:
            # Read the tool code from file
            tool_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "custom_tools", "calendar_tool.py")
            with open(tool_path, "r") as f:
                calendar_tool_code = f.read()
        except Exception as e:
            print(f"Warning: Could not read calendar_tool.py: {e}")
            calendar_tool_code = "# Error loading tool code"

        # Create the node structure manually since we might not have a template for CustomComponent
        calendar_node_id = f"CustomComponent-{uuid.uuid4().hex[:5]}"
        calendar_node = {
            "id": calendar_node_id,
            "type": "genericNode",
            "position": {"x": 400, "y": 300},
            "data": {
                "type": "CustomComponent",
                "id": calendar_node_id,
                "node": {
                    "template": {
                        "_type": "Component",
                        "code": {
                            "type": "code",
                            "required": True,
                            "placeholder": "",
                            "list": False,
                            "show": True,
                            "multiline": True,
                            "value": calendar_tool_code,
                            "name": "code",
                            "advanced": False,
                            "dynamic": True
                        }
                    },
                    "description": "A tool for booking appointments in Google Calendar",
                    "display_name": "Google Calendar Tool",
                    "icon": "Calendar",
                    "base_classes": ["Tool"],
                    "outputs": [
                        {
                            "types": ["Tool"],
                            "selected": "Tool",
                            "name": "build",
                            "display_name": "Tool",
                            "method": "build",
                            "value": "__UNDEFINED__",
                            "cache": True,
                            "allows_loop": False,
                            "group_outputs": False,
                            "tool_mode": True
                        }
                    ]
                }
            }
        }
        new_flow['data']['nodes'].append(calendar_node)

        # 4. Create Edges with Complex Handles
        def create_handle(node_id, name, type_str, io_type, data_type=None):
            handle = {
                "id": node_id,
            }
            if io_type == "source":
                handle["name"] = name
                handle["output_types"] = [type_str]
                handle["dataType"] = data_type
            else:
                handle["fieldName"] = name
                handle["inputTypes"] = [type_str] if isinstance(type_str, str) else type_str
                handle["type"] = data_type
            return handle

        # ChatInput -> Agent
        # Source: ChatInput (message)
        source_handle_1 = create_handle(chat_input['id'], "message", "Message", "source", "ChatInput")
        # Target: OpenAIModel (input_value)
        target_handle_1 = create_handle(agent_node['id'], "input_value", "Message", "target", "str")
        
        edge1 = {
            "id": f"edge-{uuid.uuid4().hex[:8]}",
            "source": chat_input['id'],
            "target": agent_node['id'],
            "sourceHandle": json.dumps(source_handle_1), 
            "targetHandle": json.dumps(target_handle_1),
            "data": {
                "sourceHandle": source_handle_1,
                "targetHandle": target_handle_1
            },
            "type": "default"
        }
        
        # Agent -> ChatOutput
        # Determine handle based on component type
        agent_type = agent_node.get('data', {}).get('type')
        if agent_type == 'Agent':
            source_handle_name = "response"
            source_data_type = "Agent"
        else:
            source_handle_name = "text_output"
            source_data_type = "OpenAIModel"

        # Source: Agent/OpenAIModel
        source_handle_2 = create_handle(agent_node['id'], source_handle_name, "Message", "source", source_data_type)
        # Target: ChatOutput (input_value)
        target_handle_2 = create_handle(chat_output['id'], "input_value", ["Data", "DataFrame", "Message"], "target", "other")
        
        edge2 = {
            "id": f"edge-{uuid.uuid4().hex[:8]}",
            "source": agent_node['id'],
            "target": chat_output['id'],
            "sourceHandle": json.dumps(source_handle_2),
            "targetHandle": json.dumps(target_handle_2),
            "data": {
                "sourceHandle": source_handle_2,
                "targetHandle": target_handle_2
            },
            "type": "default"
        }

        # Calendar Tool -> Agent
        # Source: Calendar Tool (tool) - CustomComponent usually outputs a Tool or similar
        # We need to check the output name in the custom component code, usually it's the return type name or defined in outputs
        # For CustomComponent, it often defaults to "build" output if not specified.
        # Let's assume standard Tool output.
        source_handle_3 = create_handle(calendar_node['id'], "build", "Tool", "source", "CustomComponent")
        # Target: Agent (tools)
        target_handle_3 = create_handle(agent_node['id'], "tools", "Tool", "target", "list")

        edge3 = {
            "id": f"edge-{uuid.uuid4().hex[:8]}",
            "source": calendar_node['id'],
            "target": agent_node['id'],
            "sourceHandle": json.dumps(source_handle_3),
            "targetHandle": json.dumps(target_handle_3),
            "data": {
                "sourceHandle": source_handle_3,
                "targetHandle": target_handle_3
            },
            "type": "default"
        }
        
        new_flow['data']['edges'] = [edge1, edge2, edge3]

        # 5. Output
        output_json = json.dumps(new_flow, indent=2)
        if output_path:
            with open(output_path, 'w') as f:
                f.write(output_json)
            print(f"✓ Saved Unified Agent flow to: {output_path}")
            
        return output_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert VAPI to Unified Langflow Agent")
    parser.add_argument("input", help="Path to VAPI JSON file")
    parser.add_argument("output", help="Path to output Langflow JSON file")
    args = parser.parse_args()

    converter = VAPIToLangflowUnified()
    converter.convert(args.input, args.output)
