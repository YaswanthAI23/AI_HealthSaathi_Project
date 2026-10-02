import streamlit as st

from health_ai import (
    LANGUAGES,
    answer_health_question,
    analyze_audio,
    analyze_image,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI HealthSaathi",
    page_icon="🩺",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 20px;
        margin-bottom: 25px;
    }

    .warning-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f0c36d;
        background-color: #fff8e6;
        margin-bottom: 20px;
    }

    .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #dddddd;
        text-align: center;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.write(
        "Ask a health question, speak your question, "
        "or upload a medicine/prescription image."
    )

    selected_language_name = st.selectbox(
        "Preferred language",
        list(LANGUAGES.keys()),
    )

    selected_language = LANGUAGES[
        selected_language_name
    ]

    st.markdown("---")

    st.markdown(
        """
        ### 🩺 AI HealthSaathi

        **AI for Bharat in Indian Languages**

        Features:

        - 💬 Multilingual health questions
        - 🎤 Voice interaction
        - 💊 Medicine information
        - 📄 Prescription understanding
        - 🧠 RAG knowledge base
        - 🛡️ Safety-first responses
        """
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🩺 AI HealthSaathi</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Multilingual AI health information and prescription assistant"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SAFETY NOTICE
# ============================================================

st.markdown(
    """
    <div class="warning-box">

    ⚠️ <b>Important:</b>

    AI HealthSaathi provides general health information
    and prescription understanding for educational purposes.

    It does not replace a doctor and does not independently
    prescribe or change medicines.

    If you have severe or emergency symptoms,
    seek urgent professional medical care.

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tab_health, tab_medicine, tab_voice = st.tabs(
    [
        "💬 Health Assistant",
        "💊 Medicine / Prescription",
        "🎤 Voice Assistant",
    ]
)


# ============================================================
# HEALTH ASSISTANT
# ============================================================

with tab_health:

    st.subheader("💬 Ask a Health Question")

    st.write(
        f"Response language: **{selected_language_name}**"
    )

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example:\n"
            "What are common causes of headache?\n\n"
            "You can also ask in your preferred Indian language."
        ),
        height=150,
    )

    ask_button = st.button(
        "Get Health Information",
        type="primary",
        use_container_width=False,
        key="health_button",
    )

    if ask_button:

        if not question.strip():

            st.warning(
                "Please enter a health question first."
            )

        else:

            with st.spinner(
                "AI HealthSaathi is processing your question..."
            ):

                result = answer_health_question(
                    question=question,
                    language=selected_language,
                )

            st.success("Response")

            st.markdown(result)


# ============================================================
# MEDICINE / PRESCRIPTION
# ============================================================

with tab_medicine:

    st.subheader(
        "💊 Medicine / Prescription Understanding"
    )

    st.write(
        "Upload a clear medicine strip, medicine box, "
        "medicine bottle, or doctor's prescription."
    )

    uploaded_file = st.file_uploader(
        "Upload medical image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
        help=(
            "Use a clear, well-lit image. "
            "Make sure the text is visible."
        ),
        key="medical_image",
    )

    image_question = st.text_area(
        "What would you like to know?",
        placeholder=(
            "Examples:\n"
            "What is this medicine generally used for?\n"
            "Explain this prescription.\n"
            "What precautions should I know?"
        ),
        height=120,
        key="image_question",
    )

    if uploaded_file is not None:

        st.markdown("### 📷 Uploaded Image")

        st.image(
            uploaded_file,
            caption="Medical image",
            use_container_width=True,
        )

    analyze_button = st.button(
        "🔍 Analyze Image",
        type="primary",
        key="image_button",
    )

    if analyze_button:

        if uploaded_file is None:

            st.warning(
                "Please upload a medicine or prescription image."
            )

        else:

            with st.spinner(
                "AI HealthSaathi is reading the image..."
            ):

                result = analyze_image(
                    image_bytes=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type,
                    question=image_question,
                    language=selected_language,
                )

            st.success("Analysis complete")

            st.markdown(result)

            st.info(
                "If a medicine name, dosage, timing, "
                "or prescription instruction is unclear, "
                "verify it with a doctor or pharmacist."
            )


# ============================================================
# VOICE ASSISTANT
# ============================================================

with tab_voice:

    st.subheader("🎤 Ask Using Your Voice")

    st.write(
        f"Speak your health question. "
        f"Response language: **{selected_language_name}**"
    )

    st.info(
        "Keep your recording short and speak clearly."
    )

    audio_value = st.audio_input(
        "Record your question",
        key="voice_input",
    )

    if audio_value is not None:

        st.audio(audio_value)

        process_voice_button = st.button(
            "🎙️ Process Voice Question",
            type="primary",
            key="voice_button",
        )

        if process_voice_button:

            with st.spinner(
                "AI HealthSaathi is understanding your voice..."
            ):

                result = analyze_audio(
                    audio_bytes=audio_value.getvalue(),
                    language=selected_language,
                )

            st.success("Voice processing complete")

            st.markdown(result)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    <b>AI HealthSaathi</b> • AI for Bharat in Indian Languages

    <br><br>

    For educational information only.
    Consult a qualified healthcare professional for
    diagnosis and treatment decisions.

    </div>
    """,
    unsafe_allow_html=True,
)