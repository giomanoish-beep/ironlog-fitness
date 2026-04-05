"""
IronLog — Professional Fitness Workout Tracker
Run: streamlit run app.py
"""

import streamlit as st
import json
import os
import random
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path.home() / "projects" / "fitness-app"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

WORKOUTS_FILE = DATA_DIR / "workouts.json"
PLANS_FILE    = DATA_DIR / "plans.json"
EXERCISES_FILE = DATA_DIR / "exercises.json"

# ── Theme ─────────────────────────────────────────────────────────────────────
DARK_CSS = """
<style>
    :root {
        --bg:         #0d0d0d;
        --surface:    #1a1a1a;
        --surface2:   #242424;
        --border:     #333333;
        --accent:     #e63946;
        --accent2:    #f4a261;
        --text:       #f1f1f1;
        --muted:      #888888;
        --green:      #2a9d8f;
        --blue:       #457b9d;
    }
    .stApp { background-color: var(--bg); color: var(--text); }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div,
    .stSlider > div > div > div { background-color: var(--surface2) !important; border-color: var(--border) !important; color: var(--text) !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: var(--surface); border-radius: 8px 8px 0 0; padding: 8px 20px; color: var(--muted); border: none; }
    .stTabs .css-1q8jdt6 { background-color: var(--accent) !important; color: white !important; }
    section[data-testid="stSidebar"] { background-color: var(--surface); border-right: 1px solid var(--border); }
    .stMetric { background-color: var(--surface); padding: 16px; border-radius: 10px; border: 1px solid var(--border); }
    .stAlert { border-radius: 8px; }
    div[data-testid="stExpander"] { background-color: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
    .workout-card { background-color: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 10px; }
    .session-complete { background-color: #1a3a2a; border: 1px solid var(--green); border-radius: 10px; padding: 12px; margin-bottom: 8px; }
    .suggested-weight { background-color: #1a2a3a; border: 1px solid var(--blue); border-radius: 8px; padding: 10px; margin: 4px 0; font-size: 14px; }
    .plan-header { font-size: 22px; font-weight: 700; color: var(--accent); }
    .section-header { font-size: 16px; font-weight: 600; color: var(--accent2); margin-top: 12px; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
    .stDataFrame { background-color: var(--surface); }
    thead th { background-color: var(--surface2) !important; color: var(--text) !important; }
    tbody td { background-color: var(--surface) !important; color: var(--text) !important; }
    .delta-neg { color: #e63946 !important; }
    .delta-pos { color: #2a9d8f !important; }
</style>
"""
st.set_page_config(page_title="IronLog — Workout Tracker", layout="wide", page_icon="🏋️")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_json(path: Path, default=list):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return default()
    return default()

def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def today_str():
    return datetime.date.today().isoformat()

def now_str():
    return datetime.datetime.now().isoformat()

def load_exercises() -> List[Dict]:
    return load_json(EXERCISES_FILE, [])

def load_workouts() -> Dict:
    return load_json(WORKOUTS_FILE, {})

def save_workouts(data: Dict):
    save_json(WORKOUTS_FILE, data)

def load_plans() -> List[Dict]:
    return load_json(PLANS_FILE, [])

def save_plans(data: List[Dict]):
    save_json(PLANS_FILE, data)

def get_last_performance(exercise_name: str, workouts: Dict) -> Optional[Dict]:
    """Get most recent logged weight/reps for an exercise."""
    for log in reversed(workouts.get("logs", [])):
        for ex in log.get("exercises", []):
            if ex.get("name", "").lower() == exercise_name.lower():
                return ex
    return None

def suggest_weight(exercise_name: str, workouts: Dict, is_lower_body: bool = False) -> Dict:
    """
    Weight suggestion logic:
    - Take last session's weight
    - Add 2.5% for upper body, 5% for lower body if last session hit 8+ reps
    """
    last = get_last_performance(exercise_name, workouts)
    if not last:
        return {"weight": None, "reps": "8-10", "note": "No previous data — start light and build up"}

    last_weight = last.get("weight")
    last_reps = last.get("reps", 0)

    if last_weight and last_reps and last_reps >= 8:
        pct = 0.05 if is_lower_body else 0.025
        new_weight = round(last_weight * (1 + pct) / 2.5) * 2.5  # round to nearest 2.5kg
        return {
            "weight": new_weight,
            "reps": f"{max(4, last_reps - 2)}-{last_reps}",
            "note": f"Last: {last_weight}kg × {last_reps} reps → Today: {new_weight}kg × ({max(4, last_reps - 2)}-{last_reps})"
        }
    else:
        return {
            "weight": last_weight,
            "reps": f"{last_reps}-{last_reps + 2}",
            "note": f"Last: {last_weight}kg × {last_reps} reps → Same weight, aim for {last_reps}+ reps"
        }

