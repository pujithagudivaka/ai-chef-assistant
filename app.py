
import os
import json
import streamlit as st

st.set_page_config(
    page_title="AI Recipe Generator",
    page_icon="🍳",
    layout="wide"
)

# Kitchen-themed design
st.markdown("""
<style>
.stApp {
    background:
        linear-gradient(rgba(255, 249, 238, 0.90),
                        rgba(255, 249, 238, 0.94)),
        url("https://images.unsplash.com/photo-1556911220-e15b29be8c8f");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1450px;
}
h1, h2, h3 {
    color: #245642;
}
.recipe-card {
    background: rgba(255,255,255,0.94);
    border: 1px solid #e5e3d6;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 16px rgba(70,60,30,0.08);
}
.step-card {
    background: #ffffff;
    border-left: 4px solid #39775a;
    border-radius: 8px;
    padding: 12px 15px;
    margin: 8px 0;
}
.stButton > button {
    background: #28664e;
    color: white;
    border-radius: 12px;
    border: none;
    min-height: 45px;
    font-weight: bold;
}
.stButton > button:hover {
    background: #194b38;
    color: white;
}
</style>
""", unsafe_allow_html=True)


def generate_recipe(dish, ingredients, preference, spice,
                    servings, max_time, budget):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None, (
            "AI recipe generation kosam GEMINI_API_KEY set cheyyali. "
            "Setup instructions kinda unnayi."
        )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an experienced Indian cooking chef.

Create a practical recipe for this exact dish: {dish}

Available ingredients: {ingredients}
Food preference: {preference}
Spice level: {spice}
Servings: {servings}
Maximum cooking time: {max_time} minutes
Budget per serving: Rs. {budget}

Requirements:
- Give a recipe specifically for the requested dish.
- Do not replace it with an unrelated generic curry.
- Respect the food preference and available ingredients.
- If an essential ingredient is missing, list it separately.
- Give realistic ingredient quantities for the servings.
- Give 8 to 10 detailed, logically ordered cooking steps.
- Keep the method within the time limit where practical.
- Never invent nutritional or cost guarantees.
- Include cooking tips and approximate cooking time.
- If the dish cannot reasonably meet the preferences or budget,
  explain that honestly.

