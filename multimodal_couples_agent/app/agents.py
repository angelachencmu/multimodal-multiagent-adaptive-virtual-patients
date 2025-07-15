
from typing import Dict, Any, Optional
import re
import logging


from openai import OpenAI
import os


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_TOKENS = 150
TEMPERATURE = 0.8
MODEL_NAME = "gpt-4o-mini"

AGENT_PROFILES = {  
    "Alpha": {
        "role": "pursuer",
        "base_communication": "pressures, nags, criticizes, demands, escalates quickly, uses direct language",
        "base_emotion": "sad",
        "description": "Alpha tends to criticize, demand, and escalate when upset. Alpha is more vocal, direct, and confrontational. Alpha takes initiative in conversations and is not afraid to express strong opinions."
    },
    "Beta": {
        "role": "withdrawer",
        "base_communication": "withdraws, becomes silent, defends, resists apologizing, uses passive-aggressive language",
        "base_emotion": "contempt",
        "description": "Beta tends to withdraw, become silent, or defend themselves when pressured. Beta is more reserved, indirect, and avoids direct confrontation. Beta often responds with sarcasm, eye rolls, or minimal engagement."
    }
}

STAGE_DEFINITIONS = {
    "Greeting": {
        "description": "Session beginning with small talk (eg. hi, hello, good to see you, how was your week?)",
        "Alpha_behavior": "Very brief greeting only. eg. Hi, hello. Keep responses short. Let your tone subtly reflect your emotional state or attitude about being in therapy. don't elaborate or bring up problems unless specifically asked by trainee. you can show some negative emotion related to your character or the situation.",
        "Beta_behavior": "Very brief, reserved greeting. Minimal engagement, short response. May seem uncomfortable or guarded about being in therapy."
    },
    "Problem Raising": {
        "description": "One partner raises an issue or concern that’s bothering them, and they may provide examples or describe specific situations.",
        "Alpha_behavior": "Takes the lead in bringing up issues. Direct, critical, and focused on what Beta did wrong. Uses 'he always' or 'he never' statements. Provide very detailed examples or scenarios of what Beta did wrong.",
        "Beta_behavior": "Becomes defensive or tries to minimize issues. Counter-complain or shut down. Avoids taking responsibility."
    },
    "Escalation": {
        "description": "Demander escalates the situation and criticizes the other partner",
        "Alpha_behavior": "Becomes more demanding and critical. Uses 'you always' and 'you never' statements. May raise voice or interrupt. Shows desperation under the anger - feels unheard and panicked. Pressures for immediate answers or changes. May bring up past incidents as evidence. IMPORTANT: Even when talking to the therapist, make statements that contradict or challenge what Beta might say. Be critical of Beta's perspective or actions.",
        "Beta_behavior": "Withdraws further or becomes defensive. May shut down emotionally, use sarcasm, or make contemptuous remarks. Shows hurt and overwhelm. May counter-attack with their own complaints or go completely silent. Feels criticized and under attack. IMPORTANT: Even when talking to the therapist, defend yourself or contradict Alpha's claims. Be dismissive of Alpha's perspective or minimize their concerns. When Alpha is talking to you, you should respond to them directly, not to the therapist."
    },
    "De-escalation": {
        "description": "Trainee reframes the situation, validates each side, and proposes new perspectives",
        "Alpha_behavior": "Initially resistant to reframing. May argue with therapist's perspective. Slowly begins to consider alternative viewpoints if approached skillfully.",
        "Beta_behavior": "May be more receptive to validation but still guarded. Cautiously opens up if feeling understood and safe."
    },
    "Enactment": {
        "description": "One partner directly expresses and communicates their feelings to the other partner.",
        "Alpha_behavior": "Begins to soften demands. Directly express feelings to Beta. May acknowledge Beta's perspective. Shows some vulnerability under the anger. Less critical tone and more focus on primary emotions. eg. I'm feeling hurt, angry, and sad. eg. I didn’t mean to…, I need you to… ",
        "Beta_behavior": "Becomes more engaged and open. May share feelings more directly. Shows willingness to participate in solutions."
    },
    "Wrap-up": {
        "description": "Session conclusion with summaries and future planning",
        "Alpha_behavior": "May express some hope or relief. Acknowledges progress made. Still concerned about follow-through on agreements.",
        "Beta_behavior": "More relaxed and open. May express gratitude for feeling heard. Shows cautious optimism about working on issues."
    }
}

