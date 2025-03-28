#   streamlit run app_llm.py

import json
import streamlit as st
import time
import pandas as pd
import os
import cohere
import requests
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64


COHERE_API_KEY = os.getenv("COHERE_API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")

# Get your Cohere API for the app to work
with open("cohere.key") as f:
    COHERE_API_KEY = f.read().strip()

client = cohere.ClientV2(COHERE_API_KEY)

st.markdown(
    """
    <style>
    .block-container {
        background-color: white;
        border-radius: 15px; /* Rounded corners */
        padding: 20px;
        box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.2);
        max-width: 800px;
        margin: 100px auto; /* Leave space at the top and bottom */
        max-height: calc(100vh - 120px); /* Prevent touching top/bottom */
        overflow-y: auto; /* Scrollable if content exceeds box height */
    }

    .stApp {
        background: linear-gradient(45deg, #1e5e65, #2a797c, #34a4a8, #1e5e65); /* Gradient background */
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Override the default Streamlit container (the block container) styling.
st.markdown(
    """
    <style>
    /* Change the app background */
    body {
        background-color: #f0f2f6;
    }
    /* Override the main content container styling */
    .stApp .block-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        max-width: 1000px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to get the base64 encoded version of the image
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Base64 encode the image
image_path = "logo.png"  
image_base64 = get_image_base64(image_path)

# HTML to display the base64 image
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-top: -40px;">
        <img src="data:image/png;base64,{image_base64}" alt="App Logo" style="width: 400px;">
    </div>
    """,
    unsafe_allow_html=True
)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Quiz Practice", "Translate with AI", "Quiz Records"])

with tab1:
    # Session State Setup
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # --- Step 1: Input Filters ---
    st.header("Configure the Quiz to Practice")

    # Create three columns for the input filters
    col1, col2, col3 = st.columns(3)

    # Add the select boxes to the columns
    with col1:
        language = st.selectbox(
            "Select Language",
            options=["English", "Spanish", "Portuguese"],
            index=0
        )

    with col2:
        difficulty = st.selectbox(
            "Select Difficulty",
            options=["Basic", "Intermediate", "Advanced"],
            index=0
        )

    with col3:
        topic = st.selectbox(
            "Select Topic",
            options=["Travel", "University", "Movies", "Food", "Hobbies"],
            index=0
        )

    # Apply custom CSS to style the default Streamlit button
    st.markdown(
        """
        <style>
        /* Center the button container */
        .stButton button {
            background: linear-gradient(45deg, #6A5ACD, #48D1CC); /* Cool gradient with blue and cyan */
            border: none;
            border-radius: 12px;
            color: white !important; /* Ensure text stays white */
            padding: 10px 100px;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.5s, transform 0.2s; /* Smooth transition effects */
        }

        .stButton button:hover {
            background: linear-gradient(45deg, #1E90FF, #32CD32); /* Blue to green gradient on hover */
            transform: scale(1.1); /* Slightly enlarge the button */
        }

        /* Fix for the :active state */
        .stButton button:active {
            background: linear-gradient(45deg, #6A5ACD, #48D1CC) !important; /* Match the default gradient */
            color: white !important; /* Ensure text stays white */
            transform: scale(1); /* Prevent further resizing */
            box-shadow: none !important; /* Remove default shadow if needed */
        }

        /* Center the button on the page */
        div.stButton {
            display: flex;
            justify-content: center; /* Horizontally center the button */
        }

        /* Center the button on the page */
        div.stButton {
            display: flex;
            justify-content: center; /* Horizontally center the button */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Add the original Streamlit button
    if st.button("Start"):
        # --- Step 2: Generate Quiz with LLM ---
        st.session_state.generating_quiz = True
        st.session_state.submitted = False

        # Initialize the progress bar
        progress_bar = st.progress(0)

        # Simulate incremental progress while generating the quiz
        for percent_complete in range(0, 95, 10):  # Simulating progress updates
            time.sleep(0.6)  # Simulate the LLM taking some time to respond
            progress_bar.progress(percent_complete)

        # Construct the new prompt for the chat-based API
        prompt_template = (
                "Create 4 different fill-in-the-blank questions for {language} learners regarding {topic} at a {difficulty} level. "
                "Each question should focus specifically on grammar rules (e.g., articles, prepositions, conjunctions) or verbal tenses (e.g., past, present, future). "
                "Each question should be a single sentence with only one blank (represented by ___) to test knowledge of grammar or tenses. "
                "For each question, provide 4 distinct options (only one of which is correct) and indicate the correct answer's index (0, 1, 2, or 3). "
                "Output the result in strict JSON format with a key 'questions', which is a list of objects. "
                "Each object should have keys 'question', 'options', and 'answer'."
            )
        final_prompt = prompt_template.format(language=language, topic=topic, difficulty=difficulty)
        
        formatted_message = {
            "role": "user",
            "content": final_prompt
        }

        try:
            # Call Cohere's chat API
            response = client.chat(
                model="command-r-plus",
                messages=[formatted_message]
            )
            
            # Iterate over `response.message.content` as objects
            generated_text = "".join(
                item.text for item in response.message.content if item.type == "text"
            )
            
            # Parse the generated JSON text into a dictionary
            st.session_state.quiz_data = json.loads(generated_text)

            # Reset user answers and submission state
            st.session_state.user_answers = [None] * len(st.session_state.quiz_data.get("questions", []))
            st.session_state.submitted = False

             # Quiz generation completed
            progress_bar.progress(100)  # Complete progress
            time.sleep(0.5)  # Small pause for user experience
            progress_bar.empty()  # Remove the progress bar
            st.session_state.generating_quiz = False


        except AttributeError as e:
            st.error(f"Error accessing response content: {e}")

        except (ValueError, json.JSONDecodeError) as e:
            st.error(f"Error parsing or processing LLM response: {e}")

    # --- Step 3: Display Quiz ---
    if st.session_state.quiz_data:
        st.header("Step 2: Answer the Quiz")

        user_answers = st.session_state.user_answers
        correct_answers = []

        # Iterate over each question
        for idx, q in enumerate(st.session_state.quiz_data.get("questions", [])):
            st.write(f"Q{idx + 1}: {q.get('question')}")
            options = q.get("options", [])
            # Do NOT display the correct answer in the dropdown directly
            correct_answers.append({
                "index": int(q.get("answer")),  # Store as a dictionary (hidden from dropdown menu)
                "options": options  # Maintain the dropdown options separately
            })

            # Display dropdown for each question
            user_answers[idx] = st.selectbox(
                label=f"Select an answer for Q{idx + 1}:",
                options=["Select an option"] + options,  # Add placeholder option
                index=0,
                key=f"question_{idx}"
            )

            # Check if the quiz is submitted and show the correct answer
            if st.session_state.get("submitted", False):
                correct_option = options[correct_answers[idx]["index"]]  # Access the correct index from the dictionary  # Correct answer for the specific question


    # --- Step 4: Submit Answers ---
    if st.session_state.quiz_data and not st.session_state.submitted:
        submit_quiz_button = st.button("Submit Quiz")  # Create the button
        if submit_quiz_button:
            st.session_state.submitted = True  # Set the submitted flag to True
            correct = 0
            total = len(st.session_state.quiz_data.get("questions", []))

            # Iterate through each question and calculate the score
            for idx, q in enumerate(st.session_state.quiz_data.get("questions", [])):
                options = correct_answers[idx]["options"]  # Access dropdown options
                correct_index = correct_answers[idx]["index"]  # Get the correct index
                user_answer = user_answers[idx]  # Retrieve user's selected answer

                if user_answer == options[correct_index]:  # Compare user answer with correct one
                    correct += 1

            # Calculate and store the score in session state
            st.session_state.score = (correct / total) * 100
            st.success(f"Your score is: {st.session_state.score:.2f}% ({correct}/{total} correct).")

    # --- Step 5: Display Correct Answers ---
    if st.session_state.get("submitted", False):
        if st.button("Check Correct Answers"):
            st.header("Correct Answers:")
            for idx, q in enumerate(st.session_state.quiz_data.get("questions", [])):
                options = q.get("options", [])
                correct_option = options[correct_answers[idx]["index"]]  # Access the correct index from the dictionary # Retrieve the correct answer
                st.markdown(f"**Q{idx + 1}: {correct_option}**")

    # Apply custom CSS styles
    st.markdown(
        """
        <style>
        /* Style for Restart Practice button */
        div[data-testid="column"] button:first-child {
            background: linear-gradient(45deg, #4B0082, #9400D3);
            border: none;
            border-radius: 12px;
            color: white;
            padding: 10px 20px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.5s, transform 0.2s;
        }
        div[data-testid="column"] button:first-child:hover {
            background: linear-gradient(45deg, #FF4500, #FFA500); /* Red-orange to Orange on hover */
            transform: scale(1.1); /* Slightly enlarge the button */
        }

        /* Style for Submit Today's Results button */
        div[data-testid="column"] button:nth-child(2) {
            background: linear-gradient(45deg, #32CD32, #87CEEB); /* Lime Green to Sky Blue */
            border: none;
            border-radius: 12px;
            color: white;
            padding: 10px 20px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.5s, transform 0.2s;
        }
        div[data-testid="column"] button:nth-child(2):hover {
            background: linear-gradient(45deg, #228B22, #1E90FF); /* Forest Green to Dodger Blue */
            transform: scale(1.1); /* Slightly enlarge the button */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # --- Step 5: Add Post-Submission Buttons ---
    if st.session_state.get("submitted", False):
        col1, col2, col3 = st.columns(3)  # Create two side-by-side buttons

        with col1:
            if st.button("Restart Practice"):
                st.session_state.clear()  # Reset the session state to restart the app
                st.experimental_rerun()  # Force the app to rerun

        with col3:
            if st.button("Submit today's Results"):
                # Define the database filename
                db_file = "quiz_results.csv"

                # Prepare the data to store
                result_data = {
                    "Language": [language],
                    "Difficulty": [difficulty],
                    "Topic": [topic],
                    "Grade": [st.session_state.score],  # Use the stored score
                    "Date": [datetime.today().strftime('%Y-%m-%d')]
                }
                result_df = pd.DataFrame(result_data)

                # Check if the file already exists
                if os.path.exists(db_file):
                    # Append to the existing database
                    existing_df = pd.read_csv(db_file)
                    updated_df = pd.concat([existing_df, result_df], ignore_index=True)
                    updated_df.to_csv(db_file, index=False)
                else:
                    # Create a new database
                    result_df.to_csv(db_file, index=False)

                st.success("Your results have been successfully submitted!")


# New tab for the chatbot
with tab2:
    with open("ocr.key") as file:
        ocr_api_key = file.read().strip()

    def translate_text(model, text, source_lang, target_lang):
        """
        Translate text using Cohere's API.
        """
        prompt = f"Translate the following text from {source_lang} to {target_lang}:\n{text}"
        response = client.generate(
            model=model,
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return response.generations[0].text.strip()

    def ocr_space_api(image_path, api_key):
        """
        Sends an image to the OCR.Space API for text recognition.
        """
        with open(image_path, 'rb') as image_file:
            response = requests.post(
                url='https://api.ocr.space/parse/image',
                files={'file': image_file},
                data={'apikey': api_key, 'language': 'eng'}
            )
        result = response.json()
        if result.get("ParsedResults"):
            return result["ParsedResults"][0]["ParsedText"]
        else:
            return "No text found or an error occurred."


    def main():
        st.markdown("Translate text from one language to another using Cohere!")

        # Layout for "From" and "To" dropdowns
        cols = st.columns(2)
        source_lang = cols[0].selectbox("From", ["English", "Spanish", "French", "German", "Japanese", "Chinese", "Italian", "Portuguese"])
        target_lang = cols[1].selectbox("To", [ "Spanish", "English", "French", "German", "Japanese", "Chinese", "Italian", "Portuguese"])

        # Text input for user to enter the text to be translated
        user_input = st.text_area("Enter the text you want to translate:", key="input")

        cols = st.columns(2)  # Create two columns
        with cols[0]:  # First column for the Translate button
            if st.button("Translate"):
                if user_input.strip():  # Check if the user input is not empty
                    translation = translate_text("command-r-plus", user_input, source_lang, target_lang)
                    st.markdown("### Translated Text:")
                    st.markdown(
                        f"<div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;'>{translation}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Please enter text to translate.")

        with cols[1]:  # Second column for the Restart button
            if st.button("Restart"):
                st.session_state.clear()  # Clear session state to reset the app
                st.experimental_rerun()  # Rerun the app to refresh the UI

        st.markdown("### Or instead upload an image to translate the text:")
        uploaded_file = st.file_uploader("Upload an image (jpg, jpeg, png):", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            with open("uploaded_image.png", "wb") as f:
                f.write(uploaded_file.getbuffer())

            if st.button("Extract and Translate Text"):
                api_key = ocr_api_key  
                extracted_text = ocr_space_api("uploaded_image.png", api_key)

                if extracted_text.strip():
                    st.markdown("### Extracted Text:")
                    st.text(extracted_text)

                    # Automatically translate the extracted text
                    translation = translate_text("command-r-plus", extracted_text, source_lang, target_lang)
                    st.markdown("### Translated Text:")
                    st.markdown(
                        f"<div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;'>{translation}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.error("No text could be extracted from the image. Please try again.")
        

    if __name__ == "__main__":
        main()



with tab3:
    # Load the dataset
    @st.cache_data
    def load_data():
        return pd.read_csv("quiz_results.csv")

    data = load_data()

    # Metrics Section
    total_quizzes = len(data)
    last_date = pd.to_datetime(data['Date']).max()
    days_since_last_practice = (datetime.now() - last_date).days

    # Metrics inside styled boxes
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; text-align: center;'>
                <h3>Total Quizzes Done</h3>
                <p style='font-size: 30px; font-weight: bold;'>{total_quizzes}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; text-align: center;'>
                <h3>Days Since Last Practice</h3>
                <p style='font-size: 30px; font-weight: bold;'>{days_since_last_practice}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Pie Charts Section (side by side)
    pie_col1, pie_col2 = st.columns(2)

    # Pie Chart: Quizzes per Language
    language_counts = data['Language'].value_counts()
    pie_language = px.pie(
                names=language_counts.index,
                values=language_counts.values,
                title="Quizzes Per Language",
                color_discrete_sequence=["#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]  # Add your desired color sequence
            )
    with pie_col1:
        st.plotly_chart(pie_language, use_container_width=True)

    # Pie Chart: Quizzes per Difficulty
    difficulty_counts = data['Difficulty'].value_counts()
    pie_difficulty = px.pie(
                    names=difficulty_counts.index,
                    values=difficulty_counts.values,
                    title="Quizzes Per Difficulty",
                    color_discrete_sequence=["#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]  # Add your desired color sequence
                )
    with pie_col2:
        st.plotly_chart(pie_difficulty, use_container_width=True)

    # Line Plot: Quizzes Per Day
    st.markdown("### Filter Quizzes By Date:")
    date_filter = st.date_input("Select Date Range:", [])
    filtered_data = data.copy()

    if date_filter:
        start_date = date_filter[0] if len(date_filter) > 0 else data["Date"].min()
        end_date = date_filter[1] if len(date_filter) > 1 else data["Date"].max()
        filtered_data = filtered_data[(pd.to_datetime(filtered_data["Date"]) >= pd.to_datetime(start_date)) &
                                      (pd.to_datetime(filtered_data["Date"]) <= pd.to_datetime(end_date))]

    filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])
    quizzes_per_day = filtered_data.groupby(filtered_data["Date"].dt.date).size().reset_index(name="Count")
    line_plot = px.line(quizzes_per_day, x="Date", y="Count", title="Quizzes Per Day")
    st.plotly_chart(line_plot, use_container_width=True)