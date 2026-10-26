import json
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Recipe Generator",
    page_icon="🍳",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

# Kitchen-themed design
st.markdown("""
<style>
.stApp {
    background:
        linear-gradient(rgba(255,249,238,0.90),
                        rgba(255,249,238,0.94)),
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
.stButton > button,
.stFormSubmitButton > button {
    background: #28664e;
    color: white;
    border-radius: 12px;
    border: none;
    min-height: 45px;
    font-weight: bold;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #194b38;
    color: white;
}
</style>
""", unsafe_allow_html=True)


def generate_recipe(
    dish, ingredients, preference, spice,
    servings, max_time, budget
):
    prompt = f"""
You are an experienced Indian cooking chef.

Create a practical recipe for this exact dish: {dish}

Available ingredients: {ingredients}
Food preference: {preference}
Spice level: {spice}
Number of servings: {servings}
Maximum cooking time: {max_time} minutes
Budget per serving: Rs. {budget}

Instructions:
- Make the requested dish, not an unrelated recipe.
- Respect the food preference and listed ingredients.
- Never include meat or eggs in a vegetarian or vegan recipe.
- List essential missing ingredients separately.
- Give realistic ingredient quantities for the servings.
- Provide 8 detailed, logically ordered cooking steps.
- Include useful cooking tips and approximate cooking time.
- Be honest if the requested time or budget is unrealistic.
- Return ONLY valid JSON. Do not use Markdown fences.

Use exactly this JSON structure:
{{
  "title": "Dish name",
  "description": "Short description",
  "time": "Approximate cooking time",
  "ingredients": [
    {{"name": "Ingredient", "quantity": "Amount"}}
  ],
  "missing_ingredients": ["Ingredient"],
  "steps": ["Step 1", "Step 2"],
  "tips": ["Tip 1", "Tip 2"]
}}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.3
                }
            },
            timeout=(10, 300)
        )

        response.raise_for_status()
        data = response.json()
        result_text = data.get("response", "").strip()

        if not result_text:
            return None, "AI nunchi response raledu. Malli try cheyyi."

        recipe = json.loads(result_text)

        if not isinstance(recipe, dict):
            return None, "Recipe response format correct ga ledu."

        if not recipe.get("ingredients") or not recipe.get("steps"):
            return None, "Complete recipe raledu. Malli try cheyyi."

        return recipe, None

    except requests.exceptions.ConnectionError:
        return None, (
            "Ollama connect avvaledu. Ollama install chesi, "
            "run avuthundo check cheyyi. Tarvatha malli try cheyyi."
        )
    except requests.exceptions.Timeout:
        return None, (
            "Recipe generate avvadaniki ekkuva time pattindi. "
            "Konchem sepu tarvatha malli try cheyyi."
        )
    except requests.exceptions.HTTPError as e:
        return None, (
            f"Ollama HTTP error: {e}. Model name and Ollama status check cheyyi."
        )
    except (json.JSONDecodeError, ValueError):
        return None, "AI valid JSON recipe ivvaledu. Malli try cheyyi."
    except Exception as e:
        return None, f"Recipe generation error: {e}"


# Header
st.markdown("# 🍳 AI Recipe Generator")
st.markdown(
    "### Fresh ingredients + your preferences = your perfect recipe ❤️"
)
st.caption("Powered by Ollama local AI")
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
            with st.spinner(
                "👩‍🍳 AI chef is preparing your recipe..."
            ):
                recipe, error = generate_recipe(
                    dish.strip(),
                    ingredients.strip(),
                    preference,
                    spice,
                    int(servings),
                    max_time,
                    int(budget)
                )

            if error:
                st.error(error)
            else:
                st.session_state["recipe"] = recipe
                st.session_state["recipe_settings"] = {
                    "servings": int(servings),
                    "preference": preference,
                    "spice": spice,
                    "budget": int(budget)
                }

    recipe = st.session_state.get("recipe")
    settings = st.session_state.get("recipe_settings", {})

    if recipe and settings:
        st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
        st.markdown(f"# 🍽️ {recipe.get('title', 'Your Recipe')}")
        st.write(recipe.get("description", ""))
        st.write(
            f"⏱️ Approximate time: "
            f"{recipe.get('time', 'Not specified')}"
        )
        st.write(f"🍴 Servings: {settings['servings']}")
        st.write(f"🥗 Preference: {settings['preference']}")
        st.write(f"🌶️ Spice level: {settings['spice']}")
        st.write(f"💰 Budget per serving: ₹{settings['budget']}")
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🥕 Ingredients & quantities")

            for item in recipe.get("ingredients", []):
                if isinstance(item, dict):
                    st.write(
                        f"• **{item.get('name', 'Ingredient')}:** "
                        f"{item.get('quantity', 'As needed')}"
                    )
                else:
                    st.write(f"• {item}")

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
            f"{recipe.get('title', 'Recipe')}\n\n"
            f"Description: {recipe.get('description', '')}\n"
            f"Cooking time: {recipe.get('time', '')}\n"
            f"Servings: {settings['servings']}\n\n"
            "INGREDIENTS\n"
            + "\n".join(
                f"- {x.get('name', '')}: {x.get('quantity', '')}"
                if isinstance(x, dict) else f"- {x}"
                for x in recipe.get("ingredients", [])
            )
            + "\n\nMISSING INGREDIENTS\n"
            + "\n".join(
                f"- {x}" for x in recipe.get("missing_ingredients", [])
            )
            + "\n\nCOOKING METHOD\n"
            + "\n".join(
                f"{i}. {step}"
                for i, step in enumerate(recipe.get("steps", []), 1)
            )
            + "\n\nCOOKING TIPS\n"
            + "\n".join(
                f"- {tip}" for tip in recipe.get("tips", [])
            )
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
    "<center>🌿 Fresh Ingredients, Better Recipes · "
    "Happy Cooking! ❤️</center>",
    unsafe_allow_html=True
)
