import { useState } from 'react';

export default function CharacterMemory({ memoryInfo, SEM }) {
  const [openSections, setOpenSections] = useState({
    sessionSummary: true,
    longTermMemory: true,
    longTermMemoryfull: false,
    emotion: true,
    depression: true,
    empathyTracker: true,
    rapportTracker: true,
    behavioralStates: true,
  });

  const toggleSection = (key) => {
    setOpenSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };
  
  return (
    <div className="flex flex-col h-full px-5 w-full gap-5 overflow-y-auto transparent-scrollbar">
      <div className="flex-none flex flex-col gap-5 border p-4 rounded-xl shadow bg-coral w-full text-white">
        <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">Memory Information</h1>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-coral">
          <div className="flex justify-between items-center mb-5">
            <h2 className="uppercase font-bold tracking-wide text-lg">Session Summary</h2>
            <button
              className="text-sm "
              onClick={() => toggleSection('sessionSummary')}
            >
              {openSections.sessionSummary ? '▲' : '▼'}
            </button>
          </div>
          {openSections.sessionSummary && (
            <ul className="list-none max-h-96 overflow-y-auto transparent-scrollbar pr-3 mb-3">
              {(memoryInfo.summary ?? "(none)")
                .split('\n')
                .map((line, index) => (
                  <li key={index} className='mb-3'>{line}</li>
                ))}
            </ul>
          )}
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-coral">
          <div className="flex justify-between items-center mb-5">
            <h2 className="uppercase font-bold tracking-wide text-lg">Long Term Memory</h2>
            <button
              className="text-sm "
              onClick={() => toggleSection('longTermMemory')}
            >
              {openSections.longTermMemory ? '▲' : '▼'}
            </button>
          </div>
          {openSections.longTermMemory && (
            <>
              <h3><strong>Current Repository:</strong> </h3>
              <div className='max-h-96 overflow-y-auto transparent-scrollbar flex flex-col gap-5 pr-3 mt-3'>
                {openSections.longTermMemory && (
                  <ul className="list-none">
                    {(memoryInfo.currentRepo ?? "(none)")
                      .split('\n')
                      .map((line, index) => (
                        <li key={index}>{line}</li>
                      ))}
                  </ul>
                )}
              </div>
              <div className="flex justify-between items-center my-5">
                <h3 className="font-bold">Full Repository</h3>
                <button
                  className="text-sm "
                  onClick={() => toggleSection('longTermMemoryfull')}
                >
                  {openSections.longTermMemoryfull ? '▲' : '▼'}
                </button>
              </div>
              {openSections.longTermMemoryfull && (
                <ul className="list-disc pl-5 max-h-96 overflow-y-auto transparent-scrollbar pr-3 mb-3">
                  {(memoryInfo.fullRepo ?? "(none)")
                    .split('\n')
                    .map((line, index) => (
                      <li key={index}>{line}</li>
                    ))}
                </ul>
              )}
            </>
          )}
        </div>
      </div>
      <div className="flex-none gap-5 flex flex-col border p-4 rounded-xl shadow bg-purple w-full text-white">
        <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">SEM Information</h1>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <div className="flex justify-between items-center mb-5">
            <h2 className="uppercase font-bold tracking-wide text-lg">Emotion</h2>
            <button
              className="text-sm "
              onClick={() => toggleSection('emotion')}
            >
              {openSections.emotion ? '▲' : '▼'}
            </button>
          </div>
          {openSections.emotion && (
            <div className="max-h-32 overflow-y-auto transparent-scrollbar">
            {SEM.emotion.slice().map((emotion, index) => (
              <div key={index}>
                <h3>Turn {index + 1}: {emotion ?? "(none)"} </h3>
              </div>
            ))}
            </div>
          )}          
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
        <div className="flex justify-between items-center mb-5">
          <h2 className="uppercase font-bold tracking-wide text-lg">Depression</h2>
          <button
            className="text-sm "
            onClick={() => toggleSection('depression')}
          >
            {openSections.depression ? '▲' : '▼'}
          </button>
        </div>
        {openSections.depression && (
          <div className="max-h-32 overflow-y-auto transparent-scrollbar">
            {SEM.depression.slice().map((depression, index) => (
                <div key={index}>
                  <h3>Turn {index + 1}: {depression ?? "(none)"} </h3>
                </div>
            ))}
          </div>
        )}
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <div className="flex justify-between items-center mb-5">
            <h2 className="uppercase font-bold tracking-wide text-lg">Empathy Tracker</h2>
            <button
              className="text-sm "
              onClick={() => toggleSection('empathyTracker')}
            >
              {openSections.empathyTracker ? '▲' : '▼'}
            </button>
          </div>
          {openSections.empathyTracker && (
            <div className="max-h-96 overflow-y-auto transparent-scrollbar flex flex-col gap-5">
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
                  {SEM.rapportBlended?.[index] && (
                    <>
                      <p><strong>Rapport Blended:</strong> {SEM.rapportBlended[index].blended}</p>
                      <p><strong>Empathy-Rapport Score:</strong> {SEM.rapportBlended[index].empathy}</p>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <div className="flex justify-between items-center mb-5">
          <h2 className="uppercase font-bold tracking-wide text-lg">Rapport Tracker</h2>
          <button
            className="text-sm "
            onClick={() => toggleSection('rapportTracker')}
          >
            {openSections.rapportTracker ? '▲' : '▼'}
          </button>
        </div>
        {openSections.rapportTracker && (
          <div className="max-h-96 overflow-y-auto transparent-scrollbar flex flex-col gap-5">
              {SEM.rapport?.map((entry, index) => (
              <div key={index}>
                <h3>Checkpoint {index + 1}:</h3>
                <p><strong>Overall Rating:</strong> {entry.overall_rating}</p>
                <p><strong>Mutual Liking:</strong> {entry.mutual_liking}</p>
                <p><strong>Confidence:</strong> {entry.confidence}</p>
                <p><strong>Appreciation:</strong> {entry.appreciation}</p>
                <p><strong>Mutual Trust:</strong> {entry.mutual_trust}</p>
                <p><strong>Explanation:</strong><br />
                  <span className="text-gray-700">{entry.explanation}</span>
                </p>
              </div>
              ))}
          </div>
        )}
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
          <div className="flex justify-between items-center mb-5">
          <h2 className="uppercase font-bold tracking-wide text-lg">Behavioral States</h2>
          <button
            className="text-sm "
            onClick={() => toggleSection('behavioralStates')}
          >
            {openSections.behavioralStates ? '▲' : '▼'}
          </button>
        </div>
        {openSections.behavioralStates && (
          <div className="max-h-96 overflow-y-auto transparent-scrollbar flex flex-col gap-5">
              {SEM.behaviorState?.map((entry, index) => (
              <div key={index}>
                <h3>Turn {index + 1}:</h3>
                <p><strong>Depression:</strong> {entry.depression}</p>
                <p><strong>Anxiety:</strong> {entry.anxiety}</p>
                <p><strong>Self-Disclosure:</strong> {entry.selfDisclosure}</p>
              </div>
            ))}
          </div>
        )}            
        </div>
      </div>
    </div>
  )
}