EMOTION_TRANSITIONS = {
    "Alpha": {
        "Greeting": "neutral",
        "Problem Raising": "sad",
        "Escalation": "frustrated_angry",  
        "De-escalation": "hopeful",
        "Enactment": "vulnerable",  
        "Wrap-up": "relieved"
    },
    "Beta": {
        "Greeting": "neutral", 
        "Problem Raising": "defensive",
        "Escalation": "sad", 
        "De-escalation": "cautious",
        "Enactment": "open",
        "Wrap-up": "calm"
    }
}

def get_current_emotion(agent_name: str, stage: str) -> str:
    return EMOTION_TRANSITIONS.get(agent_name, {}).get(stage, AGENT_PROFILES[agent_name]["base_emotion"])


def get_stage_behavior(agent_name: str, stage: str) -> str:

    stage_info = STAGE_DEFINITIONS.get(stage, {})
    return stage_info.get(f"{agent_name}_behavior", "Respond according to your basic communication pattern.")


def build_agent_prompt(
    agent_name: str, 
    session: Dict[str, Any], 
    last_speaker: str, 
    last_message: str, 
    difficulty: str = "normal", 
    is_directly_addressed: bool = False, 
    other_agent_response: Optional[str] = None, 
    agent_to_agent_info: Optional[Dict[str, Any]] = None
) -> str:
    profile = AGENT_PROFILES[agent_name]
    stage = session.get("stage", "Greeting")
    scenario = session.get("scenario", "A couple discusses their extreme trust issues when they are hanging out with members of the opposite sex without each other present.")
    history = session.get("history", [])
    difficulty = session.get("difficulty", difficulty)
    emotion = get_current_emotion(agent_name, stage)
    stage_behavior = get_stage_behavior(agent_name, stage)
    stage_description = STAGE_DEFINITIONS.get(stage, {}).get("description", "")
    
    # Build conversation history showing all participants
    history_text = "\n".join([f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in history[-5:]])
    
    if difficulty == "easy":
        resistance_instruction = "You are somewhat open to the trainee's interventions and show some flexibility."
    elif difficulty == "hard":
        resistance_instruction = "You are highly resistant to the trainee's interventions, very slow to change, and deeply entrenched in your patterns."
    else:
        resistance_instruction = "You respond realistically to the trainee's interventions with moderate resistance."
    
    # guidance variables
    interaction_guidance = ""
    greeting_guidance = ""
    escalation_guidance = ""
    repetition_guidance = ""
    
    # Check for agent-to-agent communication 
    if agent_to_agent_info and agent_to_agent_info.get('is_agent_to_agent'):
        speaker_agent = agent_to_agent_info.get('speaker_agent')
        target_agent = agent_to_agent_info.get('target_agent')
        
        if agent_name == speaker_agent:
            # This agent should speak to the other agent
            response_context = f"The trainee (therapist) just asked you to speak directly to {target_agent}: \"{last_message}\""
            interaction_guidance = f"""CRITICAL: The therapist has asked you to speak DIRECTLY to {target_agent}. 
            
ADDRESS {target_agent} DIRECTLY using "you" language.
This is a direct conversation with your partner, not with the therapist.
Express your feelings, thoughts, or needs directly to {target_agent}.
Use phrases like "I want you to know...", "I feel... when you...", "I need you to..."
Stay true to your communication pattern and current emotional state while speaking to {target_agent}."""
        elif agent_name == target_agent:
            # This agent should wait for the other agent to speak first
            response_context = f"The trainee (therapist) just asked {speaker_agent} to speak to you: \"{last_message}\""
            interaction_guidance = f"""IMPORTANT: The therapist has asked {speaker_agent} to speak to you directly.
            
Wait for {speaker_agent} to speak first, then respond to what they say.
You will respond to {speaker_agent} in the next turn after they speak.
For now, acknowledge the therapist's instruction with a brief response like "Okay" or stay silent."""
        else:
            # fallback (shouldn't happen)
            response_context = f"The trainee (therapist) just said: \"{last_message}\""
            interaction_guidance = "Respond to the therapist appropriately."
    
    # Regular interaction guidance 
    else:
        
        if last_speaker == "trainee":
            if is_directly_addressed:
                response_context = f"The trainee (therapist) just addressed you directly: \"{last_message}\""
                interaction_guidance = f"""CRITICAL: The therapist is speaking ONLY to you, {agent_name}. This is a private conversation between you and the therapist.
                
DO NOT address or talk to your partner ({('Beta' if agent_name == 'Alpha' else 'Alpha')}). 
RESPOND DIRECTLY TO THE THERAPIST.
Use "I" statements when talking about yourself.
If you mention your partner, refer to their name (e.g., "Alpha" or "Beta" or "my partner").
Stay true to your communication pattern and current emotional state while responding to the therapist's intervention."""
            else:
                response_context = f"The trainee (therapist) just said: \"{last_message}\""
                interaction_guidance = f"""IMPORTANT: The therapist is speaking to both of you in the session. 
                
RESPOND TO THE THERAPIST, not to your partner.
Use "I" statements when talking about yourself.
If you mention your partner, refer to their name (e.g., "Alpha" or "Beta" or "my partner") rather than "you".
Stay true to your communication pattern and current emotional state while responding to the therapist's question or intervention."""
        elif last_speaker == "Alpha" and agent_name == "Beta":
            response_context = f"Alpha just said: \"{last_message}\""
            interaction_guidance = """IMPORTANT: Alpha just spoke to you directly. 
            
RESPOND TO ALPHA DIRECTLY using "you" language.
This is a direct conversation between you and Alpha.
React to what Alpha just said to you with your typical communication pattern.
Use phrases like "I hear you saying...", "When you say that...", "I feel... when you..."
Stay true to your character as Beta (withdrawer) - you may defend, withdraw, or respond based on what Alpha said."""
        elif last_speaker == "Beta" and agent_name == "Alpha":
            response_context = f"Beta just said: \"{last_message}\""
            interaction_guidance = """IMPORTANT: Beta just spoke to you directly.
            
RESPOND TO BETA DIRECTLY using "you" language.
This is a direct conversation between you and Beta.
React to what Beta just said to you with your typical communication pattern.
Use phrases like "I want you to understand...", "When you say that...", "I need you to..."
Stay true to your character as Alpha (pursuer) - you may press your point, make demands, or escalate based on what Beta said."""
        else:
            response_context = f"{last_speaker} just said: \"{last_message}\""
            interaction_guidance = "Respond appropriately while maintaining your character."
    
    # specific guidance for different types of greetings
    if stage == "Greeting" and last_speaker == "trainee":
        trainee_message_lower = last_message.lower().strip()
        
        # Check if it's just a simple hello/hi (actual simple greeting)
        simple_greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        is_simple_greeting = any(greeting == trainee_message_lower or trainee_message_lower.startswith(greeting + " ") for greeting in simple_greetings)
        
        # Check if trainee is asking about how they're doing (therapeutic opening)
        therapeutic_openings = ["how are you", "how's it going", "how are things", "how's everything", "how have you been", "how are you doing", "how are you both"]
        is_therapeutic_opening = any(opening in trainee_message_lower for opening in therapeutic_openings)
        
        if is_simple_greeting and not is_therapeutic_opening:
            greeting_guidance = f"""
SIMPLE GREETING RESPONSE: The trainee just gave a simple hello. Respond with a brief, simple greeting in return. Keep it short, just 1-2 sentences maximum. Examples: "Hi", "Hello", "Good to see you". Don't elaborate or bring up problems yet.
"""
        elif is_therapeutic_opening:
            if agent_name == "Alpha":
                greeting_guidance = f"""
THERAPEUTIC OPENING RESPONSE: The trainee is asking how you're doing. As Alpha (the pursuer), this is your opportunity to naturally mention the relationship problems that brought you to therapy. Be honest about your struggles. Examples: "Not great, honestly...", "We've been having some real problems...", "Things have been really tough between us..."
"""
            else:  # Beta
                greeting_guidance = f"""
THERAPEUTIC OPENING RESPONSE: The trainee is asking how you're doing. As Beta (the withdrawer), be more reserved or deflective, but show some discomfort about the situation. Examples: "I'm fine, I guess...", "Could be better...", "We're here, so..."
"""
    
    # specific guidance for escalation stage
    if (stage == "Escalation" and last_speaker == "trainee" and 
        not (agent_to_agent_info and agent_to_agent_info.get('is_agent_to_agent'))):
        escalation_guidance = f"""
ESCALATION STAGE GUIDANCE: The conflict is intensifying. Even when responding to the therapist, you should:

As {agent_name}:
- {("Be critical of Beta's perspective or actions when you mention them" if agent_name == "Alpha" else "Be dismissive of Alpha's concerns or defend against their accusations")}
- {("Show desperation and urgency - you need Beta to understand NOW" if agent_name == "Alpha" else "Show you're overwhelmed and under attack - defend yourself")}
- {("Bring up past incidents as evidence of Beta's patterns" if agent_name == "Alpha" else "Counter-attack with your own complaints about Alpha if pushed")}
- Make statements that naturally contradict or challenge what your partner might say
- Your emotional state is highly charged - let that show in your response
- When mentioning your partner, use their name ("Alpha" or "Beta") since you're speaking to the therapist
"""
    
    #guidance to prevent repetition if another agent has already responded
    if other_agent_response:
        other_agent_name = "Alpha" if agent_name == "Beta" else "Beta"
        
        # Check if this is a simple greeting scenario where repetition is acceptable
        is_simple_greeting_stage = (stage == "Greeting" and last_speaker == "trainee")
        other_response_is_brief_greeting = (
            len(other_agent_response.split()) <= 3 and 
            any(greeting in other_agent_response.lower() for greeting in ["hi", "hello", "hey", "good"])
        )
        
        if is_simple_greeting_stage and other_response_is_brief_greeting:
            repetition_guidance = f"""
SIMPLE GREETING NOTE: {other_agent_name} gave a brief greeting: "{other_agent_response}"
For simple greetings, it's fine to also give a brief greeting like "Hi", "Hello", or "Hey". Keep it short and natural.
"""
        else:
            repetition_guidance = f"""
IMPORTANT: AVOID REPETITION: {other_agent_name} just said: "{other_agent_response}"
Do NOT repeat what {other_agent_name} has already said. Give a different response that reflects your unique character and communication style. If {other_agent_name} already covered the main point, either:
1. Give a brief, different response (like "Yeah" or "I agree")
2. Add a different perspective or emotion
3. Express your character's typical reaction to what {other_agent_name} said
"""

    prompt = f"""
You are {agent_name}, a member of a couple in therapy. Your communication pattern is: {profile['base_communication']}.
Your current emotion is: {emotion}.
The scenario is: {scenario}

CURRENT STAGE: {stage} - {stage_description}
STAGE-SPECIFIC BEHAVIOR: {stage_behavior}

{profile['description']}
{resistance_instruction}

Recent conversation:
{history_text}

{response_context}

{interaction_guidance}
{greeting_guidance}
{escalation_guidance}
{repetition_guidance}

IMPORTANT: Follow your stage-specific behavior while maintaining your core character. Stay true to your role, emotion, and stage-appropriate behavior. Keep responses concise and realistic. If responding to your partner, engage naturally in the couple dynamic according to the current stage. 

RESPONSE LENGTH: Speak like a REAL PERSON in a relationship, not like a therapist or textbook. Keep your responses brief and natural. For simple greetings, respond with just 1-2 sentences maximum.

UNIQUENESS: Your response should be distinctly different from the other agent's response. Each agent has a unique communication style and emotional state.
"""
    return prompt