def is_lower_body(exercise_name: str) -> bool:
    lower_keywords = ["squat", "leg", "lunge", "calf", "hip", "glute", "hamstring", "thrust"]
    return any(k in exercise_name.lower() for k in lower_keywords)

# ── Plan Generators ───────────────────────────────────────────────────────────
def generate_muscle_plan(
    sessions_per_week: int,
    duration_min: int,
    experience: str,
    exercises: List[Dict]
) -> Dict:
    """Generate a multi-month weight training mesocycle plan."""

    def filter_ex(muscle: str, exp: str = None, equip: str = None):
        return [
            e for e in exercises
            if e["muscle"] == muscle
            and (exp is None or e["difficulty"] in ["beginner", exp])
            and (equip is None or e["equipment"] == equip)
        ]

    # Split templates based on sessions/week
    if sessions_per_week == 2:
        # Full body x2
        templates = [
            ["squat", "bench press", "barbell row", "overhead press", "romanian deadlift", "curl", "tricep pushdown"],
            ["squat", "incline dumbbell press", "pull-up", "lat pulldown", "leg press", "lateral raise", "calf raise"],
        ]
    elif sessions_per_week == 3:
        # Push / Pull / Legs
        templates = [
            ["bench press", "incline dumbbell press", "overhead press", "lateral raise", "tricep pushdown", "cable crossover"],
            ["barbell row", "pull-up", "lat pulldown", "seated cable row", "face pull", "barbell curl"],
            ["squat", "romanian deadlift", "leg press", "leg curl", "calf raise", "bulgarian split squat"],
        ]
    elif sessions_per_week == 4:
        # Upper / Lower split
        templates = [
            ["bench press", "barbell row", "overhead press", "lat pulldown", "dumbbell curl", "tricep pushdown"],
            ["squat", "romanian deadlift", "leg press", "leg curl", "calf raise", "hip thrust"],
            ["incline dumbbell press", "pull-up", "lateral raise", "seated cable row", "hammer curl", "skull crusher"],
            ["deadlift", "walking lunge", "leg extension", "good morning", "upright row", "plank"],
        ]
    elif sessions_per_week == 5:
        # Push / Pull / Legs / Upper / Lower
        templates = [
            ["bench press", "incline dumbbell press", "overhead press", "lateral raise", "tricep pushdown"],
            ["barbell row", "pull-up", "lat pulldown", "face pull", "barbell curl", "cable curl"],
            ["squat", "romanian deadlift", "leg press", "leg curl", "calf raise", "hip thrust"],
            ["incline dumbbell press", "dumbbell row", "arnold press", "seated cable row", "concentration curl", "overhead tricep extension"],
            ["deadlift", "bulgarian split squat", "leg extension", "good morning", "upright row", "hanging leg raise"],
        ]
    else:
        # 6 days: Push/Pull/Legs x2
        templates = [
            ["bench press", "incline dumbbell press", "overhead press", "lateral raise", "tricep dip", "cable crossover"],
            ["barbell row", "pull-up", "lat pulldown", "face pull", "barbell curl", "preacher curl"],
            ["squat", "romanian deadlift", "leg press", "leg curl", "calf raise", "bulgarian split squat"],
            ["incline dumbbell press", "dumbbell flyes", "arnold press", "front raise", "skull crusher", "tricep pushdown"],
            ["barbell row", "chin-up", "lat pulldown", "seated cable row", "hammer curl", "cable curl"],
            ["squat", "hip thrust", "leg extension", "romanian deadlift", "good morning", "plank"],
        ]

    # Build the plan
    plan = []
    weeks = 5  # 4 weeks building + 1 deload
    day_names = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6"]

    # Sets/reps based on experience
    rep_ranges = {
        "beginner":    {"sets": 3, "reps": "10-12", "rest": "90s"},
        "intermediate": {"sets": 4, "reps": "6-8",   "rest": "120s"},
        "advanced":    {"sets": 4, "reps": "4-6",    "rest": "180s"},
    }
    base = rep_ranges[experience]

    for week in range(1, weeks + 1):
        is_deload = (week == 5)
        week_label = f"Week {week} — {'Deload 🏖️' if is_deload else ('Week ' + str(week) + ' of 4 — Building 💪')}"
        week_data = {
            "week": week,
            "label": week_label,
            "is_deload": is_deload,
            "sessions": []
        }

        for day_idx in range(min(sessions_per_week, len(templates))):
            template = templates[day_idx]
            day_name = day_names[day_idx]
            session = {
                "day": day_name,
                "week": week,
                "is_deload": is_deload,
                "exercises": []
            }

            for ex_name in template:
                # Find matching exercise from catalog
                matched = next(
                    (e for e in exercises if e["name"].lower() == ex_name.lower()),
                    None
                )
                if not matched:
                    continue

                sets = base["sets"] if not is_deload else max(2, base["sets"] - 1)
                reps = base["reps"] if not is_deload else f"{int(base['reps'].split('-')[0]) + 4}-{int(base['reps'].split('-')[1]) + 4}"

                session["exercises"].append({
                    "name": matched["name"],
                    "sets": sets,
                    "reps": reps,
                    "rest": base["rest"] if not is_deload else "60s",
                    "equipment": matched["equipment"],
                    "muscle": matched["muscle"],
                    "type": matched["type"],
                    "progression_note": _progression_note(week, experience, is_deload)
                })

            week_data["sessions"].append(session)
        plan.append(week_data)

    return plan

