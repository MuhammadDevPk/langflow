"""
Twilio-Langflow Bridge (Production-Ready with Enhanced Error Handling)
Supports both single-agent (static) and multi-agent (dynamic) modes
"""

from flask import Flask, request, jsonify
import requests
import os
import json
import logging
import re
from datetime import datetime
from twilio.twiml.voice_response import VoiceResponse, Gather

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Base Configuration
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Default agent (single static agent)
DEFAULT_FLOW_ID = os.getenv("DEFAULT_FLOW_ID", "9c7c075b-85da-4dfd-ae0c-bcb322851b04")
DEFAULT_VOICE_INTRO = os.getenv("DEFAULT_VOICE_INTRO", "Hi, this is your Voxie agent. How can I help you today?")
DEFAULT_VOICE_TYPE = os.getenv("DEFAULT_VOICE_TYPE", "Polly.Matthew")

# Dynamic Agent Mapping (optional - for multi-agent mode)
AGENT_MAPPINGS = os.getenv("AGENT_MAPPINGS", "{}")

# Parse agent mappings
try:
    agent_map = json.loads(AGENT_MAPPINGS)
    if agent_map:
        logger.info(f"✅ Multi-agent mode: {len(agent_map)} agents configured")
    else:
        logger.info("✅ Single-agent mode: Using default agent")
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"❌ Error parsing AGENT_MAPPINGS: {e}")
    agent_map = {}

def get_agent_config(twilio_number):
    """
    Get agent configuration based on Twilio number called.
    Returns: (flow_id, intro_message, voice_type)
    """
    try:
        # If no mappings configured, use default
        if not agent_map:
            logger.debug(f"Using default agent for {twilio_number}")
            return (DEFAULT_FLOW_ID, DEFAULT_VOICE_INTRO, DEFAULT_VOICE_TYPE)

        # Clean phone number format
        clean_number = twilio_number.replace("+", "").replace("-", "").replace(" ", "")

        # Check if this number has a custom agent mapped
        if clean_number in agent_map:
            config = agent_map[clean_number]
            logger.info(f"✅ Found agent mapping for {clean_number}")
            return (
                config.get("flow_id", DEFAULT_FLOW_ID),
                config.get("intro", DEFAULT_VOICE_INTRO),
                config.get("voice", DEFAULT_VOICE_TYPE)
            )

        # Try with + prefix
        if twilio_number in agent_map:
            config = agent_map[twilio_number]
            logger.info(f"✅ Found agent mapping for {twilio_number}")
            return (
                config.get("flow_id", DEFAULT_FLOW_ID),
                config.get("intro", DEFAULT_VOICE_INTRO),
                config.get("voice", DEFAULT_VOICE_TYPE)
            )

        # Fallback to default
        logger.info(f"⚠️  No mapping found for {twilio_number}, using default agent")
        return (DEFAULT_FLOW_ID, DEFAULT_VOICE_INTRO, DEFAULT_VOICE_TYPE)

    except Exception as e:
        logger.error(f"❌ Error in get_agent_config: {e}", exc_info=True)
        return (DEFAULT_FLOW_ID, DEFAULT_VOICE_INTRO, DEFAULT_VOICE_TYPE)

