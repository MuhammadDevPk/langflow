#!/usr/bin/env python3
"""
VAPI to Langflow Multi-Node Converter - Template Cloning Approach
Creates actual multi-node visual workflows by cloning real Langflow components.

This converter:
1. Loads a template Langflow flow with real component exports
2. Clones components for each VAPI node (preserving all embedded code)
3. Updates only dynamic fields (ID, position, prompt)
4. Creates edges matching VAPI workflow structure
5. Outputs importable Langflow JSON with 24+ actual visual nodes

Author: Claude Code
Date: 2025-11-11
"""

import json
import uuid
import copy
import sys
import os
import inspect
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class VAPIToLangflowRealNode:
    """Converts VAPI workflows to multi-node Langflow flows using template cloning."""

    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize converter with component templates.

        Args:
            template_path: Path to template flow JSON. If None, uses Main Agent flow.
        """
        # Load environment variables from .env file
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')

        if self.openai_api_key:
            print("  ✓ OpenAI API key loaded from environment")
        else:
            print("  ⚠ Warning: OPENAI_API_KEY not found in .env file")
            print("    API keys will need to be added manually to nodes")

        self.template_path = template_path or self._find_template()
        self.template_flow = self._load_template()
        self.component_library = self._extract_component_templates()

    def _find_template(self) -> str:
        """Find a suitable template flow in the flows directory."""
        flows_dir = Path(__file__).parent / "flows"

        # Look for Main Agent or any flow with OpenAI components
        candidates = [
            flows_dir / "Main Agent_9f30562c-5e21-4aba-aac5-3dc226b2495f.json",
            flows_dir / "Basic Agent Blue Print_76c0c376-55c4-4da3-979a-5a541a97db24.json"
        ]

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        # Fallback: use first JSON file in flows directory
        json_files = list(flows_dir.glob("*.json"))
        if json_files:
            return str(json_files[0])

        raise FileNotFoundError("No template flow found. Please provide a template_path.")

    def _load_template(self) -> Dict:
        """Load the template flow JSON."""
        with open(self.template_path, 'r') as f:
            return json.load(f)

    def _extract_component_templates(self) -> Dict[str, Dict]:
        """
        Extract individual component templates from the flow for cloning.

        Returns:
            Dictionary mapping component types to their template structures.
        """
        library = {}
        nodes = self.template_flow.get('data', {}).get('nodes', [])

        for node in nodes:
            node_type = node.get('data', {}).get('type')
            if node_type and node_type not in library:
                # Store deep copy as template
                library[node_type] = copy.deepcopy(node)
                print(f"  ✓ Extracted template for: {node_type}")

        return library

    def convert(self, vapi_json_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert VAPI workflow to multi-node Langflow format.

        Args:
            vapi_json_path: Path to VAPI JSON file
            output_path: Optional output path for generated JSON

        Returns:
            Generated Langflow JSON as string
        """
        print(f"\n{'='*60}")
        print("VAPI to Langflow Multi-Node Converter")
        print(f"{'='*60}\n")

        # Load VAPI workflow
        print(f"Loading VAPI workflow: {vapi_json_path}")
        with open(vapi_json_path, 'r') as f:
            vapi_data = json.load(f)

        workflow = vapi_data.get('workflow', {})
        workflow_name = workflow.get('name', 'Converted Workflow')
        vapi_nodes = workflow.get('nodes', [])
        vapi_edges = workflow.get('edges', [])

        print(f"  Workflow: {workflow_name}")
        print(f"  Nodes: {len(vapi_nodes)}")
        print(f"  Edges: {len(vapi_edges)}\n")

        # Create new flow structure
        new_flow = {
            "name": workflow_name,
            "description": f"Converted from VAPI: {workflow_name}",
            "id": str(uuid.uuid4()),
            "icon": None,
            "icon_bg_color": None,
            "gradient": None,
            "data": {
                "nodes": [],
                "edges": []
            }
        }

        # Track ID mappings (VAPI node name → Langflow node ID)
        id_map = {}

        print("Creating nodes...")

        # Add ChatInput node (entry point)
        if 'ChatInput' in self.component_library:
            chat_input = self._clone_component('ChatInput')
            chat_input['position'] = {'x': -800, 'y': 0}
            new_flow['data']['nodes'].append(chat_input)
            chat_input_id = chat_input['id']
            print(f"  ✓ ChatInput: {chat_input_id}")
        else:
            print("  ⚠  Warning: No ChatInput template found")
            chat_input_id = None

        # Convert each VAPI node to Langflow node
        for i, vapi_node in enumerate(vapi_nodes):
            try:
                langflow_node = self._convert_vapi_node(vapi_node, i)
                new_flow['data']['nodes'].append(langflow_node)
                id_map[vapi_node['name']] = langflow_node['id']

                node_type = vapi_node.get('type', 'unknown')
                print(f"  ✓ {vapi_node['name']} ({node_type}): {langflow_node['id']}")
            except Exception as e:
                print(f"  ✗ Error converting {vapi_node.get('name', 'unknown')}: {e}")

        # Add ChatOutput node (exit point)
        if 'ChatOutput' in self.component_library:
            chat_output = self._clone_component('ChatOutput')
            # Position at the end
            max_x = max([n['position']['x'] for n in new_flow['data']['nodes']], default=0)
            chat_output['position'] = {'x': max_x + 400, 'y': 0}
            new_flow['data']['nodes'].append(chat_output)
            chat_output_id = chat_output['id']
            print(f"  ✓ ChatOutput: {chat_output_id}")
        else:
            print("  ⚠  Warning: No ChatOutput template found")
            chat_output_id = None

        print(f"\nCreated {len(new_flow['data']['nodes'])} nodes\n")

        # Create edges
        print("Creating edges...")

        # Connect ChatInput to first node
        if chat_input_id and vapi_nodes:
            start_node = next((n for n in vapi_nodes if n.get('isStart')), vapi_nodes[0])
            first_node_id = id_map.get(start_node['name'])
            if first_node_id:
                edge = self._create_edge(chat_input_id, first_node_id, 'ChatInput', 'Start')
                new_flow['data']['edges'].append(edge)
                print(f"  ✓ ChatInput → {start_node['name']}")

        # Create edges from VAPI workflow
        for vapi_edge in vapi_edges:
            from_name = vapi_edge.get('from')
            to_name = vapi_edge.get('to')
            from_id = id_map.get(from_name)
            to_id = id_map.get(to_name)

            if from_id and to_id:
                edge = self._create_edge(from_id, to_id, from_name, to_name)
                new_flow['data']['edges'].append(edge)
                print(f"  ✓ {from_name} → {to_name}")
            else:
                if not from_id:
                    print(f"  ⚠  Warning: Source node not found: {from_name}")
                if not to_id:
                    print(f"  ⚠  Warning: Target node not found: {to_name}")

        # Find terminal nodes (nodes with no outgoing edges)
        terminal_nodes = set(id_map.values())
        for edge in vapi_edges:
            from_name = edge.get('from')
            if from_name in id_map:
                terminal_nodes.discard(id_map[from_name])

        # Connect terminal nodes to ChatOutput
        if chat_output_id and terminal_nodes:
            for terminal_id in terminal_nodes:
                # Find the node name
                terminal_name = next((name for name, id_ in id_map.items() if id_ == terminal_id), "unknown")
                edge = self._create_edge(terminal_id, chat_output_id, terminal_name, 'ChatOutput')
                new_flow['data']['edges'].append(edge)
                print(f"  ✓ {terminal_name} → ChatOutput")

        print(f"\nCreated {len(new_flow['data']['edges'])} edges\n")

        # Generate output
        output_json = json.dumps(new_flow, indent=2)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(output_json)
            print(f"{'='*60}")
            print(f"✓ Success! Saved to: {output_path}")
            print(f"{'='*60}\n")
            print("Next steps:")
            print("1. Import the JSON file into Langflow")
            print("2. Add OpenAI API key to OpenAI nodes")
            print("3. Test in the Playground\n")

        return output_json

    def _extract_component_source_code(self, component_type: str) -> str:
        """
        Extract component source code from installed Langflow package.

        This method dynamically imports the component class from Langflow's installed
        packages and extracts its complete Python source code using the inspect module.
        This ensures we always have valid, functional component code.

        Args:
            component_type: Type of component (e.g., 'OpenAIModel', 'ChatOutput')

        Returns:
            Full Python source code of the component class, or empty string if extraction fails
        """
        # Map component type names to their Langflow module paths
        component_map = {
            'OpenAIModel': ('langflow.components.openai.openai_chat_model', 'OpenAIModelComponent'),
            'OpenAI': ('langflow.components.openai.openai_chat_model', 'OpenAIModelComponent'),
            'ChatOutput': ('langflow.components.input_output.chat_output', 'ChatOutput'),
            'ChatInput': ('langflow.components.input_output.chat_input', 'ChatInput'),
        }

        if component_type not in component_map:
            return ""

        module_name, class_name = component_map[component_type]

        try:
            # Dynamically import the module
            module = __import__(module_name, fromlist=[class_name])

            # Get the component class
            component_class = getattr(module, class_name)

            # Extract the complete source code
            source_code = inspect.getsource(component_class)

            return source_code

        except (ImportError, AttributeError, OSError) as e:
            print(f"      ⚠ Warning: Could not extract source for {component_type}: {e}")
            return ""

    def _clean_component_code(self, cloned: Dict) -> None:
        """
        Replace corrupted 'code' field with actual component source code.

        The template may contain placeholder strings like "YOUR_API_KEY_HERE" in the
        code field instead of actual Python component code. This causes Langflow to
        fail runtime validation with "missing code" errors.

        This method extracts the real Python source code from Langflow's installed
        components and injects it into the cloned component, ensuring the workflow
        can execute without errors.

        Args:
            cloned: Cloned component dictionary (modified in place)
        """
        # Get component type and template
        component_type = cloned.get('data', {}).get('type', '')
        template = cloned.get('data', {}).get('node', {}).get('template', {})

        if 'code' not in template:
            return

        code_value = template['code'].get('value', '')

        # Check if code contains placeholder or is suspiciously short
        if (code_value == "YOUR_API_KEY_HERE" or
            len(code_value) < 100 or  # Real component code is much longer
            'class' not in code_value):  # Python component classes must have 'class' keyword

            # Extract valid source code from Langflow installation
            valid_code = self._extract_component_source_code(component_type)

            if valid_code:
                # Inject the real Python source code
                template['code']['value'] = valid_code
                print(f"      ✓ Injected valid {component_type} code ({len(valid_code)} chars)")
            else:
                # Fallback: set to empty string if extraction fails
                template['code']['value'] = ""
                print(f"      ⚠ Could not extract {component_type} code, cleared field")

    def _clone_component(self, component_type: str) -> Dict:
        """
        Clone a component from the library with a new unique ID.

        Args:
            component_type: Type of component to clone (e.g., 'ChatInput', 'OpenAIModel')

        Returns:
            Cloned component with new ID
        """
        if component_type not in self.component_library:
            raise ValueError(f"Component type '{component_type}' not found in template library")

        # Deep copy to avoid modifying template
        cloned = copy.deepcopy(self.component_library[component_type])

        # Generate new unique ID
        new_id = f"{component_type}-{uuid.uuid4().hex[:5]}"
        cloned['id'] = new_id

        # Update data.id as well
        if 'data' in cloned:
            cloned['data']['id'] = new_id

        # Clean corrupted code field to prevent "outdated components" issue
        self._clean_component_code(cloned)

        return cloned

    def _convert_vapi_node(self, vapi_node: Dict, index: int) -> Dict:
        """
        Convert a single VAPI node to a Langflow component.

        Args:
            vapi_node: VAPI node dictionary
            index: Node index for positioning

        Returns:
            Langflow node dictionary
        """
        node_type = vapi_node.get('type')
        node_name = vapi_node.get('name', f'node_{index}')

        if node_type == 'conversation':
            # Clone OpenAI or OpenAIModel component
            component_type = 'OpenAIModel' if 'OpenAIModel' in self.component_library else 'OpenAI'
            if component_type not in self.component_library:
                # Fallback to Agent if available
                component_type = 'Agent' if 'Agent' in self.component_library else list(self.component_library.keys())[0]

            langflow_node = self._clone_component(component_type)

            # Update the system message/prompt
            template = langflow_node.get('data', {}).get('node', {}).get('template', {})
            prompt = vapi_node.get('prompt', '')

            # Try different possible prompt field names
            if 'system_message' in template:
                template['system_message']['value'] = prompt
            elif 'system_prompt' in template:
                template['system_prompt']['value'] = prompt
            elif 'prompt' in template:
                template['prompt']['value'] = prompt

            # Inject OpenAI API key if available
            if self.openai_api_key and 'api_key' in template:
                template['api_key']['value'] = self.openai_api_key
                print(f"    ✓ API key injected into {node_name}")

        elif node_type == 'tool':
            # For tool nodes, use a placeholder or custom tool component
            # Since we may not have tool templates, create a simple message component
            tool_info = vapi_node.get('tool', {})
            tool_type = tool_info.get('type', 'unknown')

            # Try to use a ChatOutput or similar as placeholder
            component_type = 'ChatOutput' if 'ChatOutput' in self.component_library else list(self.component_library.keys())[0]
            langflow_node = self._clone_component(component_type)

            # Add tool information in a comment or description
            if 'data' in langflow_node and 'node' in langflow_node['data']:
                langflow_node['data']['node']['description'] = f"Tool: {tool_type}"

        else:
            # Unknown type, use a default component
            component_type = list(self.component_library.keys())[0]
            langflow_node = self._clone_component(component_type)

        # Set position from VAPI metadata or auto-layout
        if 'metadata' in vapi_node and 'position' in vapi_node['metadata']:
            position = vapi_node['metadata']['position']
            langflow_node['position'] = {
                'x': float(position.get('x', 0)),
                'y': float(position.get('y', 0))
            }
        else:
            # Auto-layout: horizontal arrangement
            langflow_node['position'] = {
                'x': -400 + (index * 300),
                'y': 100
            }

        return langflow_node

    def _get_component_io_info(self, node_id: str) -> Dict[str, Any]:
        """
        Get input/output information for a component based on its type.

        Args:
            node_id: Node ID to get component info for

        Returns:
            Dictionary with component type, output name, and input name
        """
        # Determine component type from node ID prefix
        if node_id.startswith("ChatInput"):
            return {
                "type": "ChatInput",
                "output_name": "message",
                "output_types": ["Message"],
                "input_name": "input_value",
                "input_types": ["Message"],
                "input_type": "str"
            }
        elif node_id.startswith("OpenAIModel") or node_id.startswith("OpenAI"):
            return {
                "type": "OpenAIModel",
                "output_name": "text_output",  # OpenAI outputs "text_output", not "message"!
                "output_types": ["Message"],
                "input_name": "input_value",
                "input_types": ["Message"],
                "input_type": "str"
            }
        elif node_id.startswith("ChatOutput"):
            return {
                "type": "ChatOutput",
                "output_name": "message",
                "output_types": ["Message"],
                "input_name": "input_value",
                "input_types": ["Data", "DataFrame", "Message"],
                "input_type": "other"
            }
        else:
            # Default fallback
            return {
                "type": "Component",
                "output_name": "output",
                "output_types": ["Message"],
                "input_name": "input_value",
                "input_types": ["Message"],
                "input_type": "str"
            }

    def _create_edge(self, source_id: str, target_id: str,
                    source_name: str = "", target_name: str = "") -> Dict:
        """
        Create a Langflow edge connecting two nodes with proper handle format.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            source_name: Source node name (for logging)
            target_name: Target node name (for logging)

        Returns:
            Edge dictionary with JSON-stringified handles
        """
        # Get component info for source and target
        source_info = self._get_component_io_info(source_id)
        target_info = self._get_component_io_info(target_id)

        # Create source handle object
        source_handle_obj = {
            "dataType": source_info["type"],
            "id": source_id,
            "name": source_info["output_name"],
            "output_types": source_info["output_types"]
        }

        # Create target handle object
        target_handle_obj = {
            "fieldName": target_info["input_name"],
            "id": target_id,
            "inputTypes": target_info["input_types"],
            "type": target_info["input_type"]
        }

        # Stringify handles (Langflow expects JSON strings)
        source_handle_str = json.dumps(source_handle_obj)
        target_handle_str = json.dumps(target_handle_obj)

        # Create edge ID using Langflow's format
        edge_id = f"xy-edge__{source_id}{source_handle_str}-{target_id}{target_handle_str}"

        edge = {
            "source": source_id,
            "sourceHandle": source_handle_str,
            "target": target_id,
            "targetHandle": target_handle_str,
            "data": {
                "targetHandle": target_handle_obj,
                "sourceHandle": source_handle_obj
            },
            "id": edge_id,
            "selected": False,
            "animated": False,
            "className": ""
        }

        return edge


def main():
    """CLI interface for the converter."""
    parser = argparse.ArgumentParser(
        description='Convert VAPI workflow JSON to Langflow multi-node format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert using default template
  python vapi_to_langflow_realnode_converter.py input.json

  # Convert with custom output name
  python vapi_to_langflow_realnode_converter.py input.json -o output.json

  # Convert using specific template
  python vapi_to_langflow_realnode_converter.py input.json -t template.json
        """
    )

    parser.add_argument(
        'input',
        help='Path to VAPI JSON file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: <input>_langflow_multinode.json)',
        default=None
    )

    parser.add_argument(
        '-t', '--template',
        help='Path to template Langflow flow JSON (optional)',
        default=None
    )

    args = parser.parse_args()

    # Determine output path
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_langflow_multinode.json")

    try:
        # Create converter
        print("Initializing converter...")
        converter = VAPIToLangflowRealNode(template_path=args.template)
        print(f"  Using template: {converter.template_path}")
        print(f"  Available components: {', '.join(converter.component_library.keys())}\n")

        # Convert
        converter.convert(args.input, args.output)

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
