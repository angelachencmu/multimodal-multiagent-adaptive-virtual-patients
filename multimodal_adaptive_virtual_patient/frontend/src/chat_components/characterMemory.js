export default function CharacterMemory({ memoryInfo, SEM }) {
  return (
    <div className="flex flex-col h-full px-5 w-full gap-5 overflow-y-auto transparent-scrollbar">
      <div className="flex-none flex flex-col gap-5 border p-4 rounded-xl shadow bg-coral w-full text-white">
        <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">Memory Information</h1>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-coral">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Session Summary</h2>
          <p>{memoryInfo.summary ?? "(none)"}</p>
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-coral">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Long Term Memory</h2>
          <h3><strong>Current Repository:</strong> {memoryInfo.currentRepo ?? "(none)"} </h3>
          <h3 className="font-bold">Full Repository</h3>
          <p>{memoryInfo.fullRepo ?? "(none)"}</p>
        </div>
      </div>
      <div className="flex-none gap-5 flex flex-col border p-4 rounded-xl shadow bg-purple w-full text-white">
        <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">SEM Information</h1>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Emotion</h2>
          <div className="max-h-32 overflow-y-auto">
            {SEM.emotion.slice().map((emotion, index) => (
              <div key={index}>
                <h3>Turn {index + 1}: {emotion ?? "(none)"} </h3>
              </div>
            ))}
          </div>
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Depression</h2>
            <div className="max-h-32 overflow-y-auto">
              {SEM.depression.slice().map((depression, index) => (
                <div key={index}>
                  <h3>Turn {index + 1}: {depression ?? "(none)"} </h3>
                </div>
              ))}
            </div>
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Empathy Tracker</h2>
            <div className="max-h-96 overflow-y-auto flex flex-col gap-5">
              {SEM.empathy?.map((entry, index) => (
              <div key={index}>
                <h3>Turn {index + 1}:</h3>
                <p><strong>Explanation:</strong> {entry.explanation}</p>
                <p><strong>Emotional Reactions:</strong> {entry.emotional_reactions}</p>
                <p><strong>Interpretations:</strong> {entry.interpretations}</p>
                <p><strong>Explorations:</strong> {entry.explorations}</p>
                {entry.behavioral_states && (
                  <p><strong>Behavioral States:</strong> {entry.behavioral_states}</p>
                )}
              </div>
            ))}
            </div>
        </div>
        <h3><strong>Behavioral States:</strong>  </h3>
        <h3><strong>Empathy Tracker:</strong> </h3>
        <h3><strong>Rapport Tracker:</strong>  </h3>

      </div>
    </div>
  )
}