def _progression_note(week: int, exp: str, is_deload: bool) -> str:
    if is_deload:
        return "Deload — reduce weight by ~40%, focus on form"
    if exp == "beginner":
        return "Focus on perfect form. Add weight when you hit 12 reps easily."
    elif exp == "intermediate":
        return "Progressive overload: add 2.5kg when top of rep range hit easily."
    else:
        return "Hit all sets of 6. Add 2.5kg upper / 5kg lower each week."


def generate_cardio_plan(
    sessions_per_week: int,
    duration_min: int,
    cardio_type: str,
    experience: str
) -> Dict:
    """Generate a periodized cardio plan."""

    plan = []
    weeks = 6
    types_map = {
        "running": {"primary": "Running", "intervals": ["Easy pace", "Tempo run", "Long run", "Fartlek"]},
        "cycling": {"primary": "Cycling", "intervals": ["Steady state", "Tempo", "Endurance ride", "Sprint intervals"]},
        "HIIT": {"primary": "HIIT", "intervals": ["Tabata 20/10", "30-30s", "Pyramid", "EMOM"]},
        "swimming": {"primary": "Swimming", "intervals": ["Easy laps", "Technique focus", "Distance", "Sprint sets"]},
    }
    config = types_map.get(cardio_type, types_map["running"])

    for week in range(1, weeks + 1):
        # Periodization
        if week <= 2:
            phase = "Base — Build aerobic foundation"
            vol_factor = 1.0
            intensity = "Low-Med (65-75% HR max)"
        elif week <= 4:
            phase = "Build — Increase intensity"
            vol_factor = 1.1
            intensity = "Medium (75-85% HR max)"
        else:
            phase = "Peak — Hit your best"
            vol_factor = 1.2
            intensity = "High (85-95% HR max)"

        adjusted_dur = int(duration_min * vol_factor)
        session_dur = min(adjusted_dur, 90)

        week_data = {
            "week": week,
            "phase": phase,
            "intensity": intensity,
            "sessions": []
        }

        # Generate varied sessions
        interval_options = config["intervals"]
        for day_idx in range(sessions_per_week):
            interval_type = interval_options[day_idx % len(interval_options)]
            session = {
                "day": f"Session {day_idx + 1}",
                "week": week,
                "type": cardio_type,
                "activity": config["primary"],
                "interval": interval_type,
                "duration": session_dur,
                "intensity": intensity,
                "warmup": 5,
                "cooldown": 5,
                "notes": _cardio_notes(cardio_type, interval_type, experience)
            }
            week_data["sessions"].append(session)

        plan.append(week_data)

    return plan

def _cardio_notes(cardio_type: str, interval: str, exp: str) -> str:
    notes = {
        "running": {
            "Easy pace": " conversational — you can hold a full sentence",
            "Tempo run": " comfortably hard — just below threshold",
            "Long run": " slow and steady — build endurance",
            "Fartlek": " mix of fast/slow — play with speed freely",
        },
        "cycling": {
            "Steady state": " maintain consistent moderate cadence (80-90 RPM)",
            "Tempo": " challenging but sustainable effort",
            "Endurance ride": " low resistance, high duration",
            "Sprint intervals": " max effort 30s, full recovery 2min",
        },
        "HIIT": {
            "Tabata 20/10": " 20s all-out, 10s rest × 8 rounds",
            "30-30s": " 30s max effort, 30s rest × 10 rounds",
            "Pyramid": " 15s-30s-45s-45s-30s-15s work intervals",
            "EMOM": " Every minute on the minute — new challenge each round",
        },
        "swimming": {
            "Easy laps": " focus on breathing and stroke technique",
            "Technique focus": " drills: catch-up, fingertip drag, single arm",
            "Distance": " build yardage steadily",
            "Sprint sets": " fast 25s/50s with full recovery",
        },
    }
    base = notes.get(cardio_type, {}).get(interval, "")
    exp_tip = f" ({exp} modifier: adjust work:rest ratio accordingly)" if exp != "beginner" else ""
    return f"{interval}{base}{exp_tip}"