def get_agent_response(
    agent_name: str, 
    session: Dict[str, Any], 
    last_speaker: str, 
    last_message: str, 
    is_directly_addressed: bool = False, 
    other_agent_response: Optional[str] = None, 
    agent_to_agent_info: Optional[Dict[str, Any]] = None
) -> str:
    """Generate a response from the specified agent based on the session context.
    
        agent_name: Name of the agent ("Alpha" or "Beta")
        session: Current session state and history
        last_speaker: Who spoke last ("trainee", "Alpha", or "Beta")
        last_message: The last message spoken
        is_directly_addressed: Whether this agent was directly addressed
        other_agent_response: Response from the other agent (if any)
        agent_to_agent_info: Information about agent-to-agent communication
        
    It will return:
        The agent's response as a string
        
    """
    difficulty = session.get("difficulty", "normal")
    prompt = build_agent_prompt(
        agent_name, session, last_speaker, last_message, 
        difficulty, is_directly_addressed, other_agent_response, agent_to_agent_info
    )
    
    # check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are simulating a couple therapy session where partners can interact with both the therapist and each other. Follow EFT therapy stages and respond authentically to each stage. Keep responses natural. DO NOT include the character name or any prefix in your response - just provide the actual spoken words."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.8,
        )
        content = response.choices[0].message.content
        if content:
            content = content.strip()
            # remove agent name prefixes if they exist, so agent don't speak out their name in the response
            if content.startswith(f"{agent_name}: "):
                content = content[len(f"{agent_name}: "):].strip()
            elif content.startswith(f"{agent_name}:"):
                content = content[len(f"{agent_name}:"):].strip()
        return content if content else ""
        
    except Exception as e:
        logger.error(f"Error generating response for {agent_name}: {str(e)}")
        # Return a fallback response based on agent characteristics
        profile = AGENT_PROFILES.get(agent_name, {})
        base_emotion = profile.get("base_emotion", "neutral")
        if base_emotion == "sad":
            return "I... I don't know what to say right now."
        else:
            return "...uhm"

