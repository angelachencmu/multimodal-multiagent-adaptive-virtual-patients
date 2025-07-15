# this file is a backup for future usage that we want to incorporate demand-withdraw pattern into Escalation stage


DEMAND_WITHDRAW_PHASES = {
    1: {
        "description": "Alpha tries to start a discussion, Beta avoids",
        "Alpha_prompt": "Try to start a serious discussion with Beta about the problem. Be direct but not yet aggressive. Use 'we need to talk about' or 'I want to discuss' language.",
        "Beta_prompt": "Avoid the discussion Beta is trying to start. Be evasive, change the subject, or minimize the issue. Use phrases like 'not now', 'it's not that serious', or 'I don't want to get into this'."
    },
    2: {
        "description": "Alpha pressures, nags, or demands while Beta withdraws defensively",
        "Alpha_prompt": "Pressure Beta more intensely. Use demanding language like 'you always', 'you never', 'I need you to', or 'we have to deal with this now'. Show frustration that Beta is avoiding the issue.",
        "Beta_prompt": "Withdraw defensively from the discussion. Use dismissive or defensive language while pulling back. Examples: 'You're being ridiculous', 'I don't have to listen to this', 'This is exactly why I don't want to talk to you', 'You're just going to twist everything I say'. Show emotional charge even while withdrawing."
    },
    3: {
        "description": "Alpha pressures for apology, Beta resists",
        "Alpha_prompt": "Demand an apology or acknowledgment from Beta. Use phrases like 'just say you're sorry', 'admit you were wrong', 'I need you to take responsibility'. Show desperation under the anger.",
        "Beta_prompt": "Resist apologizing or taking responsibility. Defend yourself or counter-attack. Use phrases like 'I'm not apologizing', 'you're the one who', 'this is ridiculous', or 'I didn't do anything wrong'."
    }
}

def get_demand_withdraw_phase(session):
    disagreement_turns = session.get('disagreement_turns', 0)
    
    if disagreement_turns <= 1:
        return 1  # Phase 1: Initial discussion attempt
    elif disagreement_turns <= 4:
        return 2  # Phase 2: Pressure and withdrawal
    else:
        return 3  # Phase 3: Demand for apology

def get_demand_withdraw_prompt(agent_name, session):
    if session.get('stage') != 'Escalation' or not session.get('disagreement_mode'):
        return None
    
    phase = get_demand_withdraw_phase(session)
    phase_info = DEMAND_WITHDRAW_PHASES.get(phase, {})
    
    prompt = phase_info.get(f"{agent_name}_prompt", "")
    
    if prompt:
        return f"""
DEMAND-WITHDRAW PATTERN (Phase {phase}): {phase_info['description']}

As {agent_name}: {prompt}

IMPORTANT: You are speaking DIRECTLY to your partner, not to the therapist. Use "you" language and address them directly.
"""
    return None

def is_demand_withdraw_active(session):
    """Check if demand-withdraw pattern should be active"""
    return (session.get('stage') == 'Escalation' and 
            session.get('disagreement_mode', False) and
            session.get('disagreement_turns', 0) >= 0)

def should_override_disagreement_exit(session, response_text):
    """Check if disagreement mode exit should be overridden for demand-withdraw pattern"""
    if not is_demand_withdraw_active(session):
        return False
    
    phase = get_demand_withdraw_phase(session)
    response_lower = response_text.lower()
    
    # Phase 3: Beta's "apology" might be resistant, don't exit
    if phase == 3:
        resistant_apology_patterns = [
            "fine, i'm sorry",
            "whatever, i'm sorry", 
            "happy now",
            "there, i said it",
            "i'm sorry, okay?",
            "sorry, sorry, sorry"
        ]
        
        if any(pattern in response_lower for pattern in resistant_apology_patterns):
            return True  # Override exit, continue pattern
    
    # Don't end pattern before Phase 3 is complete
    if phase < 3:
        return True
    
    return False

def get_demand_withdraw_turn_limit(session):
    """Get extended turn limit for demand-withdraw pattern"""
    if is_demand_withdraw_active(session):
        return 9  # Allow 3 phases with 3 turns each
    return 6  # Default escalation limit 