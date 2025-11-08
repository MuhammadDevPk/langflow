from flask import Flask, request
import requests
import os
import json
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

# Base Configuration
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "sk-SlAQGa_sWQnLcJHEHW2WLIFkv17xjpGLdj3EhRV5bmY")

# Default agent (currently hardcoded, works as single static agent)
DEFAULT_FLOW_ID = os.getenv("DEFAULT_FLOW_ID", "9c7c075b-85da-4dfd-ae0c-bcb322851b04")
DEFAULT_VOICE_INTRO = os.getenv("DEFAULT_VOICE_INTRO", "Hi, this is your Voxie agent. How can I help you today?")
DEFAULT_VOICE_TYPE = os.getenv("DEFAULT_VOICE_TYPE", "Polly.Matthew")

# Dynamic Agent Mapping (optional - leave empty for now, add later for multi-agent)
# Format: {"phone_number": {"flow_id": "xxx", "intro": "yyy", "voice": "zzz"}}
# Example when you want multiple agents:
# {
#   "14722302360": {"flow_id": "hotel-flow-id", "intro": "Hotel booking service", "voice": "Polly.Joanna"},
#   "15551234567": {"flow_id": "car-flow-id", "intro": "Car rental service", "voice": "Polly.Matthew"}
# }
AGENT_MAPPINGS = os.getenv("AGENT_MAPPINGS", "{}")
# AGENT_MAPPINGS={
#     "14722302360": {
#       "flow_id": "9c7c075b-85da-4dfd-ae0c-bcb322851b04",
#       "intro": "Hi, this is your hotel booking assistant",
#       "voice": "Polly.Joanna"
#     },
#     "15551234567": {
#       "flow_id": "car-receptionist-flow-id",
#       "intro": "Welcome to car rental service",
#       "voice": "Polly.Matthew"
#     },
#     "15559876543": {
#       "flow_id": "doctor-assistant-flow-id",
#       "intro": "Hello, this is Dr. Pawel's assistant",
#       "voice": "Polly.Amy"
#     }
#   }

try:
    agent_map = json.loads(AGENT_MAPPINGS)
except:
    agent_map = {}

def get_agent_config(twilio_number):
    """
    Get agent configuration based on Twilio number called.

    How it works:
    - NOW: Returns default agent (single static agent)
    - LATER: When you add AGENT_MAPPINGS, returns specific agent per number

    Returns: (flow_id, intro_message, voice_type)
    """
    # If no mappings configured, use default (current behavior)
    if not agent_map:
        return (DEFAULT_FLOW_ID, DEFAULT_VOICE_INTRO, DEFAULT_VOICE_TYPE)

    # Clean phone number format (remove +, spaces, etc.)
    clean_number = twilio_number.replace("+", "").replace("-", "").replace(" ", "")

    # Check if this number has a custom agent mapped
    if clean_number in agent_map:
        config = agent_map[clean_number]
        return (
            config.get("flow_id", DEFAULT_FLOW_ID),
            config.get("intro", DEFAULT_VOICE_INTRO),
            config.get("voice", DEFAULT_VOICE_TYPE)
        )

    # Also try with + prefix
    if twilio_number in agent_map:
        config = agent_map[twilio_number]
        return (
            config.get("flow_id", DEFAULT_FLOW_ID),
            config.get("intro", DEFAULT_VOICE_INTRO),
            config.get("voice", DEFAULT_VOICE_TYPE)
        )

    # Fallback to default agent
    return (DEFAULT_FLOW_ID, DEFAULT_VOICE_INTRO, DEFAULT_VOICE_TYPE)

@app.route('/', methods=['GET'])
def greet():
    return {
        "status": "running",
        "service": "Twilio-Langflow Bridge (Multi-Agent Ready)",
        "mode": "single-agent" if not agent_map else "multi-agent",
        "agents_configured": len(agent_map) if agent_map else 1,
        "default_agent": DEFAULT_FLOW_ID
    }, 200

