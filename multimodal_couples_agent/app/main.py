from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from .agents import get_agent_responses, get_current_emotion
from .tts import text_to_speech
from dotenv import load_dotenv
from fastapi import Body
from .eft import detect_stage, detect_eft_skill, detect_eft_subskill, get_all_eft_subskills
load_dotenv()

# session store for demonstration
sessions: Dict[str, Dict[str, Any]] = {}

# Default scenario for each difficulty level
difficulty_scenarios: Dict[str, str] = {
    "easy": "A couple discusses their extreme trust issues when they are hanging out with members of the opposite sex without each other present.  Alpha is worried about Beta hanging out with other women.  Couple's trust issues stem from previous indiscretions. The couple is willing to work on their relationship and show some openness to therapeutic guidance.",
    "normal": "A couple discusses their extreme trust issues when they are hanging out with members of the opposite sex without each other present.  Alpha is worried about Beta hanging out with other women. The couple's trust issues stem from previous indiscretions. They have some resistance but can be guided with appropriate therapeutic techniques.",
    "hard": "A couple discusses their extreme trust issues when they are hanging out with members of the opposite sex without each other present.  Alpha is worried about Beta hanging out with other women. Couple's trust issues stem from previous indiscretions. They are highly defensive, resistant to change, and quick to escalate conflicts. Previous therapy attempts have failed."
}

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")

class ChatRequest(BaseModel):
    session_id: str
    message: str
    difficulty: Optional[str] = None
    selected_agents: Optional[str] = "both"  # "both"

class AgentContinueRequest(BaseModel):
    session_id: str
    responding_agent: str  # "Alpha" or "Beta"

class AgentResponse(BaseModel):
    name: str
    text: str
    audio_url: str

class ChatResponse(BaseModel):
    agent_responses: List[AgentResponse]
    current_stage: str
    eft_skill: str
    eft_subskill: Dict[str, Any]
    difficulty: str
    is_completed: bool
    completion_message: Optional[str] = None
    wrap_up_turns_remaining: Optional[int] = None
    disagreement_mode: bool = False
    disagreement_turns: int = 0
    intervention_needed: bool = False

def initialize_session(session_id: str, difficulty: str = "normal") -> Dict[str, Any]:
    """Initialize a new session with the specified difficulty level"""
    if difficulty not in ["easy", "normal", "hard"]:
        difficulty = "normal"
    
    return {
        "history": [],
        "stage": "Greeting", 
        "scenario": difficulty_scenarios.get(difficulty, "A generic couple conflict."),
        "difficulty": difficulty,
        "wrap_up_turns": 0,  # Track turns after reaching wrap up stage
        "is_completed": False  
    }

def detect_intervention(message: str) -> bool:
    """Detect if trainee's message is an intervention to stop agent disagreement"""
    intervention_keywords = [
        "stop", "calm down", "hold on", "wait", "pause", "enough", 
        "let's refocus", "take a breath", "slow down", "hold up",
        "that's enough", "let's step back", "time out", "settle down"
    ]
    
    message_lower = message.lower().strip()
    
    # Check for exact matches and phrases
    for keyword in intervention_keywords:
        if keyword in message_lower:
            return True
    
    # Check for intervention phrases
    intervention_phrases = [
        "let's talk about",
        "i want to focus on",
        "let's work on",
        "i need you both to",
        "can we please",
        "i'd like to redirect"
    ]
    
    for phrase in intervention_phrases:
        if phrase in message_lower:
            return True
    
    return False

def detect_actual_speaker(message: str) -> str:
    """
    Detect who is actually speaking based on the message content.
    So that system can handle agent-to-agent communication properly.
    """
    message_lower = message.lower().strip()
    
    # Check for direct name addressing 
    if message_lower.startswith("alpha,") or " alpha," in message_lower:
        return "Beta"  # Beta is talking to Alpha
    elif message_lower.startswith("beta,") or " beta," in message_lower:
        return "Alpha"  # Alpha is talking to Beta
    
    # Specific patterns indicate Alpha is speaking to Beta 
    alpha_to_beta_patterns = [
        "you always", "you never", "you can't", "you won't", "you should",
        "you need to", "you make me", "you hurt me", "you ignore", "you dismiss",
        "you say", "you think", "you feel", "you act",
        "when you", "why do you", "how can you", "you're making"
    ]
    
    # Specific patterns indicate Beta is speaking to Alpha 
    beta_to_alpha_patterns = [
        "you're exaggerating", "you're being dramatic", "you're overreacting", 
        "you're making this", "you're putting words", "you don't understand",
        "you're not listening", "you're being unfair"
    ]
    
    # Check for Beta talking to Alpha 
    for pattern in beta_to_alpha_patterns:
        if pattern in message_lower:
            return "Beta"
    
    # Check for Alpha talking to Beta 
    for pattern in alpha_to_beta_patterns:
        if pattern in message_lower:
            return "Alpha"
    
    # If no direct addressing is detected, assume it's the trainee
    return "trainee"

