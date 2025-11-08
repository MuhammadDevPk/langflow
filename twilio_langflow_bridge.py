from flask import Flask, request
import requests
import os
import ngrok
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

# Configuration - Set these via environment variables or update here
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")
FLOW_ID = os.getenv("FLOW_ID", "9c7c075b-85da-4dfd-ae0c-bcb322851b04")  # Set your agent's flow_id
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "356U1FngJ7bKRyDVv0Zgyp2yoBa_4MCdPpo4iFLqjVY7GPvkQ")  # Get from ngrok.com after signup
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "sk-SlAQGa_sWQnLcJHEHW2WLIFkv17xjpGLdj3EhRV5bmY")  # Optional: if your Langflow requires auth

# Voice settings
VOICE_INTRO = os.getenv("VOICE_INTRO", "Hi, this is your Voxie agent. How can I help you today?")
VOICE_TYPE = os.getenv("VOICE_TYPE", "Polly.Matthew")  # Twilio voice options: man, woman, alice, or Polly.*

@app.route('/', methods=['GET'])
def greet():
    return "Hello, World!"

@app.route('/voice', methods=['POST'])
def voice_webhook():
    """Handle incoming Twilio voice calls and interact with Langflow agent."""
    # Get incoming transcribed speech (from Twilio Gather)
    speech = request.values.get('SpeechResult', '').strip()

    if not speech:
        # First call: Prompt user to speak
        resp = VoiceResponse()
        gather = Gather(
            input='speech',
            action='/voice',  # Loops back to this endpoint
            method='POST',
            speech_timeout='auto',  # Auto-detect end of speech
            language='en-US',
            speech_model='phone_call'  # Optimized for phone audio
        )
        gather.say(VOICE_INTRO, voice=VOICE_TYPE)
        resp.append(gather)
        resp.redirect('/voice')  # Fallback if no speech
        return str(resp)

    # Call Langflow API for agent response
    try:
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if LANGFLOW_API_KEY:
            headers["x-api-key"] = LANGFLOW_API_KEY

        # Langflow 1.6.5 API format - using /api/v1/run for better output handling
        # Alternative endpoint: /api/v1/process/{FLOW_ID}
        lf_payload = {
            "input_value": speech,
            "output_type": "chat",
            "input_type": "chat",
        }

        lf_response = requests.post(
            f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
            json=lf_payload,
            headers=headers,
            timeout=15
        )

        if lf_response.status_code == 200:
            response_data = lf_response.json()

            # Try multiple possible response structures
            # Structure 1: outputs -> first item -> outputs -> first item -> results -> message -> text
            if isinstance(response_data.get('outputs'), list) and len(response_data['outputs']) > 0:
                first_output = response_data['outputs'][0]
                if 'outputs' in first_output and len(first_output['outputs']) > 0:
                    results = first_output['outputs'][0].get('results', {})
                    message = results.get('message', {})
                    agent_reply = message.get('text', '')
                else:
                    agent_reply = first_output.get('message', {}).get('text', '')
            # Structure 2: outputs -> text (simple structure)
            elif 'outputs' in response_data:
                outputs = response_data['outputs']
                if isinstance(outputs, dict):
                    agent_reply = outputs.get('text', outputs.get('response', outputs.get('message', '')))
                else:
                    agent_reply = str(outputs)
            # Structure 3: direct text/message field
            else:
                agent_reply = response_data.get('text', response_data.get('message', ''))

            # Fallback if no reply found
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
    resp.say(agent_reply, voice=VOICE_TYPE, language='en-US')

    # Ask if user wants to continue or end call
    gather = Gather(
        input='speech',
        action='/voice',
        method='POST',
        speech_timeout='3',
        language='en-US',
        speech_model='phone_call'
    )
    gather.say("Is there anything else I can help you with?", voice=VOICE_TYPE)
    resp.append(gather)

    # If no response, end gracefully
    resp.say("Thank you for calling. Goodbye!", voice=VOICE_TYPE)
    resp.hangup()

    return str(resp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "flow_id": FLOW_ID}, 200

def start_ngrok_tunnel():
    """Start ngrok tunnel and return public URL."""
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)

    # Create ngrok tunnel
    listener = ngrok.forward(5000, authtoken_from_env=True)
    print("\n" + "="*60)
    print("🚀 Ngrok tunnel started!")
    print(f"📞 Public URL: {listener.url()}")
    print("="*60)
    print("\n⚙️  Next steps:")
    print("1. Copy the public URL above")
    print("2. Go to Twilio Console: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("3. Select your phone number")
    print("4. Under 'Voice Configuration' -> 'A call comes in'")
    print(f"5. Set webhook URL to: {listener.url()}/voice")
    print("6. Set HTTP method to: POST")
    print("7. Save your changes")
    print("\n📱 Call your Twilio number to test!\n")

    return listener.url()

if __name__ == '__main__':
    # Validate configuration
    if not FLOW_ID:
        print("❌ ERROR: FLOW_ID not set!")
        print("Please set FLOW_ID environment variable or update it in the code.")
        print("\nTo get your FLOW_ID:")
        print("1. Open Langflow UI (http://localhost:7860)")
        print("2. Open your agent flow")
        print("3. Look at the URL - the ID is after '/flow/'")
        print("   Example: http://localhost:7860/flow/abc-123-def -> FLOW_ID is 'abc-123-def'")
        exit(1)

    print("✅ Configuration loaded:")
    print(f"   Langflow URL: {LANGFLOW_URL}")
    print(f"   Flow ID: {FLOW_ID}")

    # Start ngrok tunnel
    try:
        public_url = start_ngrok_tunnel()
    except Exception as e:
        print(f"⚠️  Warning: Could not start ngrok tunnel: {e}")
        print("You'll need to manually expose your server or run ngrok separately.")
        print("If you have ngrok CLI installed, run: ngrok http 5000")

    # Start Flask app
    print("\n🌐 Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False when using ngrok