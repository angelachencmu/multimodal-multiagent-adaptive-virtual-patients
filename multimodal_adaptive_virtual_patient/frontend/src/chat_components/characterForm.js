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
    depression_extremely: 1,

    // Anxiety Thresholds
    anxiety_very_slightly: 5.5,
    anxiety_a_little: 4.5,
    anxiety_moderately: 3.5,
    anxiety_quite_a_bit: 2.5,
    anxiety_extremely: 1
  });

    const handleChange = (e) => {
        const { name, value } = e.target;
        let num = parseFloat(value);

        if (isNaN(num)) num = '';

        if (FIELD_LIMITS[name]) {
            const { min, max } = FIELD_LIMITS[name];
            if (num < min) num = min;
            if (num > max) num = max;
        }

        setFormData((prev) => ({
            ...prev,
            [name]: num
        }));
    };


    const FIELD_LIMITS = {
        // empathy weights
        emotional_reactions_weight: { min: 0, max: 1 },
        interpretations_weight: { min: 0, max: 1 },
        explorations_weight: { min: 0, max: 1 },

        // rapport blend
        rapport_blend_weight: { min: 0, max: 1 },

        // difficulty
        difficulty_coefficient: { min: 0.1, max: 3.0 }
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
        });
    };

  return (
    <div className="flex flex-col h-full w-full gap-5 items-center my-5">
        <h1 className="text-purple uppercase font-bold tracking-wide mb-3 text-xl">Behavioral Settings</h1>
        {/* <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-teal w-full text-purple">
            <h1 className="uppercase font-bold tracking-wide text-xl"  title="Weights should sum to 1.0">Empathy Weights</h1>
            <p className='mb-5'>Weights must sum to 1</p>
            <form className="flex flex-col gap-3">
            <label>
                Emotional Reactions: 
                <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    name="emotional_reactions_weight"
                    value={formData.emotional_reactions_weight}
                    onChange={handleChange}
                    className="text-purple border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Interpretations:
                <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                name="interpretations_weight"
                value={formData.interpretations_weight}
                onChange={handleChange}
                className="text-purple border rounded-xl p-2 w-full"
                />
            </label>
            <label>
                Explorations:
                <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                name="explorations_weight"
                value={formData.explorations_weight}
                onChange={handleChange}
                className="text-purple border rounded-xl p-2 w-full"
                />
            </label>
            </form>
        </div> */}

        <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-teal w-full text-purple">
            {/* <h1 className="uppercase font-bold tracking-wide text-xl">SEM Coefficients for Rapport Inference</h1>
            <p className='mb-5'>Used to compute inferred rapport score from empathy scores</p> */}
            <form className="flex flex-col gap-3">
            {/* <label>
                Interpretations:
                <input
                type="number"
                step="0.001"
                name="interpretations_coeff"
                value={formData.interpretations_coeff}
                onChange={handleChange}
                className="text-purple border rounded-xl p-2 w-full"
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
                className="text-purple border rounded-xl p-2 w-full"
                />
            </label> */}
            {/* <label>
                Emotional Reactions:
                <input
                type="number"
                step="0.001"
                name="emotional_reactions_coeff"
                value={formData.emotional_reactions_coeff}
                onChange={handleChange}
                className="text-purple border rounded-xl p-2 w-full"
                />
            </label> */}
            {/* <label>
                Rapport Blend Weight:
                <p className='text-xs mb-3'>Min: 0, Max: 1</p>
                <input
                type="number"
                step="0.01"
                min="0" 
                max="1"
                name="rapport_blend_weight"
                value={formData.rapport_blend_weight}
                onChange={handleChange}
                className="text-purple border rounded-xl p-2 w-full"
                />
            </label> */}
            <label>
                Difficulty Level Coefficient:
                <p className='text-xs mb-3'>Min: 0.1, Max: 3</p>
                <input
                type="number"
                step="0.1"
                min="0.1" 
                max="3.0"
                name="difficulty_coefficient"
                value={formData.difficulty_coefficient}
                onChange={handleChange}
                className="text-purple border rounded-xl p-2 w-full"
                />
            </label>
            </form>
        </div>

        {/* <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-teal w-full text-purple">
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
                    className="text-purple border rounded-xl p-2 w-full"
                />
                </label>
            ))}
            </form>
        </div> */}

        {/* <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-teal w-full text-purple">
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
                    className="text-purple border rounded-xl p-2 w-full"
                />
                </label>
            ))}
            </form>
        </div> */}

        <div className="flex-none flex flex-row gap-4 justify-center">
            <button
            onClick={handleSubmit}
            className="mt-2 px-4 py-2 rounded-full bg-teal tracking-wide border-4 border-solid duration-300 border-teal text-purple w-full uppercase font-bold hover:tracking-wider hover:bg-white hover:text-purple">
            Submit & Save Settings
            </button>
        </div>
        <p>Last Updated: {formUpdate}</p>
        </div>
    );
}
