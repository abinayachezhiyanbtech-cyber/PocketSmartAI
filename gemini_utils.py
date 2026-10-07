import os
import base64

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


def build_prompt(category, data):
    budget = float(data.get("budget", 0))
    preferences = data.get("preferences", "")
    extra = data.get("extra", "")

    category_names = {
        "home": "Home Interior Planning",
        "party": "Party Budget Planning",
        "jewelry": "Jewelry Recommendations"
    }

    category_name = category_names.get(
        category,
        "Budget Planning"
    )

    return f"""
You are PocketSmart AI, a smart budget
and recommendation assistant.

Planning category: {category_name}

User's budget: Rs. {budget:,.2f}

User preferences: {preferences}

Additional details: {extra or "Not provided"}

Your tasks:

1. Recommend practical options that suit the user.
2. Allocate the budget across suitable categories.
3. Show estimated prices in Indian Rupees.
4. Keep the estimated total within the user's budget.
5. Suggest relevant comparison platforms such as
   Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO.
6. Explain why each recommendation is suitable.
7. Clearly label prices as estimates.
8. Do not claim that you checked live prices,
   availability or stock.
9. Do not invent product links.
10. Format the answer with headings and bullet points.

For home planning, consider furniture, lighting
and decorations.

For party planning, consider food, venue,
decorations and entertainment.

For jewelry planning, consider occasion,
outfit colors, jewelry style and affordability.

Return a helpful, clear recommendation plan.
"""


def get_demo_result(category):
    demo_results = {
        "home": """
## Home Interior Budget Plan

1. Lighting: Compare affordable LED lights.
2. Furniture: Prioritize essential furniture.
3. Decoration: Consider curtains and wall art.
4. Storage: Look for budget-friendly organizers.

Compare options on Amazon, Flipkart and IKEA.

These are planning ideas, not live product listings.
Check current prices before purchasing.
""",

        "party": """
## Party Budget Plan

Suggested budget allocation:

- Food and drinks: 40%
- Venue: 25%
- Decorations: 20%
- Cake and entertainment: 10%
- Emergency expenses: 5%

Compare food options on Swiggy and Zomato.
Check venue prices directly with providers.

These are estimates, not live vendor quotations.
""",

        "jewelry": """
## Jewelry Recommendations

1. Traditional: Jhumkas and a matching necklace.
2. Minimal: Small studs and a delicate chain.
3. Festive: Statement earrings and a bracelet.
4. Everyday: Lightweight earrings and a pendant.

Choose colors that complement your outfit.
Compare affordable options on Amazon and Flipkart.

These are style suggestions, not live listings.
"""
    }

    return demo_results.get(
        category,
        "Please enter your budget and preferences."
    )


async def generate_recommendations(
    category,
    data,
    image_data=None,
    mime_type=None
):
    # Demo mode works without a Gemini API key.
    if not API_KEY:
        return (
            "DEMO MODE: Add your Gemini API key "
            "to the .env file to enable AI responses.\n\n"
            + get_demo_result(category)
        )

    try:
        client = genai.Client(api_key=API_KEY)

        prompt = build_prompt(category, data)

        contents = [prompt]

        # Optional outfit image for jewelry planning.
        if image_data and mime_type:
            image_bytes = base64.b64decode(image_data)

            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
            )

            contents.append(
                "Analyze the outfit colors and suggest "
                "matching jewelry styles."
            )

        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )

        result = response.text

        if result:
            return result

        return get_demo_result(category)

    except Exception as error:
        print("Gemini API error:", str(error))

        return (
            "Gemini AI could not generate a response. "
            "Please check your API key, model and "
            "internet connection.\n\n"
            + get_demo_result(category)
        )