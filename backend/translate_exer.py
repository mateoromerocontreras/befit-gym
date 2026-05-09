import json

translations_exercises = {
    "Sentadilla con Barra": ("Barbell Squat", "Back squat to develop overall leg and core strength."),
    "Sentadilla Frontal": ("Front Squat", "Front bar variant emphasizing quads and torso stability."),
    "Peso Muerto Convencional": ("Conventional Deadlift", "Basic posterior chain movement for total strength."),
    "Peso Muerto Rumano": ("Romanian Deadlift", "Focused on hamstrings and glutes with eccentric control."),
    "Press de Banca Plano": ("Flat Bench Press", "Main horizontal pushing exercise for chest."),
    "Press de Banca Inclinado": ("Incline Bench Press", "Incline variant to emphasize upper chest."),
    "Press Militar de Pie": ("Standing Military Press", "Vertical push with barbell for shoulders and triceps."),
    "Remo con Barra": ("Barbell Row", "Horizontal pull for lats, rhomboids and mid-back."),
    "Hip Thrust con Barra": ("Barbell Hip Thrust", "Hip extension for gluteus maximus and lumbo-pelvic stability."),
    "Zancadas con Mancuernas": ("Dumbbell Lunges", "Unilateral leg work and dynamic balance."),
    "Press de Pecho con Mancuernas": ("Dumbbell Chest Press", "Horizontal push with greater range of motion."),
    "Aperturas con Mancuernas": ("Dumbbell Flyes", "Chest isolation on a flat bench."),
    "Remo con Mancuerna a Una Mano": ("One-Arm Dumbbell Row", "Unilateral pull for lats and scapular control."),
    "Curl de Bíceps con Mancuernas": ("Dumbbell Bicep Curl", "Alternating elbow flexion for bicep development."),
    "Press Arnold": ("Arnold Press", "Press with rotation for complete deltoid development."),
    "Elevaciones Laterales": ("Lateral Raises", "Middle deltoid isolation for shoulder width."),
    "Fondos en Paralelas": ("Dips", "Closed chain push for triceps and lower chest."),
    "Dominadas Pronadas": ("Pull-ups (Pronated)", "Vertical pull for lats and upper back."),
    "Dominadas Supinas": ("Chin-ups (Supinated)", "Pull-up variant that increases bicep involvement."),
    "Face Pull en Polea": ("Cable Face Pull", "Posterior deltoid and rotator cuff work."),
    "Jalón al Pecho en Polea": ("Lat Pulldown", "Guided vertical pull for back and lats."),
    "Remo en Polea Baja": ("Seated Cable Row", "Horizontal cable pull for back density."),
    "Cruce de Poleas para Pecho": ("Cable Crossover", "Shoulder adduction on cable for chest."),
    "Extensión de Tríceps en Polea": ("Cable Tricep Extension", "Triceps isolation with controlled range."),
    "Curl de Bíceps en Polea Baja": ("Cable Bicep Curl", "Continuous elbow flexion with cable tension."),
    "Sentadilla en Hack": ("Hack Squat", "Guided squat pattern for quads."),
    "Prensa de Piernas 45°": ("45° Leg Press", "Leg push on an incline plane for strength."),
    "Extensión de Cuádriceps": ("Leg Extension", "Quad isolation on machine."),
    "Curl Femoral Tumbado": ("Lying Leg Curl", "Specific hamstring work on machine."),
    "Sentadilla en Smith": ("Smith Machine Squat", "Guided variant for technical progression and safety."),
    "Press de Hombros en Máquina": ("Machine Shoulder Press", "Guided vertical push for delts and triceps."),
    "Press de Pecho en Máquina": ("Machine Chest Press", "Stable horizontal push for chest hypertrophy."),
    "Remo en Máquina": ("Machine Row", "Guided horizontal pull for lats and rhomboids."),
    "Curl Scott con Barra Z": ("EZ Bar Preacher Curl", "Bicep isolation on Scott bench with EZ bar."),
    "Extensión de Tríceps con Barra Z": ("EZ Bar Skullcrusher", "Triceps work on bench with EZ bar."),
    "Plancha Frontal": ("Front Plank", "Core isometric for trunk stability."),
    "Crunch en Fitball": ("Stability Ball Crunch", "Controlled trunk flexion with unstable support."),
    "Mountain Climbers": ("Mountain Climbers", "Dynamic core exercise and cardiovascular endurance."),
    "Carrera en Cinta": ("Treadmill Running", "Continuous aerobic work for cardiorespiratory capacity."),
    "HIIT en Bicicleta de Spinning": ("Spin Bike HIIT", "High-intensity intervals for VO2 improvement and caloric expenditure.")
}

with open("accounts/fixtures/ejercicios.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    name = item["fields"]["name"]
    if name in translations_exercises:
        item["fields"]["name"] = translations_exercises[name][0]
        item["fields"]["description"] = translations_exercises[name][1]

missing_exercises = [
    {
        "name": "Hex Bar Deadlift",
        "description": "Alternative to conventional deadlift that reduces lower back stress.",
        "muscle_group": "LEGS",
        "difficulty": "INTERMEDIATE",
        "image_url": None,
        "equipment": [33] # Hex Bar pk
    },
    {
        "name": "Kettlebell Swing",
        "description": "Explosive hip hinge movement for posterior chain and conditioning.",
        "muscle_group": "FULL_BODY",
        "difficulty": "INTERMEDIATE",
        "image_url": None,
        "equipment": [4] # Kettlebells pk
    },
    {
        "name": "Russian Twist",
        "description": "Core exercise focusing on obliques and rotational strength.",
        "muscle_group": "CORE",
        "difficulty": "BEGINNER",
        "image_url": None,
        "equipment": [34] # Medicine Ball pk (assume 34)
    },
    {
        "name": "Calf Raises",
        "description": "Isolation exercise for the gastrocnemius and soleus muscles.",
        "muscle_group": "LEGS",
        "difficulty": "BEGINNER",
        "image_url": None,
        "equipment": [36] # Calf raise machine pk
    },
    {
        "name": "Pec Deck Fly",
        "description": "Machine-based chest fly for isolated pectoral development.",
        "muscle_group": "CHEST",
        "difficulty": "BEGINNER",
        "image_url": None,
        "equipment": [38] # Pec Deck pk
    }
]

max_pk = max([i["pk"] for i in data])
for ex in missing_exercises:
    max_pk += 1
    data.append({
        "model": "accounts.exercise",
        "pk": max_pk,
        "fields": ex
    })

with open("accounts/fixtures/ejercicios.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Exercises translated and new ones added!")