def check_session_completion(session: Dict[str, Any], new_stage: str) -> Dict[str, Any]:
    """
    Check if session should be completed based on stage progression.
    Returns updated session with completion status.
    """
    MAX_WRAP_UP_TURNS = 3  # Allow 3 more turns after Wrap-up stage
    
    # If already completed, don't change anything
    if session.get("is_completed", False):
        return session
    
    current_stage = session.get("stage", "Greeting")
    wrap_up_turns = session.get("wrap_up_turns", 0)
    
    # If trainee just entered Wrap-up stage
    if new_stage == "Wrap-up" and current_stage != "Wrap-up":
        session["wrap_up_turns"] = 0
    
    # If trainee is in wrap up stage, increment turn counter
    elif new_stage == "Wrap-up":
        session["wrap_up_turns"] = wrap_up_turns + 1
        
        # Check if exceeded the allowed turns in Wrap-up
        if session["wrap_up_turns"] >= MAX_WRAP_UP_TURNS:
            session["is_completed"] = True
    
    # If moved out of wrap up stage back to another stage, reset counter
    elif current_stage == "Wrap-up" and new_stage != "Wrap-up":
        session["wrap_up_turns"] = 0
    
    return session

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # Create session with proper difficulty handling
    if req.session_id not in sessions:
        # New session: use difficulty from request or default to normal
        difficulty = req.difficulty if req.difficulty and req.difficulty in ["easy", "normal", "hard"] else "normal"
        sessions[req.session_id] = initialize_session(req.session_id, difficulty)
    else:
        # Existing session: update difficulty if specified in request
        if req.difficulty and req.difficulty in ["easy", "normal", "hard"]:
            sessions[req.session_id]["difficulty"] = req.difficulty
            # Update scenario to match new difficulty
            sessions[req.session_id]["scenario"] = difficulty_scenarios.get(req.difficulty, "A generic couple conflict.")
    
    session = sessions[req.session_id]
    
    # Check if session is already completed
    if session.get("is_completed", False):
        return {
            "agent_responses": [],
            "current_stage": session.get("stage", "Wrap-up"),
            "eft_skill": "",
            "eft_subskill": {},
            "difficulty": session.get("difficulty", "normal"),
            "is_completed": True,
            "completion_message": "This therapy session has been completed. Thank you for practicing your EFT skills! Click 'New Session' to start a new practice session.",
            "wrap_up_turns_remaining": 0
        }
    
    # Ensure scenario matches current difficulty 
    current_difficulty = session.get("difficulty", "normal")
    session["scenario"] = difficulty_scenarios.get(current_difficulty, "A generic couple conflict.")
    
    # Create temporary history entry with trainee's message to detect new stage
    temp_history_entry = {"trainee": req.message, "Alpha": "", "Beta": ""}
    temp_session = {**session, "history": session["history"] + [temp_history_entry]}
    
    # Detect the new stage before agents respond
    old_stage = session.get("stage", "Greeting")
    new_stage = detect_stage(temp_session)
    
    # Check for session completion based on stage progression
    session = check_session_completion(session, new_stage)
    
    # Stage change handling for disagreement mode
    stage_changed = old_stage != new_stage
    
    if stage_changed:
        # If moving out of Escalation stage, end disagreement mode
        if old_stage == "Escalation" and new_stage != "Escalation":
            if session.get("disagreement_mode", False):
                session["disagreement_mode"] = False
                session["disagreement_turns"] = 0
    
    session["stage"] = new_stage
    
    # Detect if the trainee's message is an intervention
    intervention_detected = detect_intervention(req.message)
    
    # If an intervention is detected, stop disagreement mode and reset turns
    if intervention_detected:
        session["disagreement_mode"] = False
        session["disagreement_turns"] = 0
    
    # If session just completed, generate final completion responses
    if session.get("is_completed", False):
        # Generate final completion message from agents
        final_agent_responses = []
        
        # Alpha's completion message
        alpha_completion = "Thank you for helping us work through this. I feel like we made some real progress today."
        alpha_emotion = get_current_emotion("Alpha", "Wrap-up")
        alpha_audio_url = text_to_speech(alpha_completion, "Alpha", alpha_emotion)
        final_agent_responses.append({
            "name": "Alpha",
            "text": alpha_completion,
            "audio_url": alpha_audio_url
        })
        
        # Beta's completion message
        beta_completion = "I appreciate the safe space you created for us. This was really helpful."
        beta_emotion = get_current_emotion("Beta", "Wrap-up")
        beta_audio_url = text_to_speech(beta_completion, "Beta", beta_emotion)
        final_agent_responses.append({
            "name": "Beta", 
            "text": beta_completion,
            "audio_url": beta_audio_url
        })
        
        # Add final history entry
        final_history_entry = {
            "trainee": req.message,
            "Alpha": alpha_completion,
            "Beta": beta_completion
        }
        session["history"].append(final_history_entry)
        
        return {
            "agent_responses": final_agent_responses,
            "current_stage": session["stage"],
            "eft_skill": "Consolidation",
            "eft_subskill": {},
            "difficulty": session.get("difficulty", "normal"),
            "is_completed": True,
            "completion_message": "🎉 Congratulations! You have successfully completed this EFT couple therapy session. The couple has reached a positive resolution and expressed gratitude for your therapeutic guidance.",
            "wrap_up_turns_remaining": 0
        }
    
    # Generate agent responses using the correct stage
    import time
    total_start = time.time()
    
    selected_agents = req.selected_agents or "both"
    
    # Time for LLM response generation
    llm_start = time.time()
    # Detect who is actually speaking based on message content
    actual_speaker = detect_actual_speaker(req.message)
    agent_texts = get_agent_responses(session, actual_speaker, req.message, selected_agents)
    llm_time = time.time() - llm_start
    
    # Time for TTS generation for each agent
    tts_start = time.time()
    agent_responses = []
    
    # Skip TTS in development mode for faster responses
    skip_tts = os.getenv("SKIP_TTS", "false").lower() == "true"
    
    for agent in agent_texts:
        # Get current emotion for the agent based on the session stage
        emotion = get_current_emotion(agent["name"], session["stage"])
        
        if skip_tts:
            audio_url = f"/audio/placeholder_{agent['name'].lower()}.mp3"  # Placeholder
        else:
            audio_url = text_to_speech(agent["text"], agent["name"], emotion)
            
        agent_responses.append({
            "name": agent["name"],
            "text": agent["text"],
            "audio_url": audio_url
        })
    tts_time = time.time() - tts_start
    
    # Update session history - handle variable number of responses
    history_entry = {"trainee": req.message}
    
    # Add responses for agents that actually responded
    for agent in agent_texts:
        history_entry[agent["name"]] = agent["text"]
    
    # Fill in empty responses for agents that didn't respond
    if "Alpha" not in history_entry:
        history_entry["Alpha"] = ""
    if "Beta" not in history_entry:
        history_entry["Beta"] = ""
    
    session["history"].append(history_entry)
    eft_skill = detect_eft_skill(session)
    eft_subskill = detect_eft_subskill(session)
    
    # Ensure consistency: if subskill is detected, use its parent skill as the main skill
    if eft_subskill and eft_subskill.get("skill"):
        eft_skill = eft_subskill["skill"]
    
    # Calculate remaining wrap-up turns
    wrap_up_turns_remaining = None
    completion_message = None
    
    if session["stage"] == "Wrap-up":
        MAX_WRAP_UP_TURNS = 3
        wrap_up_turns_remaining = MAX_WRAP_UP_TURNS - session.get("wrap_up_turns", 0)
        if wrap_up_turns_remaining > 0:
            completion_message = f"Session is in wrap-up phase. {wrap_up_turns_remaining} more exchanges before automatic completion."
    
    # Determine disagreement status 
    disagreement_mode = session.get("disagreement_mode", False)
    disagreement_turns = session.get("disagreement_turns", 0)
    
    # Agent-to-agent arguments during disagreement mode
    # Only autocontinue in specific escalation scenarios
    should_auto_continue = (
        disagreement_mode and 
        len(agent_responses) == 2 and
        session.get("stage", "Greeting") == "Escalation" and  # Only during escalation stage
        disagreement_turns == 0 and  # Only on the very first turn of disagreement
        not intervention_detected  # Don't auto continue if trainee intervened
    )
    
    if should_auto_continue:
        import time
        auto_continue_start = time.time()
        
        # Use the first agent's response to trigger the second agent for back-and-forth
        first_agent_response = agent_responses[0]
        second_agent_response = agent_responses[1]
        responding_agent_name = first_agent_response["name"]
        
        # Generate additional agent-to-agent response
        llm_start = time.time()
        from app.agents import get_agent_response
        additional_agent_response = get_agent_response(
            responding_agent_name, 
            session, 
            second_agent_response["name"], 
            second_agent_response["text"], 
            is_directly_addressed=False, 
            other_agent_response=None
        )
        llm_time = time.time() - llm_start
        
        # Generate TTS for additional response
        tts_start = time.time()
        emotion = get_current_emotion(responding_agent_name, session["stage"])
        
        if skip_tts:
            audio_url = f"/audio/placeholder_{responding_agent_name.lower()}.mp3"  # Placeholder
        else:
            audio_url = text_to_speech(additional_agent_response, responding_agent_name, emotion)
            
        tts_time = time.time() - tts_start
        
        # Add the additional response
        agent_responses.append({
            "name": responding_agent_name,
            "text": additional_agent_response,
            "audio_url": audio_url
        })
        
        # Update session history
        history_entry[responding_agent_name] = additional_agent_response
        
        auto_continue_time = time.time() - auto_continue_start
        
        # Update disagreement status
        disagreement_mode = session.get("disagreement_mode", False)
        disagreement_turns = session.get("disagreement_turns", 0)
    
    # Final timing summary (check how long it took to generate the response)
    total_time = time.time() - total_start
    
    response_data = {
        "agent_responses": agent_responses,
        "current_stage": session["stage"],
        "eft_skill": eft_skill,
        "eft_subskill": eft_subskill,
        "difficulty": session.get("difficulty", "normal"),
        "is_completed": False,
        "completion_message": completion_message,
        "wrap_up_turns_remaining": wrap_up_turns_remaining,
        "disagreement_mode": disagreement_mode,
        "disagreement_turns": disagreement_turns,
        "intervention_needed": intervention_detected
    }
    
    return response_data