Return ONLY valid JSON in this format:
{{
  "title": "Dish name",
  "description": "Short dish description",
  "time": "Approximate cooking time",
  "ingredients": [
    {{"name": "Ingredient", "quantity": "Amount"}}
  ],
  "missing_ingredients": ["Ingredient"],
  "steps": ["Step 1", "Step 2"],
  "tips": ["Tip 1", "Tip 2"]
}}
"""

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        result_text = response.text.strip()
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        recipe = json.loads(result_text)

        if not recipe.get("ingredients") or not recipe.get("steps"):
            return None, "AI valid recipe ivvaledu. Malli try cheyyi."

        return recipe, None

    except Exception as e:
        return None, (
            "Recipe generate avvaledu. API key, internet connection, "
            "model access check cheyyi. Details: " + str(e)
        )


# Header
st.markdown("# 🍳 AI Recipe Generator")
st.markdown(
    "### Fresh ingredients + your preferences = your perfect recipe ❤️"
)
st.divider()

left, right = st.columns([1, 2.1], gap="large")

with left:
    st.markdown("## 🥕 Tell us about your recipe")

    with st.form("recipe_form"):
        dish = st.text_input(
            "🍽️ Dish name",
            placeholder="e.g., Chicken Biryani, Dosa, Tomato Soup"
        )

        ingredients = st.text_area(
            "🥬 Ingredients available",
            placeholder="e.g., rice, chicken, onion, spices",
            height=90
        )

        preference = st.selectbox(
            "🥗 Food preference",
            [
                "No special preference",
                "Vegetarian",
                "Vegan",
                "High protein"
            ]
        )

        spice = st.selectbox(
            "🌶️ Spice level",
            ["Mild", "Medium", "Hot"]
        )

        servings = st.number_input(
            "🍴 Number of servings",
            min_value=1,
            max_value=12,
            value=2
        )

        max_time = st.slider(
            "⏱️ Maximum cooking time (minutes)",
            min_value=10,
            max_value=120,
            value=30
        )

        budget = st.number_input(
            "💰 Budget per serving (₹)",
            min_value=50,
            max_value=2000,
            value=200,
            step=50
        )

        submitted = st.form_submit_button(
            "✨ Create Your Recipe",
            type="primary",
            use_container_width=True
        )

with right:
    st.markdown("## 🍲 Your personalized recipe")

    if submitted:
        if not dish.strip():
            st.warning("Munduga dish name enter cheyyi.")
        elif not ingredients.strip():
            st.warning("Available ingredients enter cheyyi.")
        else:
            with st.spinner("👩‍🍳 Preparing your personalized recipe..."):
                recipe, error = generate_recipe(
                    dish, ingredients, preference, spice,
                    servings, max_time, budget
                )

            if error:
                st.error(error)
            else:
                st.session_state["recipe"] = recipe
                st.session_state["recipe_settings"] = {
                    "servings": servings,
                    "preference": preference,
                    "spice": spice,
                    "budget": budget
                }

    recipe = st.session_state.get("recipe")

    if recipe:
        settings = st.session_state["recipe_settings"]

        st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
        st.markdown(f"# 🍽️ {recipe.get('title', dish)}")
        st.write(recipe.get("description", ""))
        st.write(f"⏱️ Approximate time: {recipe.get('time', 'Not specified')}")
        st.write(f"🍴 Servings: {settings['servings']}")
        st.write(f"🥗 Preference: {settings['preference']}")
        st.write(f"🌶️ Spice level: {settings['spice']}")
        st.write(f"💰 Budget per serving: ₹{settings['budget']}")
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🥕 Ingredients & quantities")
            for item in recipe.get("ingredients", []):
                st.write(
                    f"• **{item.get('name', 'Ingredient')}:** "
                    f"{item.get('quantity', 'As needed')}"
                )

            missing = recipe.get("missing_ingredients", [])
            if missing:
                st.markdown("### 🛒 Additional ingredients needed")
                for item in missing:
                    st.write(f"• {item}")

            st.markdown("### 💡 Cooking tips")
            for tip in recipe.get("tips", []):
                st.write(f"• {tip}")

        with col2:
            st.markdown("### 👩‍🍳 Step-by-step cooking method")
            for i, step in enumerate(recipe.get("steps", []), 1):
                st.markdown(
                    f'<div class="step-card"><b>Step {i}:</b> '
                    f'{step}</div>',
                    unsafe_allow_html=True
                )

        download_text = (
            f"{recipe.get('title', dish)}\n\n"
            f"Description: {recipe.get('description', '')}\n"
            f"Cooking time: {recipe.get('time', '')}\n"
            f"Servings: {settings['servings']}\n\n"
            "INGREDIENTS\n"
            + "\n".join(
                f"- {x.get('name', '')}: {x.get('quantity', '')}"
                for x in recipe.get("ingredients", [])
            )
            + "\n\nCOOKING METHOD\n"
            + "\n".join(
                f"{i}. {step}"
                for i, step in enumerate(recipe.get("steps", []), 1)
            )
            + "\n\nCOOKING TIPS\n"
            + "\n".join(f"- {tip}" for tip in recipe.get("tips", []))
        )

        st.download_button(
            "📥 Download Your Recipe",
            data=download_text,
            file_name="my_recipe.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.markdown("""
        <div class="recipe-card">
            <h2>👩‍🍳 Welcome to your kitchen!</h2>
            <p>Enter any dish and your available ingredients.</p>
            <p>Your personalized ingredients, cooking method,
            and tips will appear here.</p>
            <p>🍅 Fresh ingredients. 🥘 Delicious recipes.</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.markdown(
    "<center>🌿 Fresh Ingredients, Better Recipes · Happy Cooking! ❤️</center>",
    unsafe_allow_html=True
)
