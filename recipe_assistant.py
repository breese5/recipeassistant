import json
import streamlit as st

### Step 1: Load and Process JSON Data ###
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipes = []
    for recipe_id, recipe_data in data.items():
        chunk = {
            "id": recipe_id,
            "title": recipe_data["title"].strip(),
            "ingredients": " ".join(recipe_data["ingredients"]),
            "instructions": recipe_data["instructions"].strip(),
        }
        recipes.append(chunk)
    return recipes

### Step 2: Implement Manual Text Matching ###
def clean_text(text):
    return "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in text)

def count_matching_words(query, text):
    query_words = set(clean_text(query).split())
    text_words = set(clean_text(text).split())
    return len(query_words & text_words)

def search_recipe(query, recipes, top_k=3):
    ranked_recipes = []
    for recipe in recipes:
        title_match = count_matching_words(query, recipe["title"])
        ingredient_match = count_matching_words(query, recipe["ingredients"])
        total_score = title_match + ingredient_match

        if total_score > 0:
            ranked_recipes.append((recipe, total_score))

    ranked_recipes.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked_recipes[:top_k]]

### Step 3: Generate Natural Responses ###
def generate_response(query, recipes):
    matches = search_recipe(query, recipes)
    if not matches:
        return "Sorry, I couldn't find a matching recipe. Try different keywords!"

    response = f"Here are the best matches for '{query}':\n\n"
    for recipe in matches:
        response += f"🍽 **{recipe['title']}**\n"
        response += f"🔹 Ingredients: {recipe['ingredients']}\n"
        response += f"📖 Instructions: {recipe['instructions'][:200]}...\n\n"

    return response

### Step 4: Deploy as a Simple Streamlit App ###
def streamlit_app():
    recipes = load_json("recipes.json")

    st.title("🍳 Recipe Assistant (Manual RAG)")
    query = st.text_input("Enter an ingredient or recipe name:")

    if query:
        with st.spinner("Searching..."):
            response = generate_response(query, recipes)

        st.subheader("Results:")
        st.write(response)

if __name__ == "__main__":
    streamlit_app()