# ── Session State ─────────────────────────────────────────────────────────────
if "current_plan" not in st.session_state:
    st.session_state["current_plan"] = None
if "plan_type" not in st.session_state:
    st.session_state["plan_type"] = None
if "log_saved" not in st.session_state:
    st.session_state["log_saved"] = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏋️ **IronLog**")
    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        ["📋 Workout Plan", "📖 Exercise Catalog", "📊 Progress", "📝 Log Workout", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Data stored locally at")
    st.code(str(DATA_DIR), language="bash")

# ── Page: Workout Plan ────────────────────────────────────────────────────────
if page == "📋 Workout Plan":
    st.markdown("# 📋 Workout Plan")
    st.markdown("Build your personalized training plan")

    col_a, col_b = st.columns(2)
    with col_a:
        plan_type = st.selectbox("**Plan Type**", ["Build Muscle 💪", "Do Cardio 🏃"])
    with col_b:
        if st.button("**+ New Plan**", use_container_width=True):
            st.session_state["log_saved"] = False

    st.markdown("---")

    if plan_type == "Build Muscle 💪":
        st.session_state["plan_type"] = "muscle"
        with st.expander("⚙️ Configure Your Plan", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                sessions = st.slider("Sessions / week", 2, 6, 4)
                duration = st.slider("Duration (min)", 45, 90, 60)
            with c2:
                experience = st.selectbox("Experience", ["beginner", "intermediate", "advanced"])
            with c3:
                st.markdown("")
                if st.button("🚀 Generate Plan", use_container_width=True):
                    exercises = load_exercises()
                    plan = generate_muscle_plan(sessions, duration, experience, exercises)
                    plan_wrapper = {
                        "type": "muscle",
                        "sessions_per_week": sessions,
                        "duration": duration,
                        "experience": experience,
                        "created": now_str(),
                        "weeks": plan
                    }
                    save_plans([plan_wrapper])
                    st.session_state["current_plan"] = plan_wrapper
                    st.rerun()

        # Show plan
        plans = load_plans()
        if plans:
            st.session_state["current_plan"] = plans[-1]

        plan = st.session_state.get("current_plan")
        if plan and plan.get("type") == "muscle":
            exercises = load_exercises()
            st.success(f"Active plan — {plan['sessions_per_week']} sessions/week, {plan['experience']}")
            st.markdown("---")

            # Mesocycle tabs
            weeks = plan.get("weeks", [])
            week_tabs = st.tabs([w["label"] for w in weeks])

            for tab_idx, week_tab in enumerate(week_tabs):
                with week_tab:
                    wdata = weeks[tab_idx]
                    st.markdown(f"**{wdata['label']}**" + (" — *Deload week*" if wdata.get("is_deload") else ""))
                    for sess in wdata.get("sessions", []):
                        with st.expander(f"📅 **{sess['day']}**" + (" 🏖️" if sess.get("is_deload") else " 💪"), expanded=False):
                            for ex in sess.get("exercises", []):
                                is_lower = is_lower_body(ex["name"])
                                workouts = load_workouts()
                                suggestion = suggest_weight(ex["name"], workouts, is_lower)

                                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 2])
                                with col1:
                                    st.markdown(f"**{ex['name']}**")
                                    st.caption(f"_{ex['muscle']}_ · {ex['equipment']}")
                                with col2:
                                    st.metric("Sets", ex["sets"])
                                with col3:
                                    st.metric("Reps", ex["reps"])
                                with col4:
                                    st.metric("Rest", ex["rest"])
                                with col5:
                                    if suggestion.get("weight"):
                                        st.markdown(f"<div class='suggested-weight'>⚖️ Suggested: **{suggestion['weight']}kg** × {suggestion['reps']}</div>", unsafe_allow_html=True)
                                    else:
                                        st.info("⚖️ " + suggestion.get("note", "No data yet"))
                            st.caption(f"Progression: {sess['exercises'][0]['progression_note'] if sess['exercises'] else ''}")
        else:
            st.info("Configure and generate a plan above to get started.")

    else:  # Cardio
        st.session_state["plan_type"] = "cardio"
        with st.expander("⚙️ Configure Your Cardio Plan", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                sessions = st.slider("Sessions / week", 1, 6, 3)
                duration = st.slider("Duration (min)", 15, 90, 30)
            with c2:
                cardio_type = st.selectbox("Cardio Type", ["running", "cycling", "HIIT", "swimming"])
            with c3:
                exp_cardio = st.selectbox("Experience", ["beginner", "intermediate", "advanced"])
                st.markdown("")
                if st.button("🚀 Generate Cardio Plan", use_container_width=True):
                    plan = generate_cardio_plan(sessions, duration, cardio_type, exp_cardio)
                    plan_wrapper = {
                        "type": "cardio",
                        "sessions_per_week": sessions,
                        "duration": duration,
                        "cardio_type": cardio_type,
                        "experience": exp_cardio,
                        "created": now_str(),
                        "weeks": plan
                    }
                    save_plans([plan_wrapper])
                    st.session_state["current_plan"] = plan_wrapper
                    st.rerun()

        plans = load_plans()
        if plans:
            st.session_state["current_plan"] = plans[-1]

        plan = st.session_state.get("current_plan")
        if plan and plan.get("type") == "cardio":
            st.success(f"Cardio Plan — {plan['sessions_per_week']} sessions/week of {plan['cardio_type']}")
            st.markdown("---")
            weeks = plan.get("weeks", [])
            week_tabs = st.tabs([f"Week {w['week']} — {w['phase']}" for w in weeks])

            for tab_idx, week_tab in enumerate(week_tabs):
                with week_tab:
                    wdata = weeks[tab_idx]
                    st.markdown(f"**Phase:** {wdata['phase']} | **Intensity:** {wdata['intensity']}")
                    for sess in wdata.get("sessions", []):
                        with st.expander(f"🏃 **{sess['day']}** — {sess['activity']} ({sess['duration']}min)", expanded=False):
                            c1, c2, c3, c4 = st.columns(4)
                            with c1:
                                st.metric("Duration", f"{sess['duration']}min")
                            with c2:
                                st.metric("Warmup", f"{sess['warmup']}min")
                            with c3:
                                st.metric("Cooldown", f"{sess['cooldown']}min")
                            with c4:
                                st.metric("Intensity", sess["intensity"])
                            st.markdown(f"**Interval:** {sess['interval']}")
                            st.info(f"💡 {sess['notes']}")
        else:
            st.info("Configure and generate a cardio plan above.")

# ── Page: Exercise Catalog ───────────────────────────────────────────────────
elif page == "📖 Exercise Catalog":
    st.markdown("# 📖 Exercise Catalog")
    st.markdown("Browse and manage your exercise library")
    st.markdown(f"**{len(load_exercises())} exercises** available")
    st.markdown("---")

    exercises = load_exercises()
    cat_cols = st.columns(4)
    muscles = ["all"] + sorted(set(e["muscle"] for e in exercises))
    types   = ["all"] + sorted(set(e["type"] for e in exercises))
    equips  = ["all"] + sorted(set(e["equipment"] for e in exercises))

    with cat_cols[0]:
        sel_muscle = st.selectbox("Muscle group", muscles)
    with cat_cols[1]:
        sel_type = st.selectbox("Type", types)
    with cat_cols[2]:
        sel_equip = st.selectbox("Equipment", equips)
    with cat_cols[3]:
        sel_diff = st.selectbox("Difficulty", ["all", "beginner", "intermediate", "advanced"])

    filtered = [
        e for e in exercises
        if (sel_muscle == "all" or e["muscle"] == sel_muscle)
        and (sel_type == "all" or e["type"] == sel_type)
        and (sel_equip == "all" or e["equipment"] == sel_equip)
        and (sel_diff == "all" or e["difficulty"] == sel_diff)
    ]

    st.markdown(f"**Showing {len(filtered)} exercises**")
    st.markdown("---")

    # Group by muscle
    groups = {}
    for ex in filtered:
        grp = ex["muscle"]
        groups.setdefault(grp, []).append(ex)

    for muscle, exs in sorted(groups.items()):
        with st.expander(f"**{muscle.upper()}** ({len(exs)} exercises)", expanded=True):
            for ex in exs:
                type_emoji = {"compound": "🏋️", "isolation": "🎯", "cardio": "🏃", "HIIT": "⚡"}.get(ex["type"], "•")
                diff_color = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}.get(ex["difficulty"], "•")
                equip_color = {"barbell": "🔶", "dumbbell": "⚪", "machine": "⚙️", "bodyweight": "🧍", "cable": "🔗", "kettlebell": "🔵", "other": "🟣", "none": "—", "bike": "🚴", "pool": "🏊"}.get(ex["equipment"], "•")
                st.markdown(
                    f"{type_emoji} **{ex['name']}**  {diff_color} {ex['difficulty']}  {equip_color} {ex['equipment']}\n"
                    f"&nbsp;&nbsp;&nbsp;&nbsp;Reps: {ex['reps_min']}-{ex['reps_max']} · Primary: {ex.get('primary', ex['muscle'])}",
                    unsafe_allow_html=False
                )

    # Add custom exercise
    st.markdown("---")
    with st.expander("➕ Add Custom Exercise", expanded=False):
        st.markdown("**Add a new exercise to your catalog**")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            new_name = st.text_input("Exercise name")
            new_muscle = st.selectbox("Muscle group", ["chest","back","shoulders","biceps","triceps","legs","core","cardio"])
        with ac2:
            new_type = st.selectbox("Type", ["compound","isolation","cardio","HIIT"])
            new_diff = st.selectbox("Difficulty", ["beginner","intermediate","advanced"])
        with ac3:
            new_equip = st.selectbox("Equipment", ["barbell","dumbbell","machine","cable","bodyweight","kettlebell","other","none"])
            new_reps_min = st.number_input("Min reps", 1, 100, 8)
            new_reps_max = st.number_input("Max reps", 1, 100, 12)

        if st.button("Add Exercise"):
            exercises = load_exercises()
            new_id = max([e["id"] for e in exercises], default=0) + 1
            new_ex = {
                "id": new_id,
                "name": new_name,
                "muscle": new_muscle,
                "type": new_type,
                "difficulty": new_diff,
                "equipment": new_equip,
                "reps_min": new_reps_min,
                "reps_max": new_reps_max,
                "primary": new_muscle
            }
            exercises.append(new_ex)
            save_json(EXERCISES_FILE, {"exercises": exercises})
            st.success(f"Added '{new_name}' to catalog!")
            st.rerun()

    # Edit/delete exercises
    st.markdown("---")
    with st.expander("✏️ Edit / Remove Exercises", expanded=False):
        exercises = load_exercises()
        for ex in exercises:
            with st.expander(f"✏️ {ex['name']}"):
                c1, c2 = st.columns(2)
                with c1:
                    en = st.text_input("Name", ex["name"], key=f"en_{ex['id']}")
                    em = st.selectbox("Muscle", ["chest","back","shoulders","biceps","triceps","legs","core","cardio"],
                                      index=["chest","back","shoulders","biceps","triceps","legs","core","cardio"].index(ex["muscle"]) if ex["muscle"] in ["chest","back","shoulders","biceps","triceps","legs","core","cardio"] else 0,
                                      key=f"em_{ex['id']}")
                    et = st.selectbox("Type", ["compound","isolation","cardio","HIIT"],
                                      index=["compound","isolation","cardio","HIIT"].index(ex["type"]) if ex["type"] in ["compound","isolation","cardio","HIIT"] else 0,
                                      key=f"et_{ex['id']}")
                with c2:
                    ed = st.selectbox("Difficulty", ["beginner","intermediate","advanced"],
                                      index=["beginner","intermediate","advanced"].index(ex["difficulty"]) if ex["difficulty"] in ["beginner","intermediate","advanced"] else 0,
                                      key=f"ed_{ex['id']}")
                    ee = st.selectbox("Equipment", ["barbell","dumbbell","machine","cable","bodyweight","kettlebell","other","none","bike","pool"],
                                      index=["barbell","dumbbell","machine","cable","bodyweight","kettlebell","other","none","bike","pool"].index(ex["equipment"]) if ex["equipment"] in ["barbell","dumbbell","machine","cable","bodyweight","kettlebell","other","none","bike","pool"] else 0,
                                      key=f"ee_{ex['id']}")
                    erm = st.number_input("Reps min", 1, 100, ex["reps_min"], key=f"erm_{ex['id']}")
                    eRx = st.number_input("Reps max", 1, 100, ex["reps_max"], key=f"eRx_{ex['id']}")
                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button(f"💾 Save Changes", key=f"es_{ex['id']}"):
                        exercises = [e for e in exercises if e["id"] != ex["id"]]
                        exercises.append({
                            "id": ex["id"], "name": en, "muscle": em, "type": et,
                            "difficulty": ed, "equipment": ee, "reps_min": erm,
                            "reps_max": eRx, "primary": em
                        })
                        save_json(EXERCISES_FILE, {"exercises": exercises})
                        st.success("Saved!")
                        st.rerun()
                with cb2:
                    if st.button(f"🗑️ Delete", key=f"edel_{ex['id']}"):
                        exercises = [e for e in exercises if e["id"] != ex["id"]]
                        save_json(EXERCISES_FILE, {"exercises": exercises})
                        st.warning("Deleted!")
                        st.rerun()

