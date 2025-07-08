import { useState } from 'react';

export default function SEMSettingsForm() {
    const [formUpdate, setFormUpdated] = useState("");
    const [formData, setFormData] = useState({
    // Empathy Weights
    emotional_reactions_weight: 0.4,
    interpretations_weight: 0.3,
    explorations_weight: 0.3,

    // Rapport Coefficients
    interpretations_coeff: 0.103,
    explorations_coeff: 0.055,
    emotional_reactions_coeff: 0.017,
    rapport_blend_weight: 0.7,
    difficulty_coefficient: 1,

    // Depression Thresholds
    depression_very_slightly: 5.5,
    depression_a_little: 4.5,
    depression_moderately: 3.5,
    depression_quite_a_bit: 2.5,
    depression_extremely: 0,

    // Anxiety Thresholds
    anxiety_very_slightly: 5.5,
    anxiety_a_little: 4.5,
    anxiety_moderately: 3.5,
    anxiety_quite_a_bit: 2.5,
    anxiety_extremely: 0
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };

const handleSubmit = (e) => {
  console.log("updating settings")

  fetch(`${process.env.REACT_APP_API_URL}/new-weights`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(formData)
  })
    .then((res) => res.json())
    .then((data) => {
        setFormUpdated(data.time);
        console.log(formUpdate);
    });
};

  return (
    <div className="flex flex-col h-full w-full gap-5 items-center my-5">
        <h1 className="text-blue uppercase font-bold tracking-wide mb-3 text-xl">Behavioral Settings</h1>
        <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-blue w-full text-white">
            <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">Empathy Weights</h1>
            <form className="flex flex-col gap-3">
            <label>
                Emotional Reactions:
                <input
                type="number"
                step="0.001"
                name="emotional_reactions_weight"
                value={formData.emotional_reactions_weight}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Interpretations:
                <input
                type="number"
                step="0.001"
                name="interpretations_weight"
                value={formData.interpretations_weight}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Explorations:
                <input
                type="number"
                step="0.001"
                name="explorations_weight"
                value={formData.explorations_weight}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            </form>
        </div>

        <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-blue w-full text-white">
            <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">SEM Coefficients for Rapport Inference</h1>
            <form className="flex flex-col gap-3">
            <label>
                Interpretations:
                <input
                type="number"
                step="0.001"
                name="interpretations_coeff"
                value={formData.interpretations_coeff}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Explorations:
                <input
                type="number"
                step="0.001"
                name="explorations_coeff"
                value={formData.explorations_coeff}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Emotional Reactions:
                <input
                type="number"
                step="0.001"
                name="emotional_reactions_coeff"
                value={formData.emotional_reactions_coeff}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Rapport Blend Weight:
                <input
                type="number"
                step="0.01"
                name="rapport_blend_weight"
                value={formData.rapport_blend_weight}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Difficulty Level Coefficient:
                <input
                type="number"
                step="0.1"
                name="difficulty_coefficient"
                value={formData.difficulty_coefficient}
                onChange={handleChange}
                className="text-blue border rounded-xl p-2 w-full"
                />
            </label>
            </form>
        </div>

        <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-blue w-full text-white">
            <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">Depression Thresholds</h1>
            <form className="flex flex-col gap-3">
            {['very_slightly','a_little','moderately','quite_a_bit','extremely'].map((level) => (
                <label key={level}>
                {level.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:
                <input
                    type="number"
                    step="0.1"
                    name={`depression_${level}`}
                    value={formData[`depression_${level}`]}
                    onChange={handleChange}
                    className="text-blue border rounded-xl p-2 w-full"
                />
                </label>
            ))}
            </form>
        </div>

        <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-blue w-full text-white">
            <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">Anxiety Thresholds</h1>
            <form className="flex flex-col gap-3">
            {['very_slightly','a_little','moderately','quite_a_bit','extremely'].map((level) => (
                <label key={level}>
                {level.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:
                <input
                    type="number"
                    step="0.1"
                    name={`anxiety_${level}`}
                    value={formData[`anxiety_${level}`]}
                    onChange={handleChange}
                    className="text-blue border rounded-xl p-2 w-full"
                />
                </label>
            ))}
            </form>
        </div>

        <div className="flex-none flex flex-row gap-4 justify-center">
            <button
            onClick={handleSubmit}
            className="mt-2 px-4 py-2 rounded-full bg-blue tracking-wide border-4 border-solid duration-300 border-blue text-white w-full uppercase font-bold hover:tracking-wider hover:bg-white hover:text-blue">
            Submit & Save Settings
            </button>
        </div>
        <p>Last Updated: {formUpdate}</p>
        </div>
    );
}
