import io
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image


# ============================================================
# PATH / ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing.\n\n"
        "Create a .env file inside the AI_HealthSaathi folder "
        "and add:\n\n"
        "GEMINI_API_KEY=your_api_key_here"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)

# This is the model that your Gemini API error indicated
# is available for your account.
MODEL = "gemini-3.8-flash"

# Number of attempts for temporary service errors
MAX_RETRIES = 3


# ============================================================
# LANGUAGES
# ============================================================

LANGUAGES = {
    "English": "English",
    "తెలుగు (Telugu)": "Telugu",
    "हिन्दी (Hindi)": "Hindi",
    "தமிழ் (Tamil)": "Tamil",
    "ಕನ್ನಡ (Kannada)": "Kannada",
    "മലയാളം (Malayalam)": "Malayalam",
    "বাংলা (Bengali)": "Bengali",
    "मराठी (Marathi)": "Marathi",
    "ગુજરાતી (Gujarati)": "Gujarati",
    "ਪੰਜਾਬੀ (Punjabi)": "Punjabi",
    "ଓଡ଼ିଆ (Odia)": "Odia",
    "অসমীয়া (Assamese)": "Assamese",
    "اردو (Urdu)": "Urdu",
}


# ============================================================
# KNOWLEDGE BASE
# ============================================================

KNOWLEDGE_FILE = (
    BASE_DIR / "knowledge" / "health_knowledge.txt"
)


def load_knowledge():
    """
    Load local health knowledge for the RAG context.
    """

    try:
        if KNOWLEDGE_FILE.exists():
            return KNOWLEDGE_FILE.read_text(
                encoding="utf-8"
            )
    except Exception:
        pass

    return (
        "No local knowledge base is available. "
        "Provide only general educational health information."
    )


KNOWLEDGE = load_knowledge()


# ============================================================
# SAFETY INSTRUCTIONS
# ============================================================

SYSTEM_RULES = """
You are AI HealthSaathi, a multilingual health-information
and prescription-understanding assistant.

Your purpose is to provide general educational health information,
help users understand medicine information, and explain readable
doctor-provided prescription instructions.

IMPORTANT SAFETY RULES:

1. Provide general educational health information only.

2. Do not diagnose a disease with certainty.

3. Do not independently prescribe medicines.

4. Do not start, stop, increase, decrease, or change medicine dosage.

5. Do not create a new prescription.

6. For prescriptions, explain ONLY information that is clearly
   readable from the doctor's prescription.

7. Never guess an unclear:
   - medicine name
   - active ingredient
   - dosage
   - frequency
   - timing
   - duration
   - special instruction

8. If an image is blurry, cropped, dark, unclear, or unreadable,
   clearly tell the user that the information cannot be reliably read.

9. If prescription information is unclear, recommend verification
   with a doctor or pharmacist.

10. Medicine information may include:
    - general/common use
    - general precautions
    - common side effects
    - important warning signs

11. Do not recommend changing the doctor's prescription.

12. If the user asks to change a medicine dose or timing,
    advise them to contact their doctor or pharmacist.

13. If serious or emergency warning signs are present,
    advise the user to seek urgent professional medical care.

14. Use simple language in the user's selected language.

15. Do not invent information.

16. Medicine reminders must use ONLY clearly readable
    doctor-provided instructions.

17. Never invent a medicine schedule.

18. If uncertain, explicitly say that you are uncertain.

19. AI HealthSaathi does not replace a qualified healthcare
    professional.
"""


# ============================================================
# ERROR HANDLING
# ============================================================

def is_temporary_error(error_text):
    """
    Detect temporary Gemini service errors.
    """

    text = str(error_text).upper()

    temporary_errors = [
        "503",
        "UNAVAILABLE",
        "SERVICE UNAVAILABLE",
        "INTERNAL",
        "DEADLINE",
        "TIMEOUT",
    ]

    return any(
        error in text
        for error in temporary_errors
    )


def friendly_error(error_text):
    """
    Convert technical Gemini errors into user-friendly messages.
    """

    if is_temporary_error(error_text):
        return (
            "The AI service is temporarily busy.\n\n"
            "Please wait a few seconds and try again."
        )

    text = str(error_text)

    if "API_KEY" in text.upper():
        return (
            "The Gemini API key could not be verified. "
            "Please check the GEMINI_API_KEY in your .env file."
        )

    if "404" in text or "NOT_FOUND" in text:
        return (
            "The configured Gemini model is not available "
            "for this API account."
        )

    if "429" in text or "RESOURCE_EXHAUSTED" in text:
        return (
            "The AI service has temporarily reached its usage limit. "
            "Please try again later."
        )

    return (
        "The AI service could not process the request right now. "
        "Please try again."
    )


# ============================================================
# TEXT GENERATION
# ============================================================