# ── Page: Progress ────────────────────────────────────────────────────────────
elif page == "📊 Progress":
    st.markdown("# 📊 Progress")
    workouts = load_workouts()
    logs = workouts.get("logs", [])

    if not logs:
        st.info("No workouts logged yet. Go to 'Log Workout' to record your first session.")
    else:
        # Summary metrics
        total_sessions = len(logs)
        total_volume = sum(
            sum(ex.get("weight", 0) * ex.get("reps", 0) for ex in log.get("exercises", []))
            for log in logs
        )
        muscles_hit = set()
        for log in logs:
            for ex in log.get("exercises", []):
                muscles_hit.add(ex.get("muscle", "unknown"))
        active_weeks = len(set(log.get("date", "")[:7] for log in logs))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sessions", total_sessions)
        m2.metric("Total Volume", f"{total_volume:,} kg")
        m3.metric("Muscles Trained", len(muscles_hit))
        m4.metric("Active Weeks", active_weeks)

        st.markdown("---")

        # Per-exercise progress
        st.markdown("### 📈 Strength Gains by Exercise")
        exercise_history: Dict[str, List] = {}
        for log in reversed(logs):
            for ex in log.get("exercises", []):
                name = ex.get("name", "Unknown")
                if name not in exercise_history:
                    exercise_history[name] = []
                exercise_history[name].append({
                    "date": log.get("date", ""),
                    "weight": ex.get("weight"),
                    "reps": ex.get("reps"),
                    "sets": ex.get("sets")
                })

        for ex_name, history in sorted(exercise_history.items()):
            if len(history) < 2:
                continue
            entries = list(reversed(history[-6:]))  # last 6 sessions
            weights = [e["weight"] for e in entries if e["weight"]]
            if not weights or len(weights) < 2:
                continue

            delta = round(weights[-1] - weights[0], 1)
            delta_str = f"+{delta}" if delta > 0 else str(delta)
            improvement = round((weights[-1] - weights[0]) / weights[0] * 100, 1) if weights[0] else 0

            with st.expander(f"**{ex_name}** — {delta_str}kg ({improvement}%) over {len(entries)} sessions", expanded=False):
                chart_data = {
                    "Session": list(range(1, len(entries)+1)),
                    "Weight (kg)": [w for w in weights],
                }
                st.line_chart(chart_data, x="Session", y="Weight (kg)")
                # Show history table
                for e in entries:
                    st.write(f"  `{e['date']}` — **{e['weight']}kg** × {e['reps']} reps ({e['sets']} sets)")

        st.markdown("### 🗓️ Recent Sessions")
        recent = logs[-10:]
        for log in reversed(recent):
            date = log.get("date", "?")
            ex_count = len(log.get("exercises", []))
            session_type = log.get("session_type", "strength")
            with st.expander(f"📅 **{date}** — {ex_count} exercises · {session_type}", expanded=False):
                for ex in log.get("exercises", []):
                    st.write(f"  • **{ex.get('name','?')}** — {ex.get('weight','?')}kg × {ex.get('reps','?')} reps ({ex.get('sets','?')} sets)")
                if log.get("notes"):
                    st.caption(f"Notes: {log['notes']}")