def call_langflow_api(flow_id, speech, caller_number):
    """
    Call Langflow API and return agent response.
    Enhanced with detailed error handling and logging.
    """
    try:
        # Validate inputs
        if not flow_id:
            raise ValueError("Flow ID is empty")
        if not speech:
            raise ValueError("Speech input is empty")

        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if LANGFLOW_API_KEY:
            headers["x-api-key"] = LANGFLOW_API_KEY

        # Prepare payload
        lf_payload = {
            "input_value": speech,
            "output_type": "chat",
            "input_type": "chat",
            "session_id": caller_number  # Maintain conversation per caller
        }

        api_url = f"{LANGFLOW_URL}/api/v1/run/{flow_id}"
        logger.info(f"🔄 Calling Langflow API: {api_url}")
        logger.debug(f"Payload: {lf_payload}")

        # Make API call with timeout
        lf_response = requests.post(
            api_url,
            json=lf_payload,
            headers=headers,
            timeout=20  # Increased timeout for complex agents
        )

        # Log response status
        logger.info(f"📡 Langflow API status: {lf_response.status_code}")

        if lf_response.status_code == 200:
            response_data = lf_response.json()
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")

            # Extract agent reply with multiple fallback strategies
            agent_reply = extract_agent_reply(response_data)

            if agent_reply:
                logger.info(f"✅ Agent replied: {agent_reply[:100]}...")
                return {"success": True, "reply": agent_reply}
            else:
                logger.error("❌ No reply found in response")
                return {
                    "success": False,
                    "error": "Empty response from agent",
                    "reply": "I processed your request, but I'm having trouble formulating a response. Could you try again?"
                }

        elif lf_response.status_code == 401:
            logger.error("❌ Authentication failed - Invalid API key")
            return {
                "success": False,
                "error": "Authentication failed",
                "reply": "I'm having authentication issues. Please contact support."
            }

        elif lf_response.status_code == 404:
            logger.error(f"❌ Flow not found: {flow_id}")
            return {
                "success": False,
                "error": "Flow not found",
                "reply": "The agent you're trying to reach is not available. Please contact support."
            }

        else:
            logger.error(f"❌ API error {lf_response.status_code}: {lf_response.text}")
            return {
                "success": False,
                "error": f"API error {lf_response.status_code}",
                "reply": "I'm having trouble connecting to my system. Please try again in a moment."
            }

    except requests.exceptions.Timeout:
        logger.error("⏱️  Request timeout")
        return {
            "success": False,
            "error": "Timeout",
            "reply": "Sorry, I'm taking too long to respond. Please call back in a moment."
        }

    except requests.exceptions.ConnectionError as e:
        logger.error(f"🔌 Connection error: {e}")
        return {
            "success": False,
            "error": "Connection error",
            "reply": "I'm having trouble connecting to my system. Please try again later."
        }

    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "reply": "I encountered a technical issue. Please try again."
        }

def clean_agent_response(text: str) -> str:
    """
    Clean the agent response by removing JSON blocks and internal thoughts.
    """
    if not text:
        return ""
    # Remove Internal Thought [State: ...]
    text = re.sub(r'\[State:.*?\]', '', text, flags=re.DOTALL)
    # Remove JSON blocks (```json ... ```)
    text = re.sub(r'```json.*?```', '', text, flags=re.DOTALL)
    # Remove raw JSON at the end
    text = re.sub(r'\s*\{[\s\S]*?\}\s*$', '', text)
    return text.strip()