@app.get("/stage")
def get_stage(session_id: str = Query(...)):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}
    return {"stage": session.get("stage", "Greeting")}

@app.post("/set_stage")
def set_stage(session_id: str = Body(...), stage: str = Body(...)):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}
    session["stage"] = stage
    return {"stage": stage}

@app.post("/set_difficulty")
def set_difficulty(session_id: str = Body(...), difficulty: str = Body(...)):
    if difficulty not in ["easy", "normal", "hard"]:
        return {"error": "Invalid difficulty level. Must be 'easy', 'normal', or 'hard'"}
    
    if session_id not in sessions:
        # Create new session with specified difficulty
        sessions[session_id] = initialize_session(session_id, difficulty)
    else:
        # Update existing session
        sessions[session_id]["difficulty"] = difficulty
        # Update scenario to match new difficulty
        sessions[session_id]["scenario"] = difficulty_scenarios.get(difficulty, "A generic couple conflict.")
    
    return {
        "difficulty": difficulty,
        "scenario": difficulty_scenarios.get(difficulty, "A generic couple conflict."),
        "message": f"Difficulty set to {difficulty}. All future responses will maintain this difficulty level."
    }

@app.get("/difficulty")
def get_difficulty(session_id: str = Query(...)):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}
    return {"difficulty": session.get("difficulty", "normal")}