@app.route('/voice', methods=['POST'])
def voice_webhook():
    """Handle incoming Twilio voice calls with dynamic agent routing."""

    # Get which number was called (To = your Twilio number)
    called_number = request.values.get('To', '')
    caller_number = request.values.get('From', '')
    speech = request.values.get('SpeechResult', '').strip()

    # Get agent configuration for this number
    # NOW: Returns default hardcoded agent
    # LATER: Returns specific agent based on phone number
    flow_id, voice_intro, voice_type = get_agent_config(called_number)

    print(f"📞 Call from {caller_number} to {called_number}")
    print(f"🤖 Using Flow: {flow_id}")

    if not speech:
        # First call: Prompt user to speak
        resp = VoiceResponse()
        gather = Gather(
            input='speech',
            action='/voice',
            method='POST',
            speech_timeout='auto',
            language='en-US',
            speech_model='phone_call'
        )
        gather.say(voice_intro, voice=voice_type)
        resp.append(gather)
        resp.redirect('/voice')
        return str(resp)

    # Call Langflow API for agent response
    try:
        headers = {"Content-Type": "application/json"}
        if LANGFLOW_API_KEY:
            headers["x-api-key"] = LANGFLOW_API_KEY

        lf_payload = {
            "input_value": speech,
            "output_type": "chat",
            "input_type": "chat",
            "session_id": caller_number  # Maintain conversation per caller
        }

        lf_response = requests.post(
            f"{LANGFLOW_URL}/api/v1/run/{flow_id}",
            json=lf_payload,
            headers=headers,
            timeout=15
        )

        if lf_response.status_code == 200:
            response_data = lf_response.json()

            # Extract agent reply from response
            if isinstance(response_data.get('outputs'), list) and len(response_data['outputs']) > 0:
                first_output = response_data['outputs'][0]
                if 'outputs' in first_output and len(first_output['outputs']) > 0:
                    results = first_output['outputs'][0].get('results', {})
                    message = results.get('message', {})
                    agent_reply = message.get('text', '')
                else:
                    agent_reply = first_output.get('message', {}).get('text', '')
            elif 'outputs' in response_data:
                outputs = response_data['outputs']
                if isinstance(outputs, dict):
                    agent_reply = outputs.get('text', outputs.get('response', outputs.get('message', '')))
                else:
                    agent_reply = str(outputs)
            else:
                agent_reply = response_data.get('text', response_data.get('message', ''))

            if not agent_reply or agent_reply == '':
                agent_reply = "I processed your request, but I'm having trouble formulating a response. Could you try again?"
        else:
            print(f"Langflow API error: {lf_response.status_code} - {lf_response.text}")
            agent_reply = "I'm having trouble thinking right now. Please try again in a moment."

    except requests.exceptions.Timeout:
        agent_reply = "Sorry, I'm taking too long to respond. Please call back in a moment."
    except Exception as e:
        print(f"Error calling Langflow: {str(e)}")
        agent_reply = "I encountered a technical issue. Please try again."

    # Respond with TTS
    resp = VoiceResponse()
    resp.say(agent_reply, voice=voice_type, language='en-US')

    # Ask if user wants to continue
    gather = Gather(
        input='speech',
        action='/voice',
        method='POST',
        speech_timeout='3',
        language='en-US',
        speech_model='phone_call'
    )
    gather.say("Is there anything else I can help you with?", voice=voice_type)
    resp.append(gather)

    # End gracefully if no response
    resp.say("Thank you for calling. Goodbye!", voice=voice_type)
    resp.hangup()

    return str(resp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "default_flow_id": DEFAULT_FLOW_ID,
        "mode": "single-agent" if not agent_map else "multi-agent",
        "agents_mapped": len(agent_map),
        "langflow_url": LANGFLOW_URL
    }, 200

@app.route('/agents', methods=['GET'])
def list_agents():
    """List all configured agents - useful for debugging."""
    return {
        "mode": "single-agent" if not agent_map else "multi-agent",
        "default_agent": {
            "flow_id": DEFAULT_FLOW_ID,
            "intro": DEFAULT_VOICE_INTRO,
            "voice": DEFAULT_VOICE_TYPE
        },
        "mapped_agents": agent_map if agent_map else {}
    }, 200

if __name__ == '__main__':
    if not DEFAULT_FLOW_ID:
        print("❌ ERROR: DEFAULT_FLOW_ID not set!")
        exit(1)

    print("\n" + "="*60)
    print("🚀 Twilio-Langflow Bridge Starting...")
    print("="*60)
    print(f"📍 Langflow URL: {LANGFLOW_URL}")
    print(f"🤖 Default Flow ID: {DEFAULT_FLOW_ID}")
    print(f"📞 Mode: {'Multi-Agent' if agent_map else 'Single-Agent (Static)'}")

    if agent_map:
        print(f"✅ {len(agent_map)} agents configured:")
        for number, config in agent_map.items():
            print(f"   📱 {number} → Flow: {config.get('flow_id', 'N/A')}")
    else:
        print("💡 Currently using single static agent")
        print("   To enable multi-agent: Set AGENT_MAPPINGS environment variable")

    print("="*60 + "\n")

    # Railway sets PORT environment variable
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