# ── Page: Log Workout ─────────────────────────────────────────────────────────
elif page == "📝 Log Workout":
    st.markdown("# 📝 Log Workout")
    st.markdown("Record your completed session")

    log_type = st.radio("Workout type", ["💪 Strength", "🏃 Cardio"], horizontal=True, label_visibility="collapsed")

    if log_type == "💪 Strength":
        exercises = load_exercises()
        strength_exs = [e for e in exercises if e["muscle"] not in ["cardio"]]
        exercise_names = [e["name"] for e in strength_exs]

        # Session meta
        session_date = st.date_input("Session date", datetime.date.today())
        st.markdown("**Add Exercises**")

        if "log_entries" not in st.session_state:
            st.session_state["log_entries"] = []

        entry_key = 0
        to_remove = None

        for idx, entry in enumerate(list(st.session_state["log_entries"])):
            with st.container():
                st.markdown(f"---")
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    sel = st.selectbox(
                        "Exercise",
                        options=[""] + exercise_names,
                        index=(exercise_names.index(entry["name"]) + 1) if entry["name"] in exercise_names else 0,
                        key=f"lex_{idx}",
                        label_visibility="collapsed"
                    )
                    if sel:
                        st.session_state["log_entries"][idx]["name"] = sel
                with col2:
                    weight = st.number_input("Weight (kg)", 0.0, 500.0, entry.get("weight", 0.0), 2.5, key=f"lwt_{idx}")
                    st.session_state["log_entries"][idx]["weight"] = weight
                with col3:
                    reps = st.number_input("Reps", 1, 100, entry.get("reps", 8), key=f"lreps_{idx}")
                    st.session_state["log_entries"][idx]["reps"] = reps
                with col4:
                    sets = st.number_input("Sets", 1, 20, entry.get("sets", 3), key=f"lset_{idx}")
                    st.session_state["log_entries"][idx]["sets"] = sets

                matched = next((e for e in strength_exs if e["name"] == entry["name"]), None)
                if matched:
                    lower = is_lower_body(entry["name"])
                    workouts = load_workouts()
                    suggestion = suggest_weight(entry["name"], workouts, lower)
                    if suggestion.get("weight"):
                        st.markdown(f"<div class='suggested-weight'>⚖️ {suggestion.get('note', '')}</div>", unsafe_allow_html=True)
                    else:
                        st.caption("⚖️ No previous data for this exercise")

                if st.button(f"❌ Remove", key=f"lrem_{idx}"):
                    to_remove = idx

        if to_remove is not None:
            st.session_state["log_entries"].pop(to_remove)
            st.rerun()

        if st.button("➕ Add Exercise"):
            st.session_state["log_entries"].append({"name": "", "weight": 0.0, "reps": 8, "sets": 3})
            st.rerun()

        st.markdown("---")
        notes = st.text_area("Session notes (optional)", placeholder="Felt strong today, moved up on bench...")

        if st.button("✅ Complete Session", use_container_width=True):
            valid_entries = [e for e in st.session_state["log_entries"] if e.get("name")]
            if not valid_entries:
                st.error("Add at least one exercise before completing the session.")
            else:
                workout_log = {
                    "date": session_date.isoformat(),
                    "timestamp": now_str(),
                    "session_type": "strength",
                    "exercises": valid_entries,
                    "notes": notes,
                    "completed": True
                }
                workouts = load_workouts()
                workouts.setdefault("logs", []).append(workout_log)
                save_workouts(workouts)
                st.session_state["log_entries"] = []
                st.session_state["log_saved"] = True
                st.success(f"✅ Session saved! {len(valid_entries)} exercises logged.")

        if st.session_state.get("log_saved"):
            st.balloons()

    else:  # Cardio log
        cardio_types = ["running", "cycling", "HIIT", "swimming", "rowing", "jump rope"]
        ct = st.selectbox("Activity type", cardio_types)
        session_date = st.date_input("Session date", datetime.date.today())
        dur = st.number_input("Duration (minutes)", 5, 180, 30)
        dist = st.number_input("Distance (km) — optional", 0.0, 100.0, 0.0, 0.5)
        hr = st.number_input("Avg heart rate (bpm) — optional", 60, 220, 140)
        notes = st.text_area("Session notes")

        if st.button("✅ Log Cardio Session", use_container_width=True):
            workout_log = {
                "date": session_date.isoformat(),
                "timestamp": now_str(),
                "session_type": "cardio",
                "activity": ct,
                "duration": dur,
                "distance": dist,
                "heart_rate": hr,
                "notes": notes,
                "completed": True
            }
            workouts = load_workouts()
            workouts.setdefault("logs", []).append(workout_log)
            save_workouts(workouts)
            st.success(f"✅ Cardio session logged! {dur}min of {ct}")
            st.balloons()