@app.post("/reset_session")
def reset_session(session_id: str = Body(...), difficulty: str = Body(default="normal")):
    """Reset a session to start fresh with specified difficulty"""
    if difficulty not in ["easy", "normal", "hard"]:
        difficulty = "normal"
    
    sessions[session_id] = initialize_session(session_id, difficulty)
    return {
        "message": f"Session reset with {difficulty} difficulty",
        "difficulty": difficulty,
        "scenario": difficulty_scenarios.get(difficulty, "A generic couple conflict.")
    }

@app.post("/set_scenario")
def set_scenario(difficulty: str = Body(...), scenario: str = Body(...)):
    """Set custom scenario for a specific difficulty level"""
    if difficulty not in ["easy", "normal", "hard"]:
        return {"error": "Invalid difficulty level"}
    difficulty_scenarios[difficulty] = scenario
    return {"difficulty": difficulty, "scenario": scenario}

@app.get("/scenario")
def get_scenario(difficulty: str = Query(...)):
    """Get scenario for a specific difficulty level"""
    if difficulty not in ["easy", "normal", "hard"]:
        return {"error": "Invalid difficulty level"}
    return {"difficulty": difficulty, "scenario": difficulty_scenarios.get(difficulty, "Generic couple conflict.")}

@app.get("/all_scenarios")
def get_all_scenarios():
    """Get all scenarios for all difficulty levels"""
    return difficulty_scenarios

