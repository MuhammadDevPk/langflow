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
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class VAPIToLangflowRealNode:
    """Converts VAPI workflows to multi-node Langflow flows using template cloning."""

    def __init__(self, template_path: Optional[str] = None, validate_api_key: bool = True):
        """
        Initialize converter with component templates.

        Args:
            template_path: Path to template flow JSON. If None, uses Main Agent flow.
            validate_api_key: Whether to validate the OpenAI API key (default: True)
        """
        # Load environment variables from .env file
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')

        if self.openai_api_key:
            print("  ✓ OpenAI API key loaded from environment")

            # Validate API key if requested
            if validate_api_key:
                print("  ⏳ Validating API key with OpenAI...")
                if self._validate_openai_api_key():
                    print("  ✅ API key is valid and working")
                else:
                    print("  ❌ API key validation FAILED")
                    print("     The key may be invalid, revoked, or expired")
                    print("     Please check your key at: https://platform.openai.com/api-keys")
                    print("\n  ⚠️  WARNING: Generated JSON will contain an invalid API key!")
                    print("     You can continue, but Langflow will fail with authentication errors.")

                    # Ask user if they want to continue
                    response = input("\n  Continue anyway? (yes/no): ").strip().lower()
                    if response not in ['yes', 'y']:
                        print("\n  Exiting. Please update your API key and try again.")
                        sys.exit(1)
        else:
            print("  ⚠ Warning: OPENAI_API_KEY not found in .env file")
            print("    API keys will need to be added manually to nodes")

        self.template_path = template_path or self._find_template()
        self.template_flow = self._load_template()
        self.component_library = self._extract_component_templates()

    def _find_template(self) -> str:
        """Find a suitable template flow in the flows directory."""
        flows_dir = Path(__file__).parent / "flows"

        # Look for Basic Agent Blue Print first (has complete component code)
        # Main Agent has placeholder code that requires extraction
        candidates = [
            flows_dir / "Basic Agent Blue Print_76c0c376-55c4-4da3-979a-5a541a97db24.json",
            flows_dir / "Main Agent_9f30562c-5e21-4aba-aac5-3dc226b2495f.json"
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

    def _load_conditional_router_template(self) -> Optional[Dict]:
        """
        Load ConditionalRouter template from all_nodes_json.json.

        Returns:
            ConditionalRouter template node or None if not found.
        """
        # Check if conditional_router_template.json exists (we extracted it earlier)
        conditional_router_path = Path(__file__).parent / "conditional_router_template.json"
        if conditional_router_path.exists():
            with open(conditional_router_path, 'r') as f:
                return json.load(f)

        # Fallback: try to load from all_nodes_json.json
        all_nodes_path = Path(__file__).parent / "json" / "outputs" / "all_nodes_json.json"
        if all_nodes_path.exists():
            try:
                with open(all_nodes_path, 'r') as f:
                    data = json.load(f)
                    nodes = data.get('data', {}).get('nodes', [])
                    for node in nodes:
                        if node.get('id', '').startswith('ConditionalRouter-'):
                            return copy.deepcopy(node)
            except Exception as e:
                print(f"  ⚠  Warning: Could not load ConditionalRouter from all_nodes_json.json: {e}")

        return None

    def _load_openai_model_template(self) -> Optional[Dict]:
        """
        Load OpenAIModel template for router nodes.

        Returns:
            OpenAIModel template node or None if not found.
        """
        # Check if openai_model_template.json exists
        openai_model_path = Path(__file__).parent / "openai_model_template.json"
        if openai_model_path.exists():
            with open(openai_model_path, 'r') as f:
                return json.load(f)

        # Fallback: try to load from Main Agent flow
        main_agent_path = Path(__file__).parent / "flows" / "Main Agent_9f30562c-5e21-4aba-aac5-3dc226b2495f.json"
        if main_agent_path.exists():
            try:
                with open(main_agent_path, 'r') as f:
                    data = json.load(f)
                    nodes = data.get('data', {}).get('nodes', [])
                    for node in nodes:
                        if node.get('data', {}).get('type') == 'OpenAIModel':
                            return copy.deepcopy(node)
            except Exception as e:
                print(f"  ⚠  Warning: Could not load OpenAIModel from Main Agent flow: {e}")

        return None

    def _validate_openai_api_key(self) -> bool:
        """
        Validate the OpenAI API key by making a test request to OpenAI's API.

        Returns:
            True if the API key is valid, False otherwise
        """
        if not self.openai_api_key:
            return False

        try:
            # Test the API key with a simple models endpoint request
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers={'Authorization': f'Bearer {self.openai_api_key}'},
                timeout=10
            )

            # Check if the request was successful
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                # Unauthorized - invalid API key
                return False
            else:
                # Other error - assume key might be valid but other issues exist
                print(f"     Unexpected status code: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print("     API validation timed out - network issue?")
            # Don't fail on timeout, assume key might be valid
            return True
        except requests.exceptions.RequestException as e:
            print(f"     API validation error: {e}")
            # Don't fail on network errors, assume key might be valid
            return True
        except Exception as e:
            print(f"     Unexpected error during validation: {e}")
            return True

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

        # Load ConditionalRouter template if not already present
        if 'ConditionalRouter' not in library:
            conditional_router_template = self._load_conditional_router_template()
            if conditional_router_template:
                library['ConditionalRouter'] = conditional_router_template
                print(f"  ✓ Loaded ConditionalRouter template from all_nodes_json.json")

        # Load OpenAIModel template if not already present (needed for router nodes)
        if 'OpenAIModel' not in library:
            openai_model_template = self._load_openai_model_template()
            if openai_model_template:
                library['OpenAIModel'] = openai_model_template
                print(f"  ✓ Loaded OpenAIModel template for router nodes")

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

        # Build set of nodes that have incoming edges (to detect orphans)
        edge_targets = {edge['to'] for edge in vapi_edges}

        # Identify start node (first node that should always be created)
        start_node_name = vapi_nodes[0]['name'] if vapi_nodes else None

        # Track which nodes we actually create (for edge validation later)
        created_node_names = set()

        # Convert each VAPI node to Langflow node
        for i, vapi_node in enumerate(vapi_nodes):
            node_name = vapi_node.get('name', f'node_{i}')

            # Skip orphan nodes (no incoming edges) unless it's the start node
            if node_name not in edge_targets and node_name != start_node_name:
                print(f"  ⚠ Skipping orphan node: {node_name}")
                continue

            try:
                langflow_node = self._convert_vapi_node(vapi_node, i)
                new_flow['data']['nodes'].append(langflow_node)
                id_map[vapi_node['name']] = langflow_node['id']
                created_node_names.add(node_name)

                node_type = vapi_node.get('type', 'unknown')
                print(f"  ✓ {node_name} ({node_type}): {langflow_node['id']}")
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

        # Feature 4: Detect branching points and insert routing logic
        print("Detecting branching points...")
        branching_nodes = self._find_branching_nodes(vapi_edges)
        print(f"  Found {len(branching_nodes)} branching points\n")

        if branching_nodes:
            # Calculate node depths to determine which branching points to route
            print("Calculating node depths to filter first-level branching...")
            node_depths = self._calculate_node_depths(vapi_nodes, vapi_edges)

            # Filter branching nodes: only keep first-level (depth ≤ 1)
            # This keeps only the top-level routing decisions, dramatically reducing cascade
            MAX_ROUTING_DEPTH = 1
            first_level_branching = {}
            nested_branching = {}

            for node_name, edges in branching_nodes.items():
                depth = node_depths.get(node_name, 999)
                if depth <= MAX_ROUTING_DEPTH:
                    first_level_branching[node_name] = edges
                else:
                    nested_branching[node_name] = edges

            print(f"  First-level branching (depth ≤ {MAX_ROUTING_DEPTH}): {len(first_level_branching)} nodes")
            print(f"  Nested branching (depth > {MAX_ROUTING_DEPTH}): {len(nested_branching)} nodes (will use direct edges)\n")

            if first_level_branching:
                print("Inserting routing logic for first-level branching points...")
                for source_name, outgoing_edges in first_level_branching.items():
                    source_id = id_map.get(source_name)
                    if not source_id:
                        print(f"  ⚠  Warning: Source node not found for branching: {source_name}")
                        continue

                    # Get source node position
                    source_node = next((n for n in new_flow['data']['nodes'] if n['id'] == source_id), None)
                    if not source_node:
                        continue

                    source_pos = source_node['position']
                    depth = node_depths.get(source_name, 0)

                    # Insert RouterAgent + ConditionalRouter chain
                    routing_nodes = self._insert_routing_logic(
                        source_id, source_name, outgoing_edges, id_map, source_pos
                    )

                    # Add routing nodes to flow
                    new_flow['data']['nodes'].extend(routing_nodes)
                    print(f"  ✓ {source_name} (depth {depth}): Added {len(routing_nodes)} routing nodes ({len(outgoing_edges)} branches)")

                print(f"\nInserted routing logic for {len(first_level_branching)} first-level branching points")

            if nested_branching:
                print(f"\nSkipped routing for {len(nested_branching)} nested branching points:")
                for node_name in sorted(nested_branching.keys()):
                    depth = node_depths.get(node_name, 999)
                    num_branches = len(nested_branching[node_name])
                    print(f"  ⊗ {node_name} (depth {depth}): {num_branches} branches → will use direct edges")

            print()

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

        # Create edges from VAPI workflow (with routing logic if branching)
        edges_handled_by_routing = set()

        # Get the first_level_branching set (only these use routing logic)
        first_level_set = set(first_level_branching.keys()) if 'first_level_branching' in locals() else set()

        for vapi_edge in vapi_edges:
            from_name = vapi_edge.get('from')
            to_name = vapi_edge.get('to')
            from_id = id_map.get(from_name)
            to_id = id_map.get(to_name)
            condition = vapi_edge.get('condition')

            # Check if this edge is part of a FIRST-LEVEL branching point
            if from_name in first_level_set:
                # This edge will be handled by routing logic
                edges_handled_by_routing.add((from_name, to_name))
                continue

            # For nested branching (depth > 2), create direct edge (skip routing)
            # This is the key change: nested branches connect directly without ConditionalRouter

            if from_id and to_id:
                edge = self._create_edge(from_id, to_id, from_name, to_name, condition)
                new_flow['data']['edges'].append(edge)

                # Show condition info if present
                if condition and condition.get('prompt'):
                    cond_preview = condition['prompt'][:40] + "..." if len(condition['prompt']) > 40 else condition['prompt']
                    print(f"  ✓ {from_name} → {to_name} [condition: {cond_preview}]")
                else:
                    print(f"  ✓ {from_name} → {to_name}")
            else:
                if not from_id:
                    reason = "(orphan node)" if from_name not in created_node_names else "(not in id_map)"
                    print(f"  ⚠  Skipping edge: Source node not found: {from_name} {reason}")
                if not to_id:
                    reason = "(orphan node)" if to_name not in created_node_names else "(not in id_map)"
                    print(f"  ⚠  Skipping edge: Target node not found: {to_name} {reason}")

        # Create routing edges for branching points
        if hasattr(self, '_routing_components') and self._routing_components:
            print("\nCreating routing edges...")
            
            # Identify the start node name
            start_node_name = next((n['name'] for n in vapi_nodes if n.get('isStart')), vapi_nodes[0]['name']) if vapi_nodes else None

            for source_name, routing_info in self._routing_components.items():
                source_id = id_map.get(source_name)
                router_agent_id = routing_info['router_agent_id']
                edges_to_targets = routing_info['edges']
                pattern = routing_info['routing_pattern']

                # LOGIC FIX: Only connect ChatInput to the Router if it's the START NODE.
                # For deep nodes, we must connect Source -> Router (even if it has AI text issues, it's better than "all at once")
                if chat_input_id and source_name == start_node_name:
                    edge = self._create_edge(chat_input_id, router_agent_id, 'ChatInput', f"Router({source_name})")
                    new_flow['data']['edges'].append(edge)
                    print(f"  ✓ ChatInput → Router({source_name}) [Start Node Router]")
                else:
                    # For non-start nodes, connect Source -> Router
                    edge = self._create_edge(source_id, router_agent_id, source_name, f"Router({source_name})")
                    new_flow['data']['edges'].append(edge)
                    print(f"  ✓ {source_name} → Router({source_name}) [Nested Router]")

                if pattern == 'simple':
                    # 2-way routing: RouterAgent → ConditionalRouter → [true/false targets]
                    cond_router_id = routing_info['conditional_router_id']

                    # Connect RouterAgent → ConditionalRouter
                    edge = self._create_edge(router_agent_id, cond_router_id,
                                            f"Router({source_name})", f"RouteCheck({source_name})")
                    new_flow['data']['edges'].append(edge)
                    print(f"  ✓ Router({source_name}) → RouteCheck({source_name})")

                    # Connect ConditionalRouter true_result → target 1
                    target_1_name = edges_to_targets[0].get('to')
                    target_1_id = id_map.get(target_1_name)
                    if target_1_id:
                        # Need to create edge from ConditionalRouter's true_result output
                        edge = self._create_edge_with_specific_output(
                            cond_router_id, target_1_id, "true_result",
                            f"RouteCheck({source_name})", target_1_name
                        )
                        new_flow['data']['edges'].append(edge)
                        print(f"  ✓ RouteCheck({source_name}) [TRUE] → {target_1_name}")

                    # Connect ConditionalRouter false_result → target 2
                    target_2_name = edges_to_targets[1].get('to')
                    target_2_id = id_map.get(target_2_name)
                    if target_2_id:
                        edge = self._create_edge_with_specific_output(
                            cond_router_id, target_2_id, "false_result",
                            f"RouteCheck({source_name})", target_2_name
                        )
                        new_flow['data']['edges'].append(edge)
                        print(f"  ✓ RouteCheck({source_name}) [FALSE] → {target_2_name}")

                elif pattern == 'cascade':
                    # 3+ way routing: cascade pattern
                    cascade_router_ids = routing_info['cascade_router_ids']

                    # Connect RouterAgent → first ConditionalRouter
                    first_router_id = cascade_router_ids[0]
                    edge = self._create_edge(router_agent_id, first_router_id,
                                            f"Router({source_name})", f"RouteCheck_1({source_name})")
                    new_flow['data']['edges'].append(edge)
                    print(f"  ✓ Router({source_name}) → RouteCheck_1({source_name})")

                    # Connect cascade chain
                    for i, cond_router_id in enumerate(cascade_router_ids):
                        condition_num = i + 1

                        # Connect true_result → target i
                        target_name = edges_to_targets[i].get('to')
                        target_id = id_map.get(target_name)
                        if target_id:
                            edge = self._create_edge_with_specific_output(
                                cond_router_id, target_id, "true_result",
                                f"RouteCheck_{condition_num}({source_name})", target_name
                            )
                            new_flow['data']['edges'].append(edge)
                            print(f"  ✓ RouteCheck_{condition_num}({source_name}) [TRUE] → {target_name}")

                        # Connect false_result → next router or default target
                        if i < len(cascade_router_ids) - 1:
                            # Connect to next router
                            next_router_id = cascade_router_ids[i + 1]
                            edge = self._create_edge_with_specific_output(
                                cond_router_id, next_router_id, "false_result",
                                f"RouteCheck_{condition_num}({source_name})", f"RouteCheck_{condition_num + 1}({source_name})"
                            )
                            new_flow['data']['edges'].append(edge)
                            print(f"  ✓ RouteCheck_{condition_num}({source_name}) [FALSE] → RouteCheck_{condition_num + 1}({source_name})")
                        else:
                            # Last router: connect to default target (last edge)
                            default_target_name = edges_to_targets[-1].get('to')
                            default_target_id = id_map.get(default_target_name)
                            if default_target_id:
                                edge = self._create_edge_with_specific_output(
                                    cond_router_id, default_target_id, "false_result",
                                    f"RouteCheck_{condition_num}({source_name})", default_target_name
                                )
                                new_flow['data']['edges'].append(edge)
                                print(f"  ✓ RouteCheck_{condition_num}({source_name}) [FALSE] → {default_target_name} (default)")

        # Find terminal nodes (nodes with no outgoing edges)
        terminal_nodes = set(id_map.values())
        for edge in vapi_edges:
            from_name = edge.get('from')
            if from_name in id_map:
                terminal_nodes.discard(id_map[from_name])

        # Identify reachable nodes (nodes with incoming edges in the NEW flow)
        reachable_nodes = set()
        for edge in new_flow['data']['edges']:
            reachable_nodes.add(edge['target'])
        
        # Add Start Node to reachable (it's reached by ChatInput)
        if start_node_name and start_node_name in id_map:
            reachable_nodes.add(id_map[start_node_name])

        # Connect terminal nodes to ChatOutput
        if chat_output_id and terminal_nodes:
            for terminal_id in terminal_nodes:
                # Skip unreachable nodes (dead code) to avoid "Input data cannot be None" errors
                if terminal_id not in reachable_nodes:
                    terminal_name = next((name for name, id_ in id_map.items() if id_ == terminal_id), "unknown")
                    print(f"  ⚠ Skipping dead terminal node: {terminal_name} (no incoming edges)")
                    continue

                # Find the node name
                terminal_name = next((name for name, id_ in id_map.items() if id_ == terminal_id), "unknown")

                # Skip Start Node if it has a router (it's being bypassed by ChatInput -> Router)
                # If we don't skip it, we'll see "Hello..." AND the routed response
                if terminal_name == start_node_name and start_node_name in self._routing_components:
                     print(f"  ⚠ Skipping Start Node output: {terminal_name} (handled by Router)")
                     continue

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
            print("2. Add OpenAI API key to OpenAI nodes (if not auto-injected)")
            print("3. Test in the Playground")
            print("\nFeatures implemented:")
            print("  ✓ Feature 1: Variable Extraction (JSON output in prompts)")
            print("  ✓ Feature 2: Conversation Flow (first messages)")
            print("  ✓ Feature 3: Basic Chat (ChatInput/ChatOutput)")
            print("  ✓ Feature 4: Conditional Routing (RouterAgent + ConditionalRouter)")
            print(f"  → {len(branching_nodes)} branching points with intelligent routing")
            print("  ⚠ Feature 5: Tool Integration (not yet implemented)\n")

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

        # Skip code cleaning - Basic Agent Blue Print template already has complete code
        # self._clean_component_code(cloned)  # Disabled: causes "missing code" errors

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
            # Use Agent for all conversation nodes (reliable Message format)
            component_type = 'Agent' if 'Agent' in self.component_library else 'OpenAIModel'
            if component_type not in self.component_library:
                # Fallback to any available component
                component_type = list(self.component_library.keys())[0]

            langflow_node = self._clone_component(component_type)

            # Update the system message/prompt
            template = langflow_node.get('data', {}).get('node', {}).get('template', {})
            prompt = vapi_node.get('prompt', '')

            # Extract first message if present (for conversation flow)
            message_plan = vapi_node.get('messagePlan', {})
            first_message = message_plan.get('firstMessage')
            if first_message:
                # Prepend first message as an explicit instruction
                prompt = f"FIRST MESSAGE: When starting the conversation or when this node is first reached, begin by saying:\n\"{first_message}\"\n\nThen continue with your role:\n{prompt}"
                print(f"    ✓ First message configured: \"{first_message[:60]}...\"" if len(first_message) > 60 else f"    ✓ First message configured: \"{first_message}\"")

            # Check if this node extracts variables
            variable_extraction_plan = vapi_node.get('variableExtractionPlan')
            if variable_extraction_plan:
                # Add JSON output formatting to prompt for variable extraction
                extracted_vars = variable_extraction_plan.get('output', [])
                if extracted_vars:
                    var_names = [v.get('title') for v in extracted_vars]
                    var_descriptions = {v.get('title'): v.get('description', '') for v in extracted_vars}

                    # Build JSON schema description
                    json_schema = "{\n"
                    for var in extracted_vars:
                        var_name = var.get('title')
                        var_desc = var.get('description', '')
                        var_type = var.get('type', 'string')
                        var_enum = var.get('enum', [])

                        if var_enum:
                            json_schema += f'  "{var_name}": "{var_enum[0]}" // Options: {", ".join(var_enum)}\n'
                        else:
                            json_schema += f'  "{var_name}": "<{var_type}>" // {var_desc}\n'
                    json_schema += "}"

                    # Enhance prompt with variable extraction instructions
                    prompt += f"\n\nIMPORTANT: After your response, you MUST extract the following information and output it as JSON:\n{json_schema}\n\n"
                    prompt += f"Variables to extract: {', '.join(var_names)}\n"
                    prompt += "Format: First provide your conversational response, then on a new line output ONLY the JSON object with extracted values."

                    print(f"    ✓ Variable extraction configured: {', '.join(var_names)}")

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
        elif node_id.startswith("Agent"):
            return {
                "type": "Agent",
                "output_name": "response",  # Agent outputs "response", not "output"!
                "output_types": ["Message"],
                "input_name": "input_value",
                "input_types": ["Message"],
                "input_type": "str"
            }
        elif node_id.startswith("ConditionalRouter"):
            return {
                "type": "ConditionalRouter",
                "output_name": "true_result",  # Has two outputs: true_result and false_result
                "output_types": ["Message"],
                "input_name": "input_text",  # Primary input
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
                    source_name: str = "", target_name: str = "",
                    condition: Dict = None) -> Dict:
        """
        Create a Langflow edge connecting two nodes with proper handle format.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            source_name: Source node name (for logging)
            target_name: Target node name (for logging)
            condition: Optional VAPI condition metadata (for conversation flow)

        Returns:
            Edge dictionary with JSON-stringified handles and optional condition metadata
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

        # Add VAPI condition metadata if present (for conversation flow)
        if condition:
            edge['data']['vapiCondition'] = {
                'type': condition.get('type', 'ai'),
                'prompt': condition.get('prompt', '')
            }
            # Store for future Feature 4 (Conditional Routing) implementation

        return edge

    def _create_edge_with_specific_output(self, source_id: str, target_id: str,
                                          output_name: str, source_name: str = "",
                                          target_name: str = "") -> Dict:
        """
        Create edge with a specific output handle (for ConditionalRouter true/false outputs).

        Args:
            source_id: Source node ID
            target_id: Target node ID
            output_name: Specific output handle name (e.g., "true_result", "false_result")
            source_name: Source node name (for logging)
            target_name: Target node name (for logging)

        Returns:
            Edge dictionary
        """
        # Get component info
        source_info = self._get_component_io_info(source_id)
        target_info = self._get_component_io_info(target_id)

        # Override output name with specific output
        source_handle_obj = {
            "dataType": source_info["type"],
            "id": source_id,
            "name": output_name,  # Use specific output (true_result or false_result)
            "output_types": source_info["output_types"]
        }

        target_handle_obj = {
            "fieldName": target_info["input_name"],
            "id": target_id,
            "inputTypes": target_info["input_types"],
            "type": target_info["input_type"]
        }

        # Stringify handles
        source_handle_str = json.dumps(source_handle_obj)
        target_handle_str = json.dumps(target_handle_obj)

        # Create edge ID
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

    def _calculate_node_depths(self, vapi_nodes: List[Dict], vapi_edges: List[Dict]) -> Dict[str, int]:
        """
        Calculate the depth of each node from the start node.

        Args:
            vapi_nodes: List of VAPI nodes
            vapi_edges: List of VAPI edges

        Returns:
            Dictionary mapping node names to their depth (0 for start node)
        """
        # Find start node
        start_nodes = [n for n in vapi_nodes if n.get('isStart', False)]
        if not start_nodes and vapi_nodes:
            start_nodes = [vapi_nodes[0]]

        if not start_nodes:
            return {}

        start_name = start_nodes[0]['name']

        # Build adjacency list
        graph = {}
        for edge in vapi_edges:
            from_name = edge.get('from')
            to_name = edge.get('to')
            if from_name and to_name:
                if from_name not in graph:
                    graph[from_name] = []
                graph[from_name].append(to_name)

        # BFS to calculate depths
        depths = {start_name: 0}
        queue = [start_name]

        while queue:
            current = queue.pop(0)
            current_depth = depths[current]

            if current in graph:
                for neighbor in graph[current]:
                    if neighbor not in depths:
                        depths[neighbor] = current_depth + 1
                        queue.append(neighbor)

        return depths

    def _find_branching_nodes(self, vapi_edges: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Find nodes with multiple outgoing edges (branching points).

        Args:
            vapi_edges: List of VAPI edges

        Returns:
            Dictionary mapping node names to list of outgoing edges
        """
        outgoing = {}
        for edge in vapi_edges:
            from_node = edge.get('from')
            if from_node:
                if from_node not in outgoing:
                    outgoing[from_node] = []
                outgoing[from_node].append(edge)

        # Return only nodes with 2+ outgoing edges (branching points)
        branching = {k: v for k, v in outgoing.items() if len(v) >= 2}
        return branching

    def _create_router_agent(self, source_node_name: str, conditions: List[Dict],
                            source_node_id: str, position: Dict[str, float]) -> Dict:
        """
        Create a Router Agent that evaluates VAPI conditions using LLM.

        Uses Agent (not OpenAIModel) because Agent's Message format is reliable
        and works consistently with ConditionalRouter's MessageTextInput.

        Args:
            source_node_name: Name of the source node (for identification)
            conditions: List of VAPI condition dictionaries with 'prompt' field
            source_node_id: ID of the source node (for positioning)
            position: Position dictionary with x and y coordinates

        Returns:
            Router node dictionary (Agent type)
        """
        # Use Agent for routing (reliable Message format)
        if 'Agent' not in self.component_library:
            raise ValueError("Agent template required for routing")

        router = self._clone_component('Agent')

        # Build routing prompt with EXTREME strictness for numeric-only output
        condition_texts = []
        for i, condition in enumerate(conditions, 1):
            cond_prompt = condition.get('prompt', f'Condition {i}')
            condition_texts.append(f"{i}. {cond_prompt}")

        routing_prompt = f"""ROUTING DECISION - CRITICAL FORMAT REQUIREMENT

CONDITIONS:
{chr(10).join(condition_texts)}

YOUR RESPONSE FORMAT (CRITICAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Response MUST be EXACTLY this format:
[DIGIT]

Where [DIGIT] is 1, 2, 3, etc. based on which condition matches.

CORRECT examples:
1
2
3

WRONG examples (DO NOT USE):
- "1" (with quotes)
- "The answer is 1"
- "Route to 1"
- "1 - User wants appointment"
- "Based on analysis, I choose option 1"

INSTRUCTIONS:
1. Read the user's message carefully
2. Match it to the BEST condition above
3. Output ONLY the digit (no other text)
4. Stop immediately

Your response (digit only):"""

        # Update template for Agent
        template = router['data']['node']['template']

        # Set system prompt/message
        if 'system_message' in template:
            template['system_message']['value'] = routing_prompt
        elif 'system_prompt' in template:
            template['system_prompt']['value'] = routing_prompt
        elif 'agent_description' in template:
            template['agent_description']['value'] = routing_prompt

        # Inject API key if available
        if self.openai_api_key and 'api_key' in template:
            template['api_key']['value'] = self.openai_api_key
            print(f"    ✓ API key injected into Router Agent")

        # Set position
        router['position'] = position

        # Update node name for clarity
        router['data']['node']['display_name'] = f"Router ({source_node_name})"

        return router

    def _create_conditional_router(self, condition_index: int, total_conditions: int,
                                   position: Dict[str, float], branch_name: str = "") -> Dict:
        """
        Create a ConditionalRouter node for path selection.

        Args:
            condition_index: The condition number to match (1, 2, 3, etc.)
            total_conditions: Total number of conditions
            position: Position dictionary with x and y coordinates
            branch_name: Name of the branch (for display)

        Returns:
            ConditionalRouter node dictionary
        """
        if 'ConditionalRouter' not in self.component_library:
            raise ValueError("ConditionalRouter template not available")

        router = self._clone_component('ConditionalRouter')

        # Configure the router
        template = router['data']['node']['template']
        template['operator']['value'] = 'contains'  # Use 'contains' to be more forgiving
        template['match_text']['value'] = str(condition_index)
        template['case_sensitive']['value'] = False  # Case insensitive matching
        template['max_iterations']['value'] = 10
        template['default_route']['value'] = 'false_result'

        # Set position
        router['position'] = position

        # Update display name
        if branch_name:
            router['data']['node']['display_name'] = f"Route Check ({branch_name})"

        return router

    def _insert_routing_logic(self, source_id: str, source_name: str,
                             edges_to_targets: List[Dict], id_map: Dict[str, str],
                             position: Dict[str, float]) -> List[Dict]:
        """
        Insert RouterAgent + ConditionalRouter chain between source and targets.

        Args:
            source_id: Source node ID
            source_name: Source node name
            edges_to_targets: List of edges from source to different targets
            id_map: Mapping of VAPI names to Langflow IDs
            position: Starting position for routing nodes

        Returns:
            List of new nodes (RouterAgent + ConditionalRouters)
        """
        new_nodes = []
        num_branches = len(edges_to_targets)

        # Extract conditions
        conditions = [edge.get('condition', {}) for edge in edges_to_targets]

        # Create RouterAgent
        router_agent_pos = {
            'x': position['x'] + 300,
            'y': position['y']
        }
        router_agent = self._create_router_agent(
            source_name, conditions, source_id, router_agent_pos
        )
        new_nodes.append(router_agent)
        router_agent_id = router_agent['id']

        # Store for edge creation
        self._routing_components = getattr(self, '_routing_components', {})
        self._routing_components[source_name] = {
            'router_agent_id': router_agent_id,
            'edges': edges_to_targets,
            'num_branches': num_branches
        }



        if num_branches == 2:
            # Simple 2-way routing: single ConditionalRouter
            cond_router_pos = {
                'x': position['x'] + 600,
                'y': position['y']
            }
            cond_router = self._create_conditional_router(
                1, num_branches, cond_router_pos,
                f"{source_name}_branch"
            )
            new_nodes.append(cond_router)
            cond_router_id = cond_router['id']

            # Store routing info
            self._routing_components[source_name]['conditional_router_id'] = cond_router_id
            self._routing_components[source_name]['routing_pattern'] = 'simple'

        else:
            # 3+ way routing: cascade pattern
            # Create chain of ConditionalRouters
            cascade_routers = []
            for i in range(num_branches - 1):
                cond_router_pos = {
                    'x': position['x'] + 600 + (i * 300),
                    'y': position['y'] + (i * 150)
                }
                target_edge = edges_to_targets[i]
                target_name = target_edge.get('to', f'branch_{i+1}')

                cond_router = self._create_conditional_router(
                    i + 1, num_branches, cond_router_pos,
                    target_name
                )
                new_nodes.append(cond_router)
                cascade_routers.append(cond_router['id'])

            # Store routing info
            self._routing_components[source_name]['cascade_router_ids'] = cascade_routers
            self._routing_components[source_name]['routing_pattern'] = 'cascade'

        return new_nodes


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

    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip OpenAI API key validation (faster but may generate invalid JSON)',
        default=False
    )

    args = parser.parse_args()

    # Determine output path
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_langflow_multinode.json")

    try:
        # Create converter
        print("Initializing converter...")
        converter = VAPIToLangflowRealNode(
            template_path=args.template,
            validate_api_key=not args.skip_validation
        )
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
