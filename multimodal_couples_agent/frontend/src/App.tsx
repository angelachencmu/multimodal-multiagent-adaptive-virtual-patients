import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Play, Pause, RotateCcw, Users, Brain, MessageCircle, Settings, Edit3, Save, X, Heart, UserCheck, Smile } from 'lucide-react';
import './App.css';

// you may need to change this to the IP address of your own server
const API_BASE = 'http://127.0.0.1:8000'; 

// Configure axios 
axios.defaults.baseURL = API_BASE;
axios.defaults.headers.post['Content-Type'] = 'application/json';
axios.defaults.headers.common['Accept'] = 'application/json';

interface AgentResponse {
  name: string;
  text: string;
  audio_url: string;
}

interface EftSubskill {
  skill: string;
  step: string;
  name: string;
  description: string;
}

interface ChatMessage {
  type: 'user' | 'agents' | 'completion';
  content: string;
  agents?: AgentResponse[];
  timestamp: Date;
  stage?: string;
  eft_skill?: string;
  eft_subskill?: EftSubskill;
  difficulty?: string;
  selectedAgents?: string;
  isCompleted?: boolean;
  completionMessage?: string;
}

interface SessionInfo {
  stage: string;
  eft_skill: string;
  eft_subskill?: EftSubskill;
  difficulty: string;
}

interface AgentEmotion {
  Alpha: string;
  Beta: string;
}


const Avatar: React.FC<{ name: string; emotion: string; isActive: boolean; size?: 'small' | 'large' }> = ({ name, emotion, isActive, size = 'large' }) => {
  const getEmotionClass = (emotion: string) => {
    switch (emotion) {
      // Alpha emotions:
      case 'alpha-neutral': return 'alpha-neutral'; 
      case 'angry': return 'angry';       
      case 'hopeful': return 'hopeful';   
      case 'resistant': return 'resistant';
      case 'relieved': return 'relieved'; 
      
      // Beta emotions:
      case 'beta-neutral': return 'beta-neutral'; 
      case 'defensive': return 'defensive'; 
      case 'cautious': return 'cautious'; 
      case 'open': return 'open';         
      case 'calm': return 'calm';     
      
      // Shared emotions:
      case 'sad': return 'sad';           
      case 'contempt': return 'contempt';  
      
      // Fallback:
      case 'neutral': return 'alpha-neutral'; 
      
      default: return 'neutral';
    }
  };

  const getDisplayEmotion = (emotion: string) => {
    // Convert internal emotion names to display names
    switch (emotion) {
      case 'alpha-neutral':
      case 'beta-neutral':
        return 'neutral';
      default:
        return emotion;
    }
  };

  const sizeClass = size === 'small' ? 'face-small' : 'face';

  return (
    <div className={`flex flex-col items-center ${size === 'small' ? 'space-y-1' : 'space-y-2'}`}>
      <div className={`${getEmotionClass(emotion)} ${isActive ? 'ring-2 ring-blue-500' : ''}`}>
        <div className={sizeClass}>
          <div className="mouth"></div>
        </div>
      </div>
      <div className="text-center">
        <p className={`${size === 'small' ? 'text-xs' : 'text-sm'} font-medium ${
          name === 'Alpha' ? 'text-red-700' : 'text-blue-700'
        }`}>
          {name}
        </p>
        <p className={`${size === 'small' ? 'text-xs' : 'text-xs'} text-gray-500 capitalize`}>
          {getDisplayEmotion(emotion)}
        </p>
      </div>
    </div>
  );
};

