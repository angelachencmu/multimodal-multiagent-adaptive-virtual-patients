import { useState, useEffect } from "react";
import Chat from "./chat_components/chat";
import CharacterProfile from "./chat_components/characterProfile";

export default function App() {
  // Shared state
  const [messages, setMessages] = useState([]);
  const [selected, setSelected] = useState(false);
  const [characterCard, setCharacterCard] = useState({
    name: "",
    identity: [],
    keyBackground: [],
    personality: "",
    session: 0,
    context: ""
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    localStorage.clear();

    const restart = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/restart-webpage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "reset" }),
        });
        console.log(await response.json());
      } catch (error) {
        console.error("Failed to fetch:", error);
      }
    };

    restart();
  }, []);

  const updateSession = (characterCard, snapMessages, SEM, characterMemory) => {
    setCharacterCard(characterCard);

    const snapshot = {
      characterName: characterCard.name,
      session: characterCard.session,
      characterCard: characterCard,
      messages: snapMessages,
      characterMemory: characterMemory,
      SEM: SEM,
      timestamp: Date.now()
    };

    const existing = JSON.parse(localStorage.getItem('chatSnapshots') || '{}');

    if (!existing[characterCard.name]) {
      existing[characterCard.name] = [];
    }

    existing[characterCard.name].push(snapshot);
    existing[characterCard.name].sort((a, b) => a.session - b.session);

    localStorage.setItem('chatSnapshots', JSON.stringify(existing));
  };


  const resetCharacter = async() => {
    try {
        setIsLoading(true);
        setSelected(false);
        const response = await fetch(`${process.env.REACT_APP_API_URL}/reset-character`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "true" }),
        });

        const data = await response.json();
        setCharacterCard(data.characterCard);

        // Clear chat and name on character switch
        setMessages([]);
        setIsLoading(false);
        setSelected(true);
    } catch (error) {
        console.error("Failed to fetch:", error);
    }
  }


  // Change character and clear chat
  const handleChangeCharacter = async (characterName) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/change-character`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ character: characterName }),
      });

      const data = await response.json();
      setCharacterCard(data.characterCard);

      // Clear chat and name on character switch
      setMessages([]);
      setSelected(true);
    } catch (error) {
      console.error("Error changing character:", error);
    }
  };

  return (
    <div className="flex bg-blue p-5 h-screen">
      <div className="h-[95vh] w-1/4">
        <CharacterProfile
          changeCharacter={handleChangeCharacter}
          characterCard={characterCard}
        />
      </div>
      <div className="h-[95vh] w-3/4">
        <Chat
        selected={selected}
        setSelected={setSelected}
        messages={messages}
        setMessages={setMessages}
        name={characterCard.name}
        session={characterCard.session}
        updateSession={updateSession}
        resetCharacter={resetCharacter}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
      />
      </div>
    </div>
  );
}
