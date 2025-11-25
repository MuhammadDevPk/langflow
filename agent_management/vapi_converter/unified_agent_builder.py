import json
from typing import Dict, List, Any, Optional

class UnifiedAgentBuilder:
    """
    Builds a unified system prompt from a VAPI workflow.
    Consolidates all nodes, edges, and logic into a single set of instructions.
    """

    def __init__(self, vapi_data: Dict):
        self.workflow = vapi_data.get('workflow', {})
        self.nodes = self.workflow.get('nodes', [])
        self.edges = self.workflow.get('edges', [])
        self.node_map = {node['name']: node for node in self.nodes}

    def build_system_prompt(self) -> str:
        """Generates the complete system prompt for the Unified Agent."""
        
        # 1. Header & Role
        prompt = [
            "You are a unified voice AI assistant. Your goal is to handle the entire conversation flow defined below.",
            "You must strictly follow the state transitions and instructions for each node.",
            "Maintain the persona and tone defined in the 'start' node throughout the conversation.",
            "\n--- GLOBAL INSTRUCTIONS ---",
            "1. **State Management**: You are always in one specific 'Node' of the conversation.",
            "2. **Transitions**: After each user response, check the 'Transitions' for your current node. If a condition is met, move to the next node immediately.",
            "3. **Responses**: Speak ONLY the 'Prompt' for your current node. Do not make up text outside the instructions.",
            "4. **Variable Extraction**: If the current node requires variable extraction, output the JSON at the end of your response.",
            "\n--- CONVERSATION FLOW ---"
        ]

        # 2. Process Each Node
        for node in self.nodes:
            node_name = node.get('name', 'unknown')
            node_type = node.get('type', 'conversation')
            node_prompt = node.get('prompt', '')
            
            prompt.append(f"\n## NODE: {node_name}")
            
            # Add First Message info if it's the start node
            if node.get('isStart'):
                msg_plan = node.get('messagePlan', {})
                first_msg = msg_plan.get('firstMessage')
                if first_msg:
                    prompt.append(f"**STARTING MESSAGE**: \"{first_msg}\"")
            
            # Main Prompt/Instruction
            if node_prompt:
                prompt.append(f"**INSTRUCTION**: {node_prompt}")
            
            # Variable Extraction Plan
            var_plan = node.get('variableExtractionPlan')
            if var_plan:
                prompt.append("**VARIABLES TO EXTRACT**:")
                outputs = var_plan.get('output', [])
                for var in outputs:
                    title = var.get('title')
                    desc = var.get('description')
                    enum_vals = var.get('enum')
                    line = f"- {title}: {desc}"
                    if enum_vals:
                        line += f" (Options: {', '.join(enum_vals)})"
                    prompt.append(line)
            
            # Transitions (Edges)
            outgoing_edges = [e for e in self.edges if e.get('from') == node_name]
            if outgoing_edges:
                prompt.append("**TRANSITIONS**:")
                for edge in outgoing_edges:
                    to_node = edge.get('to')
                    condition = edge.get('condition', {})
                    cond_desc = condition.get('prompt', 'Default/Always')
                    prompt.append(f"- IF {cond_desc} -> GOTO Node: {to_node}")
            else:
                prompt.append("**TRANSITIONS**: End of conversation (Hang up or wait).")

        # 3. Footer / Format Instructions
        prompt.append("\n--- RESPONSE FORMAT ---")
        prompt.append("For every turn, your output must be:")
        prompt.append("1. Your conversational response (text).")
        prompt.append("2. (If applicable) A JSON block with extracted variables.")
        prompt.append("3. (Internal Thought) [State: <Current_Node> -> <Next_Node>]")
        
        return "\n".join(prompt)