def generate_text(prompt):
    """
    Generate a Gemini response with automatic retry
    for temporary service failures.
    """

    last_error = ""

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_RULES,
                    temperature=0.2,
                ),
            )

            if response.text:
                return response.text

            return (
                "The AI did not return a response. "
                "Please try again."
            )

        except Exception as error:

            last_error = str(error)

            if is_temporary_error(last_error):

                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue

            break

    return friendly_error(last_error)


# ============================================================
# HEALTH QUESTION
# ============================================================

def answer_health_question(question, language):
    """
    Answer a general health question.
    """

    if not question or not question.strip():
        return "Please enter a health question."

    prompt = f"""
Selected response language:
{language}

User question:
{question}

Local AI HealthSaathi knowledge base:
{KNOWLEDGE}

Provide a simple educational answer.

Where relevant, structure the response as:

### General information
Explain the topic simply.

### General precautions
Mention useful precautions.

### Self-care / prevention
Mention general safe steps where appropriate.

### Warning signs
Mention symptoms that require medical attention.

### When to consult a healthcare professional
Explain when the user should contact a doctor.

IMPORTANT:

- Do not give a definitive diagnosis.
- Do not prescribe medicine independently.
- Do not change medicine dosage.
- Do not invent facts.
- If the user's question requires professional diagnosis,
  clearly recommend consulting a healthcare professional.

Respond entirely in {language}.
"""

    return generate_text(prompt)


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image(
    image_bytes,
    mime_type,
    question,
    language,
):
    """
    Analyze a medicine image or doctor's prescription.
    """

    if not image_bytes:
        return "No image was provided."

    if not mime_type:
        mime_type = "image/jpeg"

    if question and question.strip():
        user_question = question.strip()
    else:
        user_question = (
            "Explain the readable information in this image."
        )

    prompt = f"""
Selected response language:
{language}

User question:
{user_question}

Analyze the uploaded medical image.

The image may contain:

- medicine strip
- medicine bottle
- medicine box
- doctor's prescription
- medical instructions

IMPORTANT:

Only report information that is clearly readable.

DO NOT:

- guess unclear text
- guess medicine names
- guess active ingredients
- guess dosage
- guess timing
- guess frequency
- guess duration
- create a prescription
- change doctor's instructions

------------------------------------------------------------
MEDICINE IMAGE
------------------------------------------------------------

If this is a medicine image, explain ONLY clearly readable:

1. Medicine name
2. Active ingredient
3. General/common use
4. General precautions
5. Common side effects
6. Important warning signs

------------------------------------------------------------
PRESCRIPTION IMAGE
------------------------------------------------------------

If this is a doctor's prescription, explain ONLY clearly readable:

1. Medicine name
2. Doctor-provided dosage
3. Frequency / timing
4. Duration
5. Special instructions

------------------------------------------------------------
UNCLEAR INFORMATION
------------------------------------------------------------

If any information cannot be read reliably, say:

"The information is unclear and should be verified with a doctor or pharmacist."

Do not guess missing information.

Respond entirely in {language}.

Local knowledge base:
{KNOWLEDGE}
"""

    # --------------------------------------------------------
    # Open image
    # --------------------------------------------------------

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

    except Exception:

        return (
            "The uploaded image could not be read.\n\n"
            "Please upload a clear JPG, JPEG, PNG, or WebP image."
        )

    # --------------------------------------------------------
    # Gemini image request with retry
    # --------------------------------------------------------

    last_error = ""

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    prompt,
                    image,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_RULES,
                    temperature=0.1,
                ),
            )

            if response.text:
                return response.text

            return (
                "I could not reliably read the information "
                "from this image."
            )

        except Exception as error:

            last_error = str(error)

            if is_temporary_error(last_error):

                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue

            break

    return friendly_error(last_error)


# ============================================================
# VOICE ANALYSIS
# ============================================================

def analyze_audio(audio_bytes, language):
    """
    Analyze a user's voice question.

    Streamlit's st.audio_input normally provides WAV audio.
    """

    if not audio_bytes:
        return "No audio was provided."

    prompt = f"""
Selected response language:
{language}

Listen carefully to the user's voice recording.

Understand the spoken health question and provide
general educational health information.

IMPORTANT:

- Do not diagnose with certainty.
- Do not independently prescribe medicines.
- Do not change medicine dosage.
- Do not create a prescription.
- Do not invent information.
- Mention warning signs when appropriate.
- Recommend professional medical help when appropriate.
- If the audio is unclear, do not guess.
- If you cannot understand the recording, ask the user
  to record the question again.

Respond entirely in {language}.
"""

    try:

        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type="audio/wav",
        )

    except Exception as error:

        return (
            "The voice recording could not be prepared "
            "for analysis.\n\n"
            f"{str(error)}"
        )

    last_error = ""

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    prompt,
                    audio_part,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_RULES,
                    temperature=0.2,
                ),
            )

            if response.text:
                return response.text

            return (
                "I could not understand the voice recording.\n\n"
                "Please record your question again."
            )

        except Exception as error:

            last_error = str(error)

            if is_temporary_error(last_error):

                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue

            break

    return friendly_error(last_error)