def extract_agent_reply(response_data):
    """
    Extract agent reply from Langflow response.
    """
    try:
        # Strategy 1: outputs -> first item -> outputs -> results -> message -> text
        if isinstance(response_data.get('outputs'), list) and len(response_data['outputs']) > 0:
            first_output = response_data['outputs'][0]
            if 'outputs' in first_output and len(first_output['outputs']) > 0:
                results = first_output['outputs'][0].get('results', {})
                message = results.get('message', {})
                
                if isinstance(message, dict):
                    text = message.get('text', '')
                    return clean_agent_response(text)
                elif isinstance(message, str):
                    return clean_agent_response(message)

        # Strategy 2: outputs -> text (simple structure)
        if 'outputs' in response_data:
            outputs = response_data['outputs']
            if isinstance(outputs, dict):
                text = outputs.get('text') or outputs.get('response') or outputs.get('message')
                if text:
                    return clean_agent_response(text)

        # Strategy 3: direct text/message field
        text = response_data.get('text') or response_data.get('message') or response_data.get('response')
        if text:
            return clean_agent_response(text)

        # Strategy 4: Check for messages array
        if 'messages' in response_data and isinstance(response_data['messages'], list):
            if len(response_data['messages']) > 0:
                last_message = response_data['messages'][-1]
                text = last_message.get('message') or last_message.get('text')
                if text:
                    return clean_agent_response(text)

        logger.warning("⚠️  Could not extract reply from response")
        return None

    except Exception as e:
        logger.error(f"Error extracting reply: {e}", exc_info=True)
        return None

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with service info."""
    return jsonify({
        "status": "running",
        "service": "Twilio-Langflow Bridge",
        "version": "2.0",
        "mode": "multi-agent" if agent_map else "single-agent",
        "agents_configured": len(agent_map) if agent_map else 1,
        "debug_mode": DEBUG_MODE,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/voice', methods=['POST'])
def voice_webhook():
    """
    Handle incoming Twilio voice calls with dynamic agent routing.
    Enhanced with comprehensive error handling and logging.
    """
    try:
        # Get call information
        called_number = request.values.get('To', '')
        caller_number = request.values.get('From', '')
        speech = request.values.get('SpeechResult', '').strip()
        call_sid = request.values.get('CallSid', 'unknown')

        logger.info(f"📞 CALL [{call_sid}] From: {caller_number} To: {called_number}")

        # Get agent configuration
        flow_id, voice_intro, voice_type = get_agent_config(called_number)
        logger.info(f"🤖 CALL [{call_sid}] Using Flow: {flow_id}, Voice: {voice_type}")

        if not speech:
            # First call: Prompt user to speak
            logger.info(f"🎙️  CALL [{call_sid}] Sending initial greeting")
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

        # User spoke something
        logger.info(f"💬 CALL [{call_sid}] User said: {speech}")

        # Call Langflow API
        result = call_langflow_api(flow_id, speech, caller_number)

        if result["success"]:
            agent_reply = result["reply"]
            logger.info(f"✅ CALL [{call_sid}] Agent replied successfully")
        else:
            agent_reply = result["reply"]
            logger.error(f"❌ CALL [{call_sid}] Error: {result.get('error', 'Unknown')}")

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

        logger.info(f"📤 CALL [{call_sid}] Response sent")
        return str(resp)

    except Exception as e:
        logger.error(f"💥 Unexpected error in voice_webhook: {e}", exc_info=True)

        # Return generic error message to caller
        resp = VoiceResponse()
        resp.say(
            "I'm experiencing technical difficulties. Please try calling again later.",
            voice=DEFAULT_VOICE_TYPE
        )
        resp.hangup()
        return str(resp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed status."""
    try:
        # Check Langflow connectivity
        langflow_status = "unknown"
        try:
            health_response = requests.get(f"{LANGFLOW_URL}/health", timeout=5)
            langflow_status = "connected" if health_response.status_code == 200 else "error"
        except Exception as e:
            langflow_status = f"disconnected: {str(e)}"

        return jsonify({
            "status": "healthy",
            "service": "twilio-bridge",
            "default_flow_id": DEFAULT_FLOW_ID,
            "mode": "multi-agent" if agent_map else "single-agent",
            "agents_mapped": len(agent_map),
            "langflow_url": LANGFLOW_URL,
            "langflow_status": langflow_status,
            "debug_mode": DEBUG_MODE,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/agents', methods=['GET'])
def list_agents():
    """List all configured agents."""
    try:
        return jsonify({
            "mode": "multi-agent" if agent_map else "single-agent",
            "default_agent": {
                "flow_id": DEFAULT_FLOW_ID,
                "intro": DEFAULT_VOICE_INTRO,
                "voice": DEFAULT_VOICE_TYPE
            },
            "mapped_agents": agent_map if agent_map else {},
            "total_agents": len(agent_map) if agent_map else 1
        }), 200
    except Exception as e:
        logger.error(f"Error listing agents: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint - only enabled if DEBUG_MODE=true."""
    if not DEBUG_MODE:
        return jsonify({"error": "Debug mode is disabled"}), 403

    return jsonify({
        "env_vars": {
            "LANGFLOW_URL": LANGFLOW_URL,
            "DEFAULT_FLOW_ID": DEFAULT_FLOW_ID,
            "DEFAULT_VOICE_TYPE": DEFAULT_VOICE_TYPE,
            "AGENT_MAPPINGS": AGENT_MAPPINGS,
            "DEBUG_MODE": DEBUG_MODE
        },
        "agent_map": agent_map,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/voice", "/health", "/agents"]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {e}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

if __name__ == '__main__':
    # Startup validation
    if not DEFAULT_FLOW_ID:
        logger.error("❌ ERROR: DEFAULT_FLOW_ID not set!")
        exit(1)

    logger.info("\n" + "="*60)
    logger.info("🚀 Twilio-Langflow Bridge Starting...")
    logger.info("="*60)
    logger.info(f"📍 Langflow URL: {LANGFLOW_URL}")
    logger.info(f"🤖 Default Flow ID: {DEFAULT_FLOW_ID}")
    logger.info(f"📞 Mode: {'Multi-Agent' if agent_map else 'Single-Agent'}")
    logger.info(f"🐛 Debug Mode: {DEBUG_MODE}")

    if agent_map:
        logger.info(f"✅ {len(agent_map)} agents configured:")
        for number, config in agent_map.items():
            logger.info(f"   📱 {number} → Flow: {config.get('flow_id', 'N/A')}")
    else:
        logger.info("💡 Single static agent mode")

    logger.info("="*60 + "\n")

    # Get port from environment (Railway sets this)
    port = int(os.getenv("PORT", 5000))

    # Start Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