function App() {
  const [sessionId, setSessionId] = useState(`session-${Date.now()}`);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [interrupt, setInterrupt] = useState(false);
  const interruptRef = useRef(false);

  const setInterruptState = (value: boolean) => {
    interruptRef.current = value;
    setInterrupt(value);
  };


  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [inCycle, setInCycle] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo>({ stage: 'Greeting', eft_skill: '', eft_subskill: undefined, difficulty: 'normal' });
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);
  const [audioElements, setAudioElements] = useState<{ [key: string]: HTMLAudioElement }>({});
  const [showScenarioEditor, setShowScenarioEditor] = useState(false);
  const [scenarios, setScenarios] = useState<{[key: string]: string}>({
    easy: '',
    normal: '',
    hard: ''
  });
  const [editingScenario, setEditingScenario] = useState<{difficulty: string, text: string}>({difficulty: '', text: ''});
  const [agentEmotions, setAgentEmotions] = useState<AgentEmotion>({ 
    Alpha: 'alpha-neutral',  // alpha starts neutral (pink) 
    Beta: 'beta-neutral'     // beta starts neutral (blue)
  });
  const [selectedAgents, setSelectedAgents] = useState<'both' | 'alpha' | 'beta'>('both');
  const [isSessionCompleted, setIsSessionCompleted] = useState(false);
  const [wrapUpTurnsRemaining, setWrapUpTurnsRemaining] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  
  // useEffect(() => {
  //   console.log("Updated messages:", messages);

  //   // Optional: log just agent text for clarity
  //   messages.forEach((message, i) => {
  //     if (message.type === 'agents' || message.type === 'completion') {
  //       message.agents?.forEach((agent, j) => {
  //         console.log(`Message ${i}.${j} - ${agent.name}: ${agent.text}`);
  //       });
  //     } else if (message.type === 'user') {
  //       console.log(`Message ${i} - User: ${message.content}`);
  //     }
  //   });
  // }, [messages]);

  useEffect(() => {
    console.log("Cycle Interupted", interrupt);
  }, [interrupt]);

 
  // Maping emotions by session stage

  const getAgentEmotions = (stage: string): AgentEmotion => {
    const emotionMap: { [key: string]: AgentEmotion } = {
      'Greeting': { 
        Alpha: 'alpha-neutral', 
        Beta: 'beta-neutral'   
      },
      'Problem Raising': { 
        Alpha: 'sad',          
        Beta: 'defensive'      
      },
      'Escalation': { 
        Alpha: 'angry',       
        Beta: 'sad'         
      },
      'De-escalation': { 
        Alpha: 'hopeful',      
        Beta: 'cautious'      
      },
      'Enactment': { 
        Alpha: 'resistant',    
        Beta: 'open'          
      },
      'Wrap-up': { 
        Alpha: 'relieved',    
        Beta: 'calm'         
      }
    };
    return emotionMap[stage] || { 
      Alpha: 'alpha-neutral', 
      Beta: 'beta-neutral'    
    };
  };

  // Update agent emotions when session stage changes
  useEffect(() => {
    const newEmotions = getAgentEmotions(sessionInfo.stage);
    setAgentEmotions(newEmotions);
  }, [sessionInfo.stage]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

const sendMessage = async () => {
  if (!inputMessage.trim()) return;

  console.log(messages);
  setInterruptState(true)

  const userMessage: ChatMessage = {
    type: 'user',
    content: inputMessage,
    timestamp: new Date(),
    selectedAgents: selectedAgents
  };

  setMessages(prev => [...prev, userMessage]);
  setIsLoading(true);

  try {
    const response = await axios.post('/chat', {
      session_id: sessionId,
      message: inputMessage,
      selected_agents: selectedAgents
    });

    // Update session info 
    const newSessionInfo = {
      stage: response.data.current_stage || 'Greeting',
      eft_skill: response.data.eft_skill || '',
      eft_subskill: response.data.eft_subskill,
      difficulty: response.data.difficulty || 'normal'
    };
    
    setSessionInfo(newSessionInfo);

    const initialAgentMessage: ChatMessage = {
      type: 'agents',
      content: '',
      agents: response.data.agent_responses,
      timestamp: new Date(),
      stage: response.data.current_stage,
      eft_skill: response.data.eft_skill,
      eft_subskill: response.data.eft_subskill,
      difficulty: response.data.difficulty
    };

    // Handle session completion
    if (response.data.is_completed) {
      setIsSessionCompleted(true);
      setWrapUpTurnsRemaining(0);
      
      const completionMessage: ChatMessage = {
        type: 'completion',
        content: response.data.completion_message || 'Session completed!',
        agents: response.data.agent_responses,
        timestamp: new Date(),
        stage: response.data.current_stage,
        eft_skill: response.data.eft_skill,
        eft_subskill: response.data.eft_subskill,
        difficulty: response.data.difficulty,
        isCompleted: true,
        completionMessage: response.data.completion_message
      };

      setMessages(prev => [...prev, completionMessage]);
    } else {
      // Update wrap-up turns 
      setWrapUpTurnsRemaining(response.data.wrap_up_turns_remaining);

      console.log('Initial agent message:', initialAgentMessage);
      setMessages(prev => [...prev, initialAgentMessage]);
    }
    
    // Preload and auto play audio 
    const newAudioElements: { [key: string]: HTMLAudioElement } = {};
    const agentResponses = response.data.agent_responses;

    agentResponses.forEach((agent: AgentResponse) => {
      const audio = new Audio(`${API_BASE}${agent.audio_url}`);
      newAudioElements[agent.audio_url] = audio;
    });

    setAudioElements(prev => ({ ...prev, ...newAudioElements }));

    // Sequential autoplay
    const playSequentially = (index: number) => {
      if (index >= agentResponses.length) return; // base case: done

      const currentAgent = agentResponses[index];
      const audio = newAudioElements[currentAgent.audio_url];

      setPlayingAudio(currentAgent.audio_url);

      audio.onended = () => {
        setPlayingAudio(null);
        setTimeout(() => {
          playSequentially(index + 1); // play next agent
        }, 500); // optional delay between voices
      };

      // Start playback
      setTimeout(() => {
        audio.play().catch(console.error);
      }, 300); // optional delay before first plays
    };

    // Start autoplay chain
    playSequentially(0);

    
    setAudioElements(prev => ({ ...prev, ...newAudioElements }));

    console.log(response.data);

    // Handle auto-continue loop
    if (response.data.should_auto_continue) {
      console.log("Starting auto-continue loop");
      let currentAgentData = response.data.agent_responses;
      // let updatedAgentMessage: ChatMessage = { ...initialAgentMessage };
      setInterruptState(false)
      setInCycle(true)
      while (!interruptRef.current) {
      console.log("Auto-continue iteration");

      try {
        const continueResponse = await axios.post('/auto-continue', {
          session_id: sessionId,
          message: currentAgentData,
        });

        if (interruptRef.current) {
          console.log("Interrupted — discarding current loop response.");
          break;
        }

        const newAgentMessage: ChatMessage = {
          type: 'agents',
          content: '',
          agents: [continueResponse.data],
          timestamp: new Date(),
          stage: continueResponse.data.stage,
          eft_skill: continueResponse.data.eft_skill,
          eft_subskill: continueResponse.data.eft_subskill,
          difficulty: continueResponse.data.difficulty
        };

        setMessages(prev => [...prev, newAgentMessage]);

        const audio = new Audio(`${API_BASE}${continueResponse.data.audio_url}`);
        setPlayingAudio(continueResponse.data.audio_url);
        setAudioElements(prev => ({
          ...prev,
          [continueResponse.data.audio_url]: audio
        }));

        await new Promise((resolveAudio, rejectAudio) => {
          audio.onended = () => {
            setPlayingAudio(null);
            resolveAudio(null); 
          };
          audio.onerror = (e) => {
            console.error("Audio error:", e);
            setPlayingAudio(null);
            resolveAudio(null); 
          };

          audio.play().catch((err) => {
            console.error("Playback failed:", err);
            resolveAudio(null);
          });
        });

        currentAgentData = [continueResponse.data];
      } catch (error) {
        console.error('Error in auto-continue:', error);
        break;
      }
    }

    setInCycle(false);

    }
  } catch (error) {
    console.error('Error sending message:', error);
  } finally {
    setIsLoading(false);
    setInputMessage('');
  }
};

  const playAudio = (audioUrl: string) => {
    // Stop any currently playing audio
    if (playingAudio && audioElements[playingAudio]) {
      audioElements[playingAudio].pause();
      audioElements[playingAudio].currentTime = 0;
    }

    if (audioElements[audioUrl]) {
      setPlayingAudio(audioUrl);
      audioElements[audioUrl].play().catch(console.error);
    }
  };

  const stopAudio = () => {
    if (playingAudio && audioElements[playingAudio]) {
      audioElements[playingAudio].pause();
      audioElements[playingAudio].currentTime = 0;
      setPlayingAudio(null);
    }
  };
  // Reset session
  const resetSession = () => {
    const newSessionId = `session-${Date.now()}`;
    setSessionId(newSessionId);
    setMessages([]);
    setSessionInfo({ stage: 'Greeting', eft_skill: '', eft_subskill: undefined, difficulty: 'normal' });
    setAgentEmotions({ 
      Alpha: 'alpha-neutral',  
      Beta: 'beta-neutral'    
    });
    setSelectedAgents('both');  
    setIsSessionCompleted(false);  
    setWrapUpTurnsRemaining(null);  
    setPlayingAudio(null);
    setAudioElements({});
  };

  const setDifficulty = async (difficulty: string) => {
    try {
      await axios.post('/set_difficulty', {
        session_id: sessionId,
        difficulty: difficulty
      });
      setSessionInfo(prev => ({ ...prev, difficulty }));
    } catch (error) {
      console.error('Error setting difficulty:', error);
    }
  };

  const loadScenarios = async () => {
    try {
      const response = await axios.get('/all_scenarios');
      setScenarios(response.data);
    } catch (error) {
      console.error('Error loading scenarios:', error);
    }
  };

  const saveScenario = async () => {
    try {
      await axios.post('/set_scenario', {
        difficulty: editingScenario.difficulty,
        scenario: editingScenario.text
      });
      await loadScenarios();
      setEditingScenario({difficulty: '', text: ''});
    } catch (error) {
      console.error('Error saving scenario:', error);
    }
  };

  const openScenarioEditor = async (difficulty: string) => {
    if (!scenarios[difficulty]) {
      await loadScenarios();
    }
    setEditingScenario({
      difficulty,
      text: scenarios[difficulty] || ''
    });
  };



  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-8xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <svg width="64" height="64" viewBox="0 0 288 173" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-16 w-16">
                <ellipse cx="80.1102" cy="85.5599" rx="68" ry="67.5" transform="rotate(-10.7212 80.1102 85.5599)" fill="#FD9F9F"/>
                <circle cx="201.5" cy="86.4" r="66.5" transform="rotate(21.3298 201.5 86.4)" fill="#447FFF"/>
                <circle cx="61.3759" cy="81.4445" r="9.03125" transform="rotate(-10.7212 61.3759 81.4445)" fill="white"/>
                <circle cx="94.7827" cy="75.1195" r="9.03125" transform="rotate(-10.7212 94.7827 75.1195)" fill="white"/>
                <rect x="58.0493" y="100.998" width="48.875" height="11.6875" rx="5.84375" transform="rotate(-10.7212 58.0493 100.998)" fill="white"/>
                <circle cx="188.909" cy="72.4993" r="9.03125" transform="rotate(21.3298 188.909 72.4993)" fill="white"/>
                <circle cx="220.58" cy="84.8663" r="9.03125" transform="rotate(21.3298 220.58 84.8663)" fill="white"/>
                <rect x="175.712" y="87.3074" width="48.875" height="11.6875" rx="5.84375" transform="rotate(21.3298 175.712 87.3074)" fill="white"/>
              </svg>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Couple Agents</h1>
                <p className="text-sm text-gray-600">EFT Couple Therapy Training</p>
              </div>
            </div>
            <button
              onClick={resetSession}
              className="flex items-center space-x-2 px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              <span>New Session</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-8xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-6 gap-6">
          {/* Left Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Session Info */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                <Brain className="h-4 w-4 mr-2" />
                Session Status
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Current Interaction Stage</label>
                  <p className="text-sm font-medium text-primary-600 mt-1">{(() => {
                    const latestAgentMessage = messages.slice().reverse().find(msg => msg.type === 'agents' && msg.stage);
                    return latestAgentMessage?.stage || sessionInfo.stage;
                  })()}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">EFT Skill Detected</label>
                  {(() => {
                    // Get the latest EFT skill from the most recent agent message
                    const latestAgentMessage = messages.slice().reverse().find(msg => msg.type === 'agents' && msg.eft_skill);
                    const currentEftSkill = latestAgentMessage?.eft_skill || sessionInfo.eft_skill;
                    const currentEftSubskill = latestAgentMessage?.eft_subskill || sessionInfo.eft_subskill;
                    

                    
                    return currentEftSkill ? (
                      <div>
                        <p className="text-sm font-medium text-green-600 mt-1">{currentEftSkill}</p>
                        {currentEftSubskill && (
                          <div className="mt-2 p-2 bg-green-50 rounded-lg border border-green-200">
                            <p className="text-xs font-medium text-green-800">{currentEftSubskill.name}</p>
                            <p className="text-xs text-green-700 mt-1">{currentEftSubskill.description}</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="mt-1">
                        <p className="text-sm text-gray-400 italic">No EFT skill detected yet</p>
                        <p className="text-xs text-gray-500 mt-1">
      
                        </p>
                      </div>
                    );
                  })()}
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Difficulty Level</label>
                  <p className={`text-sm font-medium mt-1 ${
                    sessionInfo.difficulty === 'easy' ? 'text-green-600' :
                    sessionInfo.difficulty === 'hard' ? 'text-red-600' : 'text-orange-600'
                  }`}>
                    {sessionInfo.difficulty.charAt(0).toUpperCase() + sessionInfo.difficulty.slice(1)}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Session ID</label>
                  <p className="text-xs text-gray-600 mt-1 font-mono">{sessionId.slice(-8)}</p>
                </div>
              </div>
            </div>

            {/* Conversation Tips */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                <Settings className="h-4 w-4 mr-2" />
                Therapy Guide
              </h3>
              <div className="space-y-3 text-sm">
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                  <p className="text-red-700 font-medium">Alpha (Pursuer)</p>
                  <p className="text-red-600 text-xs mt-1">Criticizes, demands, escalates when upset</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-blue-700 font-medium">Beta (Withdrawer)</p>
                  <p className="text-blue-600 text-xs mt-1">Withdraws, becomes silent, defends</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-green-700 font-medium">Your Role</p>
                  <p className="text-green-600 text-xs mt-1">Guide them through EFT techniques to break negative cycles</p>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="border-b border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  {/* Left Avatar - ALPHA (Pursuer/Demander) */}
                  <Avatar 
                    name="Alpha" 
                    emotion={agentEmotions.Alpha} 
                    isActive={playingAudio?.includes('Alpha') || false}
                    size="small"
                  />
                  
                  {/* Center Title - Therapist Position */}
                  <div className="flex flex-col items-center">
                    <div className="flex items-center space-x-2">
                      <MessageCircle className="h-5 w-5 text-primary-600" />
                      <h2 className="font-semibold text-gray-900">Therapy Session Chat</h2>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Alpha (Demander) & Beta (Withdrawer) - Practice your EFT skills
                    </p>
                  </div>
                  
                  {/* Right Avatar - BETA (Withdrawer) */}
                  <Avatar 
                    name="Beta" 
                    emotion={agentEmotions.Beta} 
                    isActive={playingAudio?.includes('Beta') || false}
                    size="small"
                  />
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 mt-8">
                    <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Welcome to the Therapy Simulator</p>
                    <p className="text-sm mt-2">Start by greeting the couple or addressing their concerns.</p>
                  </div>
                )}

                {messages.map((message, index) => (
                  <div key={index} className="space-y-3">
                    {message.type === 'user' ? (
                      <div className="flex justify-center">
                        <div className="bg-primary-600 text-white rounded-lg px-4 py-2 max-w-md text-center">
                          <div className="flex items-center justify-center space-x-2 mb-1">
                            <p className="text-sm font-medium">You</p>
                            {message.selectedAgents && message.selectedAgents !== 'both' && (
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                message.selectedAgents === 'alpha' ? 'bg-red-500' : 'bg-blue-500'
                              }`}>
                                → {message.selectedAgents === 'alpha' ? 'Alpha' : 'Beta'}
                              </span>
                            )}
                            {message.selectedAgents === 'both' && (
                              <span className="text-xs px-2 py-1 rounded-full bg-gray-500">
                                → Both
                              </span>
                            )}
                          </div>
                          <p>{message.content}</p>
                        </div>
                      </div>
                    ) : message.type === 'completion' ? (
                      <div className="space-y-4">
                        {/* Final agent responses */}
                        {message.agents?.map((agent, agentIndex) => (
                          <div key={agentIndex} className={`flex ${
                            agent.name === 'Alpha' ? 'justify-start' : 'justify-end'
                          }`}>
                            <div className={`rounded-lg px-4 py-3 max-w-md ${
                              agent.name === 'Alpha' 
                                ? 'bg-red-50 border border-red-200' 
                                : 'bg-blue-50 border border-blue-200'
                            }`}>
                              <div className="flex items-center justify-between mb-2">
                                <p className={`text-sm font-medium ${
                                  agent.name === 'Alpha' ? 'text-red-700' : 'text-blue-700'
                                }`}>
                                  {agent.name} ({agent.name === 'Alpha' ? 'Demander' : 'Withdrawer'})
                                </p>
                                <div className="flex items-center space-x-2">
                                  {playingAudio === agent.audio_url && (
                                    <div className="flex items-center space-x-1">
                                      <div className="animate-pulse w-2 h-2 bg-green-500 rounded-full"></div>
                                      <span className="text-xs text-green-600">Playing</span>
                                    </div>
                                  )}
                                  <button
                                    onClick={() => playingAudio === agent.audio_url ? stopAudio() : playAudio(agent.audio_url)}
                                    className={`p-1 rounded-full transition-colors ${
                                      agent.name === 'Alpha'
                                        ? 'hover:bg-red-200 text-red-600'
                                        : 'hover:bg-blue-200 text-blue-600'
                                    }`}
                                  >
                                    {playingAudio === agent.audio_url ? (
                                      <Pause className="h-4 w-4" />
                                    ) : (
                                      <Play className="h-4 w-4" />
                                    )}
                                  </button>
                                </div>
                              </div>
                              <p className="text-gray-800">{agent.text}</p>
                            </div>
                          </div>
                        ))}
                        
                        {/* Completion message */}
                        <div className="flex justify-center">
                          <div className="bg-green-50 border border-green-200 rounded-lg px-6 py-4 max-w-lg text-center">
                            <div className="flex items-center justify-center space-x-2 mb-2">
                              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                              <p className="text-green-800 font-semibold">Session Complete!</p>
                            </div>
                            <p className="text-green-700">{message.completionMessage}</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {/* Show stage and EFT skill changes */}
                        {(message.stage || message.eft_skill || message.eft_subskill) && (
                          <div className="flex justify-center">
                            <div className="bg-gray-100 border border-gray-300 rounded-lg px-4 py-2 text-xs max-w-md">
                              {message.stage && (
                                <span className="text-primary-600 font-medium">
                                  Stage: {message.stage}
                                </span>
                              )}
                              {message.stage && message.eft_skill && <span className="mx-2">•</span>}
                              {message.eft_skill && (
                                <span className="text-green-600 font-medium">
                                  EFT: {message.eft_skill}
                                </span>
                              )}
                              {message.eft_subskill && (
                                <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                                  <p className="text-green-800 font-medium">{message.eft_subskill.name}</p>
                                  <p className="text-green-700 mt-1">{message.eft_subskill.description}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {message.agents?.map((agent, agentIndex) => (
                          <div key={agentIndex} className={`flex ${
                            agent.name === 'Alpha' ? 'justify-start' : 'justify-end'
                          }`}>
                            <div className={`rounded-lg px-4 py-3 max-w-md ${
                              agent.name === 'Alpha' 
                                ? 'bg-red-50 border border-red-200' 
                                : 'bg-blue-50 border border-blue-200'
                            }`}>
                              <div className="flex items-center justify-between mb-2">
                                <p className={`text-sm font-medium ${
                                  agent.name === 'Alpha' ? 'text-red-700' : 'text-blue-700'
                                }`}>
                                  {agent.name} ({agent.name === 'Alpha' ? 'Demander' : 'Withdrawer'})
                                </p>
                                <div className="flex items-center space-x-2">
                                  {playingAudio === agent.audio_url && (
                                    <div className="flex items-center space-x-1">
                                      <div className="animate-pulse w-2 h-2 bg-green-500 rounded-full"></div>
                                      <span className="text-xs text-green-600">Playing</span>
                                    </div>
                                  )}
                                  <button
                                    onClick={() => playingAudio === agent.audio_url ? stopAudio() : playAudio(agent.audio_url)}
                                    className={`p-1 rounded-full transition-colors ${
                                      agent.name === 'Alpha'
                                        ? 'hover:bg-red-200 text-red-600'
                                        : 'hover:bg-blue-200 text-blue-600'
                                    }`}
                                  >
                                    {playingAudio === agent.audio_url ? (
                                      <Pause className="h-4 w-4" />
                                    ) : (
                                      <Play className="h-4 w-4" />
                                    )}
                                  </button>
                                </div>
                              </div>
                              <p className="text-gray-800">{agent.text}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                        <p className="text-sm text-gray-600">Agents are responding...</p>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-gray-200 p-4">
                {/* Session Completion Status */}
                {isSessionCompleted && (
                  <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <p className="text-green-800 font-medium">Session Completed!</p>
                    </div>
                    <p className="text-green-700 text-sm mt-1">
                      The therapy session has ended successfully. Click "New Session" to start practicing again.
                    </p>
                  </div>
                )}
                
                {/* Wrap-up Progress */}
                {!isSessionCompleted && wrapUpTurnsRemaining !== null && wrapUpTurnsRemaining > 0 && (
                  <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
                      <p className="text-yellow-800 font-medium">Session Wrap-up</p>
                    </div>
                    <p className="text-yellow-700 text-sm mt-1">
                      {wrapUpTurnsRemaining} more exchanges before automatic completion.
                    </p>
                  </div>
                )}

                {/* Agent Selection */}
                {!isSessionCompleted && (
                  <div className="mb-3">
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 block">
                      Address:
                    </label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setSelectedAgents('both')}
                        className={`px-3 py-1 text-sm rounded-lg transition-colors flex items-center space-x-1 ${
                          selectedAgents === 'both'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <Users className="h-3 w-3" />
                        <span>Both</span>
                      </button>
                      <button
                        onClick={() => setSelectedAgents('alpha')}
                        className={`px-3 py-1 text-sm rounded-lg transition-colors flex items-center space-x-1 ${
                          selectedAgents === 'alpha'
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <UserCheck className="h-3 w-3" />
                        <span>Alpha</span>
                      </button>
                      <button
                        onClick={() => setSelectedAgents('beta')}
                        className={`px-3 py-1 text-sm rounded-lg transition-colors flex items-center space-x-1 ${
                          selectedAgents === 'beta'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <UserCheck className="h-3 w-3" />
                        <span>Beta</span>
                      </button>
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !isSessionCompleted && sendMessage()}
                    placeholder={
                      isSessionCompleted 
                        ? "Session completed - Click 'New Session' to continue practicing"
                        : `Enter your therapeutic intervention ${
                          selectedAgents === 'both' ? 'to both agents' : 
                          selectedAgents === 'alpha' ? 'to Alpha' : 'to Beta'
                        }...`
                    }
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled={isSessionCompleted}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isSessionCompleted}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    <Send className="h-4 w-4" />
                    <span>Send</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Difficulty Settings */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                <Settings className="h-4 w-4 mr-2" />
                Difficulty Settings
              </h3>
              <div className="space-y-2">
                {['easy', 'normal', 'hard'].map(difficulty => (
                  <button
                    key={difficulty}
                    onClick={() => setDifficulty(difficulty)}
                    className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
                      sessionInfo.difficulty === difficulty
                        ? difficulty === 'easy' ? 'bg-green-50 text-green-700 border border-green-200' :
                          difficulty === 'hard' ? 'bg-red-50 text-red-700 border border-red-200' :
                          'bg-orange-50 text-orange-700 border border-orange-200'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</span>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            openScenarioEditor(difficulty);
                            setShowScenarioEditor(true);
                          }}
                          className="p-1 rounded-full hover:bg-current hover:bg-opacity-20 transition-colors"
                          title="Edit scenario"
                        >
                          <Edit3 className="h-3 w-3" />
                        </button>
                        {sessionInfo.difficulty === difficulty && (
                          <div className="w-2 h-2 rounded-full bg-current"></div>
                        )}
                      </div>
                    </div>
                    <p className="text-xs mt-1 opacity-75">
                      {difficulty === 'easy' ? 'Agents are more open to interventions' :
                       difficulty === 'hard' ? 'Agents are highly resistant' :
                       'Realistic responses to therapy'}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Editor */}
      {showScenarioEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                Edit {editingScenario.difficulty.charAt(0).toUpperCase() + editingScenario.difficulty.slice(1)} Scenario
              </h2>
              <button
                onClick={() => {
                  setShowScenarioEditor(false);
                  setEditingScenario({difficulty: '', text: ''});
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="flex-1 p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scenario Description
                </label>
                <p className="text-sm text-gray-600 mb-4">
                  Define the background story and context for this difficulty level. This will influence how the agents behave and respond to therapeutic interventions.
                </p>
              </div>
              
              <textarea
                value={editingScenario.text}
                onChange={(e) => setEditingScenario(prev => ({...prev, text: e.target.value}))}
                className="w-full h-48 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder={`Enter the scenario description for ${editingScenario.difficulty} difficulty level...`}
              />
              
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Tips for writing scenarios:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• <strong>Easy:</strong> Couples with minor issues, willing to work together</li>
                  <li>• <strong>Normal:</strong> Typical relationship challenges with some resistance</li>
                  <li>• <strong>Hard:</strong> Severe distress, highly defensive, resistant to change</li>
                </ul>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowScenarioEditor(false);
                  setEditingScenario({difficulty: '', text: ''});
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={saveScenario}
                disabled={!editingScenario.text.trim()}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Save className="h-4 w-4" />
                <span>Save Scenario</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App; 