def detect_addressed_agent(message: str) -> str:
    """Detect if the trainee is addressing a specific agent by name.
    
    Args:
        message: The message from the trainee
        
    Returns:
        "Alpha", "Beta", or "both" depending on who is addressed
    """
    message_lower = message.lower().strip()
    
    # Check if message starts with agent name
    if message_lower.startswith("alpha,") or message_lower.startswith("alpha "):
        return "Alpha"
    elif message_lower.startswith("beta,") or message_lower.startswith("beta "):
        return "Beta"
    
    # Check if agent name appears early in the message with direct address indicators
    words = message_lower.split()
    if len(words) > 0:
        if words[0] == "alpha" and len(words) > 1:
            return "Alpha"
        elif words[0] == "beta" and len(words) > 1:
            return "Beta"
    
    # Check for direct addressing patterns anywhere in the message
    if "alpha," in message_lower or " alpha " in message_lower:
   
        if re.search(r'\balpha[,\s]', message_lower):
            return "Alpha"
    elif "beta," in message_lower or " beta " in message_lower:
        if re.search(r'\bbeta[,\s]', message_lower):
            return "Beta"
    
    return "both"



def detect_agent_to_agent_instruction(message: str) -> Dict[str, Any]:
    message_lower = message.lower().strip()
    
    # Indicators for Alpha talking to Beta
    alpha_to_beta_patterns = [
        r'alpha.*tell.*beta',
        r'alpha.*say.*to.*beta',
        r'alpha.*share.*with.*beta',
        r'alpha.*express.*to.*beta',
        r'alpha.*talk.*to.*beta',
        r'alpha.*speak.*to.*beta',
        r'alpha.*can you tell beta',
        r'alpha.*let beta know',
        r'alpha.*turn to beta',
        r'alpha.*look at beta'
    ]
    
    # Indicators for Beta talking to Alpha
    beta_to_alpha_patterns = [
        r'beta.*tell.*alpha',
        r'beta.*say.*to.*alpha',
        r'beta.*share.*with.*alpha',
        r'beta.*express.*to.*alpha',
        r'beta.*talk.*to.*alpha',
        r'beta.*speak.*to.*alpha',
        r'beta.*can you tell alpha',
        r'beta.*let alpha know',
        r'beta.*turn to alpha',
        r'beta.*look at alpha'
    ]
    
    # Check for Alpha to Beta patterns
    for pattern in alpha_to_beta_patterns:
        if re.search(pattern, message_lower):
            return {
                'is_agent_to_agent': True,
                'speaker_agent': 'Alpha',
                'target_agent': 'Beta'
            }
    
    # Check for Beta to Alpha patterns
    for pattern in beta_to_alpha_patterns:
        if re.search(pattern, message_lower):
            return {
                'is_agent_to_agent': True,
                'speaker_agent': 'Beta',
                'target_agent': 'Alpha'
            }
    
    return {
        'is_agent_to_agent': False,
        'speaker_agent': None,
        'target_agent': None
    }

