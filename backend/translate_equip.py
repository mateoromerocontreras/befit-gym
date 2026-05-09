import json

translations_equipment = {
    "Barra Olímpica": "Olympic Barbell",
    "Barra Z": "EZ Bar",
    "Mancuernas": "Dumbbells",
    "Pesas Rusas (Kettlebells)": "Kettlebells",
    "Discos": "Weight Plates",
    "Prensa de Piernas": "Leg Press Machine",
    "Máquina de Hack Squat": "Hack Squat Machine",
    "Rack de Poder": "Power Rack",
    "Multiestación": "Cable Multi-Station",
    "Máquina de Extensión de Cuádriceps": "Leg Extension Machine",
    "Camilla de Isquios": "Leg Curl Machine",
    "Smith Machine (Barra Guiada)": "Smith Machine",
    "Polea Alta": "High Pulley",
    "Polea Baja": "Low Pulley",
    "Cruce de Poleas": "Cable Crossover",
    "Cinta de Correr": "Treadmill",
    "Bicicleta Fija": "Stationary Bike",
    "Bicicleta de Spinning": "Spin Bike",
    "Elíptica": "Elliptical",
    "Máquina de Remo": "Rowing Machine",
    "Escaladora (Stairmaster)": "Stairmaster",
    "Banco Plano": "Flat Bench",
    "Banco Inclinado": "Incline Bench",
    "Banco Declinado": "Decline Bench",
    "Banco Scott": "Preacher Curl Bench",
    "Barra de Dominadas": "Pull-up Bar",
    "Barras Paralelas": "Parallel Bars",
    "Cajón de Salto": "Plyo Box",
    "TRX": "TRX Suspension Trainer",
    "Bandas de Resistencia": "Resistance Bands",
    "Esterilla/Mat de Yoga": "Yoga Mat",
    "Fitball": "Stability Ball"
}

with open("accounts/fixtures/equipamientos.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    name = item["fields"]["name"]
    if name in translations_equipment:
        item["fields"]["name"] = translations_equipment[name]

# Add missing equipment
missing_eq = [
    {"name": "Hex Bar", "category": "WEIGHTS"},
    {"name": "Medicine Ball", "category": "ACCESSORY"},
    {"name": "Ab Roller", "category": "ACCESSORY"},
    {"name": "Calf Raise Machine", "category": "MACHINE"},
    {"name": "Lat Pulldown Machine", "category": "MACHINE"},
    {"name": "Pec Deck / Fly Machine", "category": "MACHINE"},
    {"name": "Foam Roller", "category": "ACCESSORY"},
    {"name": "Jump Rope", "category": "CARDIO"}
]

max_pk = max([i["pk"] for i in data])
for eq in missing_eq:
    max_pk += 1
    data.append({
        "model": "accounts.equipment",
        "pk": max_pk,
        "fields": eq
    })

with open("accounts/fixtures/equipamientos.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Equipment translated and new ones added!")
