import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import { UserCircleIcon } from '@heroicons/react/24/solid';
import { ArrowRightCircleIcon } from '@heroicons/react/24/solid';
import { BookmarkSquareIcon } from '@heroicons/react/24/solid';
import { useState, useEffect } from "react";
import CharacterMemory from './characterMemory';

export default function Chat({ selected, setSelected, messages, setMessages, name, session, updateSession, resetCharacter, isLoading, setIsLoading }) {
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [characterMemory, setCharacterMemory] = useState({
        summary: "",
        currentRepo: "",
        fullRepo: "",
    });
    const [SEM, setSEM] = useState({
        emotion: [],
        depression: [],
        empathy: [],
        rapport: [],
        rapportBlended: [],
        behaviorState: []
    });

    const [messageDisplay, setMessageDisplay] = useState([]);
    const [characterMemoryDisplay, setCharacterMemoryDisplay] = useState(characterMemory);
    const [SEMDisplay, setSEMDisplay] = useState(SEM);

    const [selectedSession, setSelectedSession] = useState(session);

    const handleSessionChange = (selectedSession) => {
        setSelectedSession(selectedSession);
        const snapshot = loadSnapshotForSession(name, selectedSession);
        if (selectedSession !== session) {
            setSelected(false);
            setCharacterMemoryDisplay(snapshot.characterMemory);
            setSEMDisplay(snapshot.SEM);
            setMessageDisplay(snapshot.messages || {});
        } else {
            setSelected(true);
            setCharacterMemoryDisplay(characterMemory);
            setSEMDisplay(SEM);
        }
    };


    const loadSnapshotForSession = (characterName, sessionIndex) => {
        const allSnapshots = JSON.parse(localStorage.getItem('chatSnapshots') || '[]');
        return allSnapshots[characterName][sessionIndex - 1];
    };



    useEffect(() => {
        setSelectedSession(session);
    }, [session]);

    const progressSession = async () => {
        try {
            setIsLoading(true);
            setSelected(false);
            const response = await fetch(`${process.env.REACT_APP_API_URL}/progress-session`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });

            const data = await response.json();
            updateSession(data.characterCard, messages, SEM, characterMemory);
            setCharacterMemory({
                summary: "",
                currentRepo: "",
                fullRepo: "",
            });
            setSEM({
                emotion: [],
                depression: [],
                empathy: [],
                rapport: [],
                rapportBlended: [],
                behaviorState: []
            });
            setCharacterMemoryDisplay({
                summary: "",
                currentRepo: "",
                fullRepo: "",
            });
            setSEMDisplay({
                emotion: [],
                depression: [],
                empathy: [],
                rapport: [],
                rapportBlended: [],
                behaviorState: []
            });
            setMessages([]);
            setIsLoading(false);
            setSelected(true);
        } catch (error) {
        console.error("Failed to fetch:", error);
        }
    };

    const getSEM = async() => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/get-SEM-info`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input }),
            });

            const data = await response.json();
            setSEM(data.SEM);
            setSEMDisplay(data.SEM);
        } catch (error) {
            console.error("Failed to fetch:", error);
        }
    }

    const getCharacterMemory = async() => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/get-character-memory`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input }),
            });

            const data = await response.json();
            setCharacterMemory(data.characterMemory);
            setCharacterMemoryDisplay(data.characterMemory);
        } catch (error) {
            console.error("Failed to fetch:", error);
        }
    }

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        try {
        setIsTyping(true);
        const response = await fetch(`${process.env.REACT_APP_API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: input }),
        });

        const data = await response.json();
        const patientMessage = { role: "assistant", content: data.reply, audio: `${process.env.REACT_APP_API_URL}${data.tts}`};
        setMessages((prev) => [...prev, patientMessage]);

        console.log(`${process.env.REACT_APP_API_URL}${data.tts}`);
        const audio = new Audio(`${process.env.REACT_APP_API_URL}${data.tts}`);
        audio.play().catch((err) => {
            console.error("Audio playback failed:", err);
        });

        getCharacterMemory();
        getSEM();
        } catch (error) {
        console.error("Failed to fetch:", error);
        } finally {
        setIsTyping(false);
        }
    };

    const saveChatHistory = () => {
        if (!messages || messages.length === 0) {
            alert("No messages to save.");
            return;
        }

        let saveMessage = [];
        if (selectedSession !== session) {
            saveMessage = messageDisplay;
        } else {
            saveMessage = messages;
        }

        const formatted = saveMessage.map(msg => {
            if (msg.role === "user") return `Therapist: ${msg.content}`;
            else if (msg.role === "assistant") return `Patient: ${msg.content}`;
            else return `${msg.role}: ${msg.content}`;
        }).join("\n");

        // trigger download
        const blob = new Blob([formatted], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${name}-chat-history-session${selectedSession}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };


    return (
        <div className="flex flex-col h-full w-full border p-4 rounded-xl shadow bg-white">
            <div className='flex flex-grow h-full'>
                <div className='w-2/3 flex flex-col h-full'>
                    <div className='h-16 bg-teal p-5 flex gap-5 items-center rounded-t-lg justify-between items-center'>
                        <div className='flex gap-5'>
                            <button
                                onClick={saveChatHistory}
                            >
                                <BookmarkSquareIcon className="flex-shrink-0 h-5 w-5 text-purple" />
                            </button>
                            <h1 className='text-purple uppercase font-bold tracking-wide'>{name}</h1>
                        </div>
                        <div className='flex items-center justify-center gap-2 text-purple'>
                            <select
                                value={selectedSession}
                                onChange={(e) => handleSessionChange(Number(e.target.value))}
                                className="border rounded px-2 py-1 text-purple bg-white"
                                >
                                {Array.from({ length: session }, (_, i) => (
                                    <option key={i + 1} value={i + 1}>
                                    Session {i + 1}
                                    </option>
                                ))}
                            </select>
                            <button
                            disabled={!selected}
                            onClick={progressSession}
                            className="font-bold pl-4 py-1"
                            > 
                                <ArrowRightCircleIcon className="flex-shrink-0 h-10 w-10 text-purple" />
                            </button>
                            <button
                                disabled={!selected}
                                className="px-4 py-1 duration-300"
                                onClick={resetCharacter}
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="#1f7a8c" className="size-6">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    {isLoading && (
                        <div className="flex w-full h-full bg-white p-5 transparent-scrollbar justify-center items-center text-purple">
                            processing request...
                        </div>
                    )}
                   {selectedSession !== session ? (
                    <div className="flex-1 overflow-y-auto bg-white p-5 transparent-scrollbar">
                        {messageDisplay.map((msg, index) => (
                            <div
                            key={index}
                            className={`flex mb-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                            {msg.role === "user" ? (
                                <>
                                <div className="mr-2 py-3 px-4 bg-coral rounded-bl-3xl rounded-tl-3xl rounded-tr-xl text-white max-w-[70%]">
                                    {msg.content}
                                </div>
                                <UserCircleIcon className="flex-shrink-0 h-10 w-10 text-coral" />
                                </>
                            ) : (
                                <>
                                <UserCircleIcon className="flex-shrink-0 h-10 w-10 text-blue" />
                                <div className="ml-2 py-3 px-4 bg-blue rounded-br-3xl rounded-tr-3xl rounded-tl-xl text-purple max-w-[70%]">
                                    {msg.content}
                                </div>
                                </>
                            )}
                            </div>
                        ))}
                    </div>
                    ) : (   !isLoading && (
                    <div className="flex-1 overflow-y-auto bg-white p-5 transparent-scrollbar">
                        {messages.map((msg, index) => (
                            <div
                            key={index}
                            className={`flex mb-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                            {msg.role === "user" ? (
                                <>
                                <div className="mr-2 py-3 px-4 bg-coral rounded-bl-3xl rounded-tl-3xl rounded-tr-xl text-white max-w-[70%]">
                                    {msg.content}
                                </div>
                                <UserCircleIcon className="flex-shrink-0 h-10 w-10 text-coral" />
                                </>
                            ) : (
                                <>
                                <UserCircleIcon className="flex-shrink-0 h-10 w-10 text-blue" />
                                
                                <div className="flex ml-2 py-3 px-4 bg-blue rounded-br-3xl rounded-tr-3xl rounded-tl-xl text-purple max-w-[70%]">
                                    {msg.content}
                                    {msg.audio && (
                                    <button
                                        onClick={() => {
                                        const audio = new Audio(msg.audio);
                                        audio.play().catch(err => {
                                            console.error("Audio playback failed:", err);
                                        });
                                        }}
                                        className="h-8 text-sm text-purple px-2"
                                    >
                                        ▶ 
                                    </button>
                                    )}
                                </div>
                            </>
                            )}
                            </div>
                        ))}
                    </div>
                    ))}
                    {isTyping && (
                    <div className="italic text-gray-500 ml-2 p-2">{name} is typing...</div>
                    )}
                    <div className="flex items-center bg-teal p-2 rounded-b-lg">
                        <input
                            disabled={!selected}
                            type="text"
                            placeholder="Type your message..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                            className="border p-2 w-full rounded-xl"
                        />
                        <button
                            disabled={!selected}
                            onClick={sendMessage}
                            className="ml-2 px-4 py-2 rounded"
                        >
                            <PaperAirplaneIcon className="h-8 w-8 text-purple" />
                        </button>
                    </div>
                </div>
                <div className='w-1/3'>
                    <CharacterMemory memoryInfo={characterMemoryDisplay} SEM = {SEMDisplay} />
                </div>
            </div>
        </div>
    );
}