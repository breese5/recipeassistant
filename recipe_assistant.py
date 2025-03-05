import json
import streamlit as st
import requests

# 🔹 Your Google Drive file ID extracted from the link
GOOGLE_DRIVE_FILE_ID = "1prXiZZvhzdTC5QyfhwLhK6y5vXvL8Jzy"

# 🔹 Convert Google Drive link to a direct download URL
JSON_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

@st.cache_data
def load_json_from_url(url):
    """Download JSON file from a URL and load it."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error if request fails
        return response.json()  # Load JSON content
    except Exception as e:
        st.error(f"❌ Failed to load recipes: {e}")
        return None

### 🔹 Load recipes from Google Drive
recipes = load_json_from_url(JSON_URL)

if not recipes:
    st.warning("⚠️ Could not load recipes. Please check your Google Drive link.")
    st.stop()  # Stop execution if the file isn't loaded

st.success("✅ Recipe data loaded successfully!")

### 🔍 Recipe Search Functions
def clean_text(text):
    """Lowercase and remove punctuation manually."""
    return "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in text)

def count_matching_words(query, text):
    """Count how many words from query exist in text."""
    query_words = set(clean_text(query).split())
    text_words = set(clean_text(text).split())
    return len(query_words & text_words)  # Intersection of query & text words

def search_recipe(query, top_k=3):
    """Find the top-k most relevant recipes based on word overlap."""
    ranked_recipes = []
    
    for recipe_id, recipe_data in recipes.items():
        title = recipe_data["title"]
        ingredients = " ".join(recipe_data["ingredients"])

        title_match = count_matching_words(query, title) * 1  # Lower weight
        ingredient_match = count_matching_words(query, ingredients) * 2  # Higher weight
        total_score = title_match + ingredient_match

        if total_score > 0:
            ranked_recipes.append((recipe_data, total_score))

    ranked_recipes.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked_recipes[:top_k]]

### 🏠 Streamlit App
def generate_response(query):
    """Format search results as a readable response."""
    matches = search_recipe(query)

    if not matches:
        return "❌ No matching recipes found. Try different keywords!"

    response = f"### 🍽 Recipes for '{query}':\n\n"
    for recipe in matches:
        response += f"**🔹 {recipe['title']}**\n"
        response += f"**🥄 Ingredients:** {recipe['ingredients']}\n"
        response += f"**📖 Instructions:** {recipe['instructions'][:200]}...\n\n"

    return response

def streamlit_app():
    """Streamlit UI."""
    st.title("🍳 RAG Recipe Assistant")

    query = st.text_input("Enter an ingredient or recipe name:")
    
    if query:
        with st.spinner("Searching..."):
            response = generate_response(query)

        st.subheader("Results:")
        st.write(response)

if __name__ == "__main__":
    streamlit_app()