def _handle_agent_to_agent_communication(
    session: Dict[str, Any], 
    last_speaker: str, 
    last_message: str, 
    agent_to_agent_info: Dict[str, Any]
) -> Optional[list]:
    """Handle direct agent-to-agent communication.
    
    Returns:
        List of responses if handled, None if should fall back to regular handling
    """
    speaker_agent = agent_to_agent_info.get('speaker_agent')
    target_agent = agent_to_agent_info.get('target_agent')
    
    # Ensure to have valid agent names
    if not speaker_agent or not target_agent or not isinstance(speaker_agent, str) or not isinstance(target_agent, str):
        return None
    
    responses = []
    
    # first, the speaker agent responds (speaking TO the target agent)
    speaker_response = get_agent_response(
        speaker_agent, session, last_speaker, last_message, 
        is_directly_addressed=True, other_agent_response=None, 
        agent_to_agent_info=agent_to_agent_info
    )
    responses.append({"name": speaker_agent, "text": speaker_response})
    
    # then, the target agent responds 
    target_response = get_agent_response(
        target_agent, session, last_speaker, last_message, 
        is_directly_addressed=False, other_agent_response=speaker_response, 
        agent_to_agent_info=agent_to_agent_info
    )
    responses.append({"name": target_agent, "text": target_response})
    
    return responses


