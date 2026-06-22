import streamlit as st
import google.generativeai as genai

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="🏋️",
    layout="wide"
)

st.title("🏋️ AI Health & Fitness Planner")
st.write("Generate personalized diet and workout plans using Gemini AI.")

# ---------------- SESSION STATE ---------------- #
if "diet_plan" not in st.session_state:
    st.session_state.diet_plan = ""

if "fitness_plan" not in st.session_state:
    st.session_state.fitness_plan = ""

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("🔑 Gemini API Key")

    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password"
    )

    st.markdown(
        "[Get API Key](https://aistudio.google.com/app/apikey)"
    )

if not api_key:
    st.warning("Please enter your Gemini API key.")
    st.stop()

# ---------------- GEMINI MODEL ---------------- #
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)
except Exception as e:
    st.error(f"Error loading Gemini: {e}")
    st.stop()

# ---------------- USER INPUT ---------------- #
st.header("👤 User Profile")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", 15, 80, 23)
    height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)

    activity = st.selectbox(
        "Activity Level",
        [
            "Sedentary",
            "Lightly Active",
            "Moderately Active",
            "Very Active"
        ]
    )

with col2:
    weight = st.number_input("Weight (kg)", 20.0, 200.0, 70.0)

    gender = st.selectbox(
        "Gender",
        ["Male", "Female"]
    )

    goal = st.selectbox(
        "Goal",
        [
            "Lose Weight",
            "Gain Muscle",
            "Maintain Weight"
        ]
    )

diet_type = st.selectbox(
    "Diet Preference",
    [
        "Vegetarian",
        "Non-Vegetarian"
    ]
)

# ---------------- BMI ---------------- #
height_m = height / 100
bmi = round(weight / (height_m ** 2), 2)

# ---------------- BMR ---------------- #
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_multiplier = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725
}

daily_calories = int(bmr * activity_multiplier[activity])

st.info(f"""
BMI: **{bmi}**

BMR: **{int(bmr)} kcal**

Daily Maintenance Calories: **{daily_calories} kcal**
""")

# ---------------- GENERATE PLAN ---------------- #
if st.button("Generate Plan"):

    profile = f"""
Age: {age}
Weight: {weight} kg
Height: {height} cm
Gender: {gender}
BMI: {bmi}
BMR: {int(bmr)}
Maintenance Calories: {daily_calories}
Activity Level: {activity}
Goal: {goal}
Diet Preference: {diet_type}
"""

    with st.spinner("Generating your plans..."):

        diet_prompt = f"""
Create a healthy one-day meal plan.

Include:
- Breakfast
- Lunch
- Dinner
- Snacks
- Approximate calories

User Details:
{profile}
"""

        fitness_prompt = f"""
Create a fitness routine.

Include:
- Warm-up
- Exercises with sets and reps
- Cool-down

User Details:
{profile}
"""

        try:
            diet_response = model.generate_content(diet_prompt)
            fitness_response = model.generate_content(fitness_prompt)

            st.session_state.diet_plan = diet_response.text
            st.session_state.fitness_plan = fitness_response.text

        except Exception as e:
            st.error(f"Generation Error: {e}")

# ---------------- DISPLAY PLANS ---------------- #
if st.session_state.diet_plan:

    st.header("🥗 Diet Plan")
    st.markdown(st.session_state.diet_plan)

    st.header("💪 Workout Plan")
    st.markdown(st.session_state.fitness_plan)

# ---------------- Q&A SECTION ---------------- #
if st.session_state.diet_plan:

    st.header("❓ Ask Questions")

    question = st.text_input(
        "Ask anything about your generated plans"
    )

    if st.button("Get Answer"):

        context = f"""
Diet Plan:
{st.session_state.diet_plan}

Workout Plan:
{st.session_state.fitness_plan}

User Question:
{question}
"""

        try:
            response = model.generate_content(context)
            st.success(response.text)

        except Exception as e:
            st.error(f"Error: {e}")