from langflow.custom import Component
from langflow.io import MessageInput, SecretStrInput, StrInput, Output
from langflow.schema import Message
from pydantic import SecretStr
import json
import uuid
import requests
import copy

class ProgressAgentBuilder(Component):
    display_name = "Progress Agent Builder"
    description = "Generates and saves a Voxie agent flow JSON, uploads it via API for immediate testing."
    icon = "sparkles"

    inputs = [
        MessageInput(
            name="generated_prompt",
            display_name="Generated Prompt",
            info="The generated prompt from OpenAI (Message type).",
            required=True,
        ),
        SecretStrInput(
            name="openai_api_key",
            display_name="OpenAI API Key",
            info="Your OpenAI API key.",
            required=True,
        ),
        SecretStrInput(
            name="langflow_api_key",
            display_name="Langflow API Key",
            info="Required: API key for Langflow auth (generate in UI under API Keys).",
            required=True,
        ),
        StrInput(
            name="folder_id",
            display_name="Folder ID",
            info="Required: Target project/folder ID for upload (from URL or logs).",
            required=True,
        ),
    ]

    outputs = [
        Output(name="result", display_name="Result", method="build_agent"),
    ]

    def generate_comprehensive_prompt(self, user_description: str) -> str:
        """
        Intelligently expand user's agent description into a comprehensive,
        step-by-step system prompt with role, scenarios, responses, and flow.
        """
        system_prompt = f"""You are an AI agent with the following core description:
{user_description}

ROLE & PERSONALITY:
- You embody the role described above with appropriate professionalism and tone
- You are helpful, polite, and maintain a conversational yet efficient style
- You adapt your personality to match the context (formal for business, friendly for casual interactions)

MEMORY & CONTEXT:
- You have access to conversation history and will remember important details shared during our conversation
- When users provide their name, preferences, or specific requirements, acknowledge and reference them in follow-ups
- Use context from previous messages to provide personalized, coherent responses

CONVERSATION FLOW:
1. GREETING: Start with a warm, context-appropriate welcome
2. UNDERSTANDING: Listen carefully to user inquiries and ask clarifying questions when needed
3. RESPONDING: Provide clear, accurate, and helpful information based on your role
4. CONFIRMING: Verify understanding and ensure user satisfaction with your response
5. NEXT STEPS: Guide users on what they can do next or offer additional assistance
6. CLOSING: End conversations gracefully when the user's needs are met

HANDLING USER SCENARIOS:
- Information Requests: Provide detailed, accurate information relevant to your role
- Specific Inquiries: Answer questions about availability, options, features, pricing, or processes
- Action Requests: When users want to perform actions (book, schedule, purchase, etc.), guide them through the process step-by-step
- Problem Solving: If users have issues or concerns, acknowledge them empathetically and offer solutions
- Comparisons: Help users compare options by highlighting key differences and benefits
- Recommendations: Suggest appropriate options based on user preferences and requirements

RESPONSE GUIDELINES:
- Keep responses focused and relevant to the user's current question
- Break down complex information into clear, digestible points
- Use examples when helpful to illustrate concepts
- When you don't have specific information, be honest and offer alternatives (e.g., "I can check that for you" or "Let me guide you to someone who can help")
- Simulate actions naturally (e.g., "I've noted your preference for X" or "Based on what you've shared, I recommend Y")

CONVERSATIONAL BEST PRACTICES:
- Always acknowledge the user's input before responding
- Use follow-up questions to ensure you fully understand their needs
- Provide options when multiple solutions exist
- Summarize key points when discussions are lengthy
- Maintain consistency with information provided earlier in the conversation
- End each significant response by asking if there's anything else you can help with

ERROR HANDLING:
- If a request is unclear, politely ask for clarification
- If something is outside your scope, acknowledge it and suggest next steps
- Never make up information you don't have; instead, explain what you CAN help with

ADAPTABILITY:
- Adjust detail level based on user's apparent expertise and interest
- Match the user's tone (formal vs. casual) while maintaining professionalism
- Be concise for simple queries, comprehensive for complex ones

Remember: Your goal is to provide exceptional assistance within your role, using context and memory to create a natural, helpful, and personalized conversation experience."""

        return system_prompt

    def build_agent(self) -> Message:
        self.status = "Parsing brief..."

        # Access inputs
        generated_prompt = self.generated_prompt
        if isinstance(self.openai_api_key, SecretStr):
            openai_api_key = str(self.openai_api_key.get_secret_value()).strip()
        else:
            openai_api_key = str(self.openai_api_key).strip()

        # De-duplicate OpenAI key if it was accidentally doubled
        # OpenAI keys are typically 51-56 characters (sk-proj-...)
        if openai_api_key.startswith("sk-") and len(openai_api_key) > 100:
            # Check if first half equals second half (duplication)
            half_length = len(openai_api_key) // 2
            first_half = openai_api_key[:half_length]
            second_half = openai_api_key[half_length:]
            if first_half == second_half:
                openai_api_key = first_half
                print("✓ Detected and fixed duplicated API key")

        if isinstance(self.langflow_api_key, SecretStr):
            langflow_api_key = str(self.langflow_api_key.get_secret_value()).strip()
        else:
            langflow_api_key = str(self.langflow_api_key).strip()

        folder_id = str(self.folder_id).strip()

        # Extract text from Message
        user_description = generated_prompt.text if generated_prompt and hasattr(generated_prompt, 'text') else "You are a helpful assistant."

        self.status = "Crafting intelligent prompt..."

        # Generate comprehensive system prompt
        full_system_prompt = self.generate_comprehensive_prompt(user_description)

        self.status = "Fetching template..."

        # Fetch the working Agent template flow (Basic Agent Blue Print)
        try:
            # First, get all flows to find "Basic Agent Blue Print" by name
            flows_response = requests.get(
                "http://localhost:7860/api/v1/flows/",
                headers={
                    "accept": "application/json",
                    "x-api-key": langflow_api_key
                },
                timeout=10
            )

            if flows_response.status_code != 200:
                return Message(text=f"✗ Failed to fetch flows: HTTP {flows_response.status_code}")

            flows = flows_response.json()

            # Find "Basic Agent Blue Print" flow
            template_flow_id = None
            for flow in flows:
                if flow.get("name") == "Basic Agent Blue Print":
                    template_flow_id = flow.get("id")
                    break

            if not template_flow_id:
                return Message(text="✗ Template flow 'Basic Agent Blue Print' not found. Please ensure it's imported.")

            # Now fetch the full flow details
            template_response = requests.get(
                f"http://localhost:7860/api/v1/flows/{template_flow_id}",
                headers={
                    "accept": "application/json",
                    "x-api-key": langflow_api_key
                },
                timeout=10
            )

            if template_response.status_code != 200:
                return Message(text=f"✗ Failed to fetch template flow: HTTP {template_response.status_code}")

            template_flow = template_response.json()

        except Exception as e:
            return Message(text=f"✗ Error fetching template: {str(e)}")

        self.status = "Customizing flow..."

        # Create a deep copy
        new_flow = copy.deepcopy(template_flow)

        # Update basic flow info
        flow_id = str(uuid.uuid4())
        new_flow["id"] = flow_id
        new_flow["name"] = f"Voxie Agent - {user_description[:50]}"
        new_flow["description"] = "Dynamic conversational agent with intelligent prompt and memory."

        # Generate new node IDs
        chat_input_id = f"ChatInput-{uuid.uuid4().hex[:6]}"
        agent_id = f"Agent-{uuid.uuid4().hex[:6]}"
        chat_output_id = f"ChatOutput-{uuid.uuid4().hex[:6]}"

        # Create ID mapping (old -> new)
        nodes = new_flow.get("data", {}).get("nodes", [])
        if len(nodes) < 3:
            return Message(text="✗ Template flow doesn't have expected structure")

        old_ids = {}
        node_types = {}
        for node in nodes:
            old_id = node.get("id")
            node_type = node.get("data", {}).get("type")
            if node_type:
                old_ids[node_type] = old_id
                node_types[old_id] = node_type

        id_mapping = {}
        if "ChatInput" in old_ids:
            id_mapping[old_ids["ChatInput"]] = chat_input_id
        if "Agent" in old_ids:
            id_mapping[old_ids["Agent"]] = agent_id
        if "ChatOutput" in old_ids:
            id_mapping[old_ids["ChatOutput"]] = chat_output_id

        # Update nodes with new IDs and custom values
        for node in nodes:
            old_id = node.get("id")
            if old_id in id_mapping:
                new_id = id_mapping[old_id]
                node["id"] = new_id

                # Update data.id as well
                if "data" in node:
                    node["data"]["id"] = new_id

                    # If it's Agent node, update system_prompt, API key, and memory settings
                    if node_types.get(old_id) == "Agent":
                        template = node.get("data", {}).get("node", {}).get("template", {})

                        # Update system prompt
                        if "system_prompt" in template:
                            template["system_prompt"]["value"] = full_system_prompt

                        # Update API key
                        if "api_key" in template:
                            template["api_key"]["value"] = openai_api_key

                        # Ensure memory is enabled (n_messages = 10)
                        if "n_messages" in template:
                            template["n_messages"]["value"] = 10

                        # Ensure no tools
                        if "add_current_date_tool" in template:
                            template["add_current_date_tool"]["value"] = False

                        # Set model to gpt-4o-mini
                        if "model_name" in template:
                            template["model_name"]["value"] = "gpt-4o-mini"

                        # Set temperature
                        if "temperature" in template:
                            template["temperature"]["value"] = 0.7

        # Update edges with new IDs
        edges = new_flow.get("data", {}).get("edges", [])
        for edge in edges:
            # Update source and target IDs
            if edge.get("source") in id_mapping:
                old_source = edge["source"]
                edge["source"] = id_mapping[old_source]

                # Update sourceHandle string if it contains the old ID
                if "sourceHandle" in edge and old_source in edge["sourceHandle"]:
                    edge["sourceHandle"] = edge["sourceHandle"].replace(old_source, id_mapping[old_source])

                # Update edge ID if it contains the old ID
                if "id" in edge and old_source in edge["id"]:
                    edge["id"] = edge["id"].replace(old_source, id_mapping[old_source])

                # Update data.sourceHandle.id
                if "data" in edge and "sourceHandle" in edge["data"]:
                    edge["data"]["sourceHandle"]["id"] = id_mapping[old_source]

            if edge.get("target") in id_mapping:
                old_target = edge["target"]
                edge["target"] = id_mapping[old_target]

                # Update targetHandle string if it contains the old ID
                if "targetHandle" in edge and old_target in edge["targetHandle"]:
                    edge["targetHandle"] = edge["targetHandle"].replace(old_target, id_mapping[old_target])

                # Update edge ID if it contains the old ID
                if "id" in edge and old_target in edge["id"]:
                    edge["id"] = edge["id"].replace(old_target, id_mapping[old_target])

                # Update data.targetHandle.id
                if "data" in edge and "targetHandle" in edge["data"]:
                    edge["data"]["targetHandle"]["id"] = id_mapping[old_target]

        self.status = "Uploading..."

        # Upload the modified flow
        api_url = f"http://localhost:7860/api/v1/flows/upload/?folder_id={folder_id}"

        headers = {
            "accept": "application/json",
            "x-api-key": langflow_api_key,
        }

        files = {"file": (f"{flow_id}.json", json.dumps(new_flow), "application/json")}

        try:
            response = requests.post(api_url, headers=headers, files=files, timeout=30)

            if response.status_code in (200, 201):
                try:
                    uploaded_data = response.json()
                    if isinstance(uploaded_data, list) and uploaded_data:
                        new_flow_id = uploaded_data[0].get("id", flow_id)
                    elif isinstance(uploaded_data, dict):
                        new_flow_id = uploaded_data.get("id", flow_id)
                    else:
                        new_flow_id = flow_id

                    test_link = f"http://localhost:7860/flow/{new_flow_id}"
                    print(f"✓ Agent uploaded successfully. Flow ID: {new_flow_id}")
                    result_text = f"✓ Dynamic agent created and uploaded!\n\nTest at: {test_link}\n\nAgent description: {user_description[:100]}...\n\nFeatures:\n- Intelligent system prompt\n- Conversation memory (10 messages)\n- Step-by-step guidance\n- No tools (pure conversation)\n\nReady to chat in playground!"
                    self.status = "Ready"

                except json.JSONDecodeError as e:
                    print(f"✗ JSON decode error: {str(e)}")
                    result_text = f"✗ Error parsing upload response: {str(e)}"
                    self.status = "Error"
            else:
                error_msg = response.text
                print(f"✗ Upload failed (HTTP {response.status_code}): {error_msg}")
                result_text = f"✗ Upload failed (HTTP {response.status_code}): {error_msg}\n\nCheck:\n1. API key is valid\n2. Folder ID exists: {folder_id}\n3. Langflow is running on port 7860"
                self.status = "Error"

        except requests.exceptions.ConnectionError:
            result_text = "✗ Connection error: Cannot reach Langflow at http://localhost:7860. Is Langflow running?"
            self.status = "Error"
            print(result_text)
        except Exception as e:
            result_text = f"✗ Unexpected error: {str(e)}"
            self.status = "Error"
            print(result_text)

        return Message(text=result_text)