def _determine_addressed_agent(last_speaker: str, last_message: str, selected_agents: str) -> str:
    """Determine which agent(s) should respond based on selection and detection."""
    if selected_agents and selected_agents != "both":
        # explicit selection overrides automatic detection
        if selected_agents.lower() == "alpha":
            return "Alpha"
        elif selected_agents.lower() == "beta":
            return "Beta"
        else:
            return "both"
    else:
        # use automatic detection for "both" or when no selection is provided
        return detect_addressed_agent(last_message) if last_speaker == "trainee" else "both"


def get_agent_responses(session: Dict[str, Any], last_speaker: str, last_message: str, selected_agents: str = "both"):
    """Get responses from agents based on session context and last message.
    
    Args:
        session: Current session state and history
        last_speaker: Who spoke last ("trainee", "Alpha", or "Beta")
        last_message: The last message spoken
        selected_agents: Which agents should respond ("both", "alpha", "beta")
        
    Returns:
        List of agent responses with name and text
    """
    # Check for agent-to-agent communication instruction first
    agent_to_agent_info = detect_agent_to_agent_instruction(last_message) if last_speaker == "trainee" else {'is_agent_to_agent': False}
    
    # Handle agent-to-agent communication
    if agent_to_agent_info.get('is_agent_to_agent') and selected_agents == "both":
        agent_responses = _handle_agent_to_agent_communication(session, last_speaker, last_message, agent_to_agent_info)
        if agent_responses is not None:
            return agent_responses
    
    # Determine which agent should respond
    addressed_agent = _determine_addressed_agent(last_speaker, last_message, selected_agents)
    responses = []
    
    # agent-agent communication
    if last_speaker in ["Alpha", "Beta"]:
        # One agent spoke to the other directly
        other_agent = "Beta" if last_speaker == "Alpha" else "Alpha"
        logger.info(f"Direct agent-to-agent communication: {last_speaker} spoke to {other_agent}")
        
        # Generate response from the other agent
        agent_response = get_agent_response(
            other_agent, session, last_speaker, last_message, 
            is_directly_addressed=True, other_agent_response=None
        )
        responses.append({"name": other_agent, "text": agent_response})
        
        # Return immediately after direct agent-to-agent communication
        return responses
    
    # General response generation when trainee speaks
    elif last_speaker == "trainee":
        # Generate responses sequentially so each agent can be aware of the other's response
        if addressed_agent == "Alpha" or addressed_agent == "both":
            is_alpha_addressed = addressed_agent == "Alpha"
            alpha_response = get_agent_response("Alpha", session, last_speaker, last_message, is_directly_addressed=is_alpha_addressed, other_agent_response=None)
            responses.append({"name": "Alpha", "text": alpha_response})
        
        if addressed_agent == "Beta" or addressed_agent == "both":
            is_beta_addressed = addressed_agent == "Beta"
            # Pass Alpha's response to Beta so Beta can avoid repetition
            alpha_response = next((r["text"] for r in responses if r["name"] == "Alpha"), None)
            beta_response = get_agent_response("Beta", session, last_speaker, last_message, is_directly_addressed=is_beta_addressed, other_agent_response=alpha_response)
            responses.append({"name": "Beta", "text": beta_response})
    
    # If no agents were addressed,default to both
    if not responses:
        alpha_response = get_agent_response("Alpha", session, last_speaker, last_message, other_agent_response=None)
        beta_response = get_agent_response("Beta", session, last_speaker, last_message, other_agent_response=alpha_response)
        responses = [
            {"name": "Alpha", "text": alpha_response},
            {"name": "Beta", "text": beta_response}
        ]
    
    return responses 