# ── Page: Settings ────────────────────────────────────────────────────────────
elif page == "⚙️ Settings":
    st.markdown("# ⚙️ Settings")
    st.markdown("---")

    st.markdown("### 📂 Data Management")
    ws1, ws2 = st.columns(2)
    with ws1:
        if st.button("📥 Export Workout History", use_container_width=True):
            workouts = load_workouts()
            st.download_button(
                label="Download workouts.json",
                data=json.dumps(workouts, indent=2),
                file_name="ironlog_workouts.json",
                mime="application/json",
                use_container_width=True
            )
    with ws2:
        if st.button("📤 Import Workout History", use_container_width=True):
            uploaded = st.file_uploader("Upload workouts.json", type="json")
            if uploaded:
                data = json.load(uploaded)
                save_workouts(data)
                st.success("Workout history imported!")

    st.markdown("---")
    st.markdown("### 🗑️ Danger Zone")

    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        if st.button("🗑️ Clear Workout Logs"):
            save_workouts({"logs": []})
            st.warning("Workout logs cleared.")
    with dc2:
        if st.button("🗑️ Clear All Plans"):
            save_plans([])
            st.warning("Plans cleared.")
    with dc3:
        if st.button("💣 Reset Everything"):
            save_workouts({"logs": []})
            save_plans([])
            save_json(EXERCISES_FILE, {"exercises": []})
            st.warning("Everything reset!")

    st.markdown("---")
    st.markdown("### ℹ️ About IronLog")
    st.markdown("""
    **IronLog** — Professional Fitness Workout Tracker
    - Built with Streamlit
    - Data stored locally in `~/projects/fitness-app/data/`
    - No external paid services
    - Weight suggestion: +2.5% upper body / +5% lower body when hitting 8+ reps
    - Mesocycle: 4 weeks building + 1 week deload
    """)

    # Quick stats
    workouts = load_workouts()
    logs = workouts.get("logs", [])
    st.markdown(f"**Sessions logged:** {len(logs)}")
    if logs:
        st.markdown(f"**First session:** {logs[0].get('date','?')}")
        st.markdown(f"**Last session:** {logs[-1].get('date','?')}")

print("IronLog loaded successfully!")