@app.get("/eft_skill")
def get_eft_skill(session_id: str = Query(...)):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}
    skill = detect_eft_skill(session)
    subskill = detect_eft_subskill(session)
    
    # If subskill is detected, use its parent skill as the main skill
    if subskill and subskill.get("skill"):
        skill = subskill["skill"]
    
    return {"eft_skill": skill, "eft_subskill": subskill}

@app.get("/eft_subskills")
def get_eft_subskills():
    """Get all EFT sub-skills for frontend display"""
    return {"eft_subskills": get_all_eft_subskills()}

@app.post("/agent_continue", response_model=ChatResponse)
async def agent_continue_endpoint(req: AgentContinueRequest):
    """Allow an agent to continue responding to another agent's direct communication"""
    if req.session_id not in sessions:
        return {"error": "Session not found"}
    
    session = sessions[req.session_id]
    history = session.get("history", [])
    
    if not history:
        return {"error": "No conversation history found"}
    
    # Get the last exchange
    last_entry = history[-1]
    
    # Find the last agent that spoke and what they said
    last_speaker = None
    last_message = ""
    
    # Check if Alpha or Beta spoke last (not the trainee)
    if last_entry.get("Alpha") and last_entry.get("Alpha").strip():
        last_speaker = "Alpha"
        last_message = last_entry["Alpha"]
    elif last_entry.get("Beta") and last_entry.get("Beta").strip():
        last_speaker = "Beta"
        last_message = last_entry["Beta"]
    
    if not last_speaker or last_speaker == req.responding_agent:
        return {"error": "No valid agent-to-agent communication to continue"}
    
    # Generate response from the responding agent
    agent_texts = get_agent_responses(session, last_speaker, last_message, "both")
    
    # Filter to only get the response from the requested agent
    agent_responses = []
    for agent in agent_texts:
        if agent["name"] == req.responding_agent:
            # Get current emotion for the agent based on the session stage
            emotion = get_current_emotion(agent["name"], session["stage"])
            audio_url = text_to_speech(agent["text"], agent["name"], emotion)
            agent_responses.append({
                "name": agent["name"],
                "text": agent["text"],
                "audio_url": audio_url
            })
    
    # Update session history , add the new response to the existing entry
    if agent_responses:
        # Update the last history entry with the new response
        last_entry[req.responding_agent] = agent_responses[0]["text"]
    
    # Detect EFT skills based on the updated session
    eft_skill = detect_eft_skill(session)
    eft_subskill = detect_eft_subskill(session)
    
    # if subskill is detected, use its parent skill as the main skill
    if eft_subskill and eft_subskill.get("skill"):
        eft_skill = eft_subskill["skill"]
    
    return {
        "agent_responses": agent_responses,
        "current_stage": session["stage"],
        "eft_skill": eft_skill,
        "eft_subskill": eft_subskill,
        "difficulty": session.get("difficulty", "normal"),
        "is_completed": session.get("is_completed", False),
        "completion_message": None,
        "wrap_up_turns_remaining": None,
        "disagreement_mode": session.get("disagreement_mode", False),
        "disagreement_turns": session.get("disagreement_turns", 0),
        "intervention_needed": False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)