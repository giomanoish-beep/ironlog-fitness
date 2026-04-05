# IronLog — Professional Fitness Workout Tracker 🏋️

A fully local, professional-grade fitness app built with Streamlit. Track your lifts, generate periodized training plans, and watch your strength grow over time.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Features

### 💪 Build Muscle Mode
- **Mesocycle periodization**: 4 weeks building + 1 week deload
- **Split options**: Full Body, Push/Pull/Legs, Upper/Lower based on frequency (2–6 sessions/week)
- **Auto weight suggestions**: Increases 2.5% for upper body, 5% for lower body when you hit 8+ reps
- **Exercise catalog**: 73+ exercises with full metadata (muscle group, type, equipment, difficulty)

### 🏃 Cardio Mode
- **Periodized cardio plans**: 6 weeks with Base → Build → Peak phases
- **Types**: Running, Cycling, HIIT, Swimming
- **Session variety**: Different interval styles each session to prevent boredom

### 📊 Progress Tracking
- Strength gains visualized per exercise over time
- Total volume, session count, muscles trained metrics
- Session history with full exercise breakdown

### 📖 Exercise Catalog
- **73 exercises** across all major muscle groups
- Filter by muscle, type, equipment, difficulty
- Add custom exercises, edit or delete existing ones
- Fully searchable

### 📝 Session Logging
- Log weights, reps, sets for each exercise
- See suggested weight based on your history before logging
- Session notes for tracking how you felt

### 🛠️ Settings
- Export/import workout history as JSON
- Clear logs, plans, or full reset
- All data stored locally — no cloud, no paid services

---

## Quick Start

```bash
# 1. Navigate to the app directory
cd ~/projects/fitness-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## File Structure

```
~/projects/fitness-app/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── data/               # Auto-created on first run
    ├── exercises.json  # Exercise catalog
    ├── workouts.json    # Workout history (logs)
    └── plans.json       # Saved training plans
```

---

## How the Weight Suggestion Algorithm Works

```
On each session:
  1. Look up the most recent weight + reps for this exercise
  2. If last session hit 8+ reps:
     - Upper body:   weight × 1.025 (round to nearest 2.5kg)
     - Lower body:   weight × 1.05  (round to nearest 2.5kg)
  3. If last session hit <8 reps:
     - Keep same weight, aim for higher reps
  4. Display: "Last: 80kg × 8 → Today: 82kg × 6-8"
```

---

## Plan Structures

### Build Muscle (by sessions/week)

| Sessions | Split |
|----------|-------|
| 2/week | Full Body × 2 |
| 3/week | Push / Pull / Legs |
| 4/week | Upper / Lower / Upper / Lower |
| 5/week | Push / Pull / Legs / Upper / Lower |
| 6/week | Push / Pull / Legs × 2 |

### Cardio Periodization

| Weeks | Phase | Focus |
|-------|-------|-------|
| 1–2 | Base | Aerobic foundation, low-medium intensity |
| 3–4 | Build | Increase intensity, 10% volume bump |
| 5–6 | Peak | High intensity, hit your best |

---

## Deployment

### Local Network Access
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
Other devices on your network can access via `http://YOUR_IP:8501`

### Cloud Deploy (Free)

**Streamlit Cloud** (free):
1. Push to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo and deploy

**Railway / Render / Fly.io**:
```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

---

## Tech Stack

- **Python 3.9+**
- **Streamlit** — UI framework
- **Local JSON files** — data persistence (no database needed)
- **No external paid APIs** — completely free

---

## Data Location

All data is stored in:
```
~/projects/fitness-app/data/
```

The app auto-creates this directory on first run. No configuration needed.

---

*Built with Streamlit · All data local · No tracking · No ads · No paid features*
