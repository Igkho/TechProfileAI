import os
import streamlit as st

from gitingest import ingest
from google import genai
from google.genai import types

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

USE_CACHE = False  # Set to False to bypass local storage and force fresh web fetches

# Configure Logging
logging.basicConfig(
    filename='app_execution.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)


def send_email_report(prompt, llm_result, sender, password, receiver):
    """Dispatches the prompt and the LLM result to your personal email."""
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = "Automated Tech Analysis Report (Gemini)"

    # Format the email body
    body = f"PROMPT SENT:\n{'=' * 40}\n{prompt[:3000]}\n\n\nLLM RESULT:\n{'=' * 40}\n{llm_result}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Email report dispatched successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def analyze_multiple_projects(client):
    # Define the list of GitHub repositories
    github_repos = [
        "https://github.com/Igkho/ZeroHostCopyInference",
        "https://github.com/Igkho/Spline",
        "https://github.com/Igkho/CropAndWeedDetection",
        "https://github.com/Igkho/Pendulum"
    ]

    combined_context = ""
    cache_dir = "gitingest_cache"

    # Use Streamlit's status container for a better UX during long processes
    with st.status("🔍 Analyzing code repositories...", expanded=True) as status:

        # 1. --- CACHE SETUP ---
        # Create the folder if it doesn't exist yet
        if USE_CACHE and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            logging.info(f"📁 Created local cache directory: {cache_dir}/")

        # 2. --- THE FETCH LOOP ---
        for repo_url in github_repos:
            # Create a safe file name (e.g., "Igkho_Spline.txt")
            safe_name = repo_url.replace("https://github.com/", "").replace("/", "_") + ".txt"
            cache_path = os.path.join(cache_dir, safe_name)

            # Scenario A: Caching is ENABLED and the file exists (Cache Hit)
            if USE_CACHE and os.path.exists(cache_path):
                status.write(f"   -> 🟢 CACHE HIT: Loading {safe_name} from local disk")
                logging.info(f"   -> 🟢 CACHE HIT: Loading {safe_name} from local disk")
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_text = f.read()
                    combined_context += f"\n\n--- REPOSITORY: {repo_url} ---\n\n"
                    combined_context += cached_text

            # Scenario B: Caching is DISABLED or the file is missing (Cache Miss)
            else:
                status_msg = "🌐 CACHE MISS" if USE_CACHE else "🌐 FETCHING"
                status.write(f"   -> {status_msg}: Downloading {repo_url} from web...")

                try:
                    # Use the native gitingest package
                    summary, tree, content = ingest(repo_url)
                    # Combine the output into a single string
                    repo_text = f"{summary}\n\n{tree}\n\n{content}"

                    # Only write to disk if caching is enabled
                    if USE_CACHE:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            f.write(repo_text)

                    combined_context += f"\n\n--- REPOSITORY: {repo_url} ---\n\n"
                    combined_context += repo_text
                    st.write(f"      ✅ Successfully ingested {repo_url}")
                    logging.info(f"      ✅ Successfully ingested {repo_url}")
                except Exception as e:
                    logging.error(f"Error fetching {repo_url}: {e}")
                    st.error(f"❌ Error fetching {repo_url}: {e}")

        status.update(label="🧠 Querying Gemini Model for Technical Evaluation...", state="running")

        # 5. Build the master prompt
        prompt = f"""
        You are an objective Lead Systems Engineer tasked with translating a candidate's personal code repository into a technical brief for an HR recruiter or non-technical hiring manager.
        Analyze the provided repository digest. Maintain a neutral, analytical tone. Do not inflate the candidate's organizational seniority. Translate complex technical implementations into clear capabilities.
        Structure the report exactly as follows using Markdown formatting:
        1. Repository Overview
        Provide a brief, 2-3 sentence summary of the project's core function and its level of technical complexity.
        2. Core Tech Stack & Languages
        List the primary languages, frameworks, and core libraries utilized.
        3. Verified Skill Set
        List specific skills explicitly supported by the code syntax. Group them by category. For each, provide a brief, non-technical explanation of what this proves the candidate can do (e.g., "Asynchronous Programming: The candidate successfully wrote thread-safe code, demonstrating they can build high-performance applications without crashing.").
        4. Code Quality & Systems Knowledge
        Assess the maturity of the code. Look for error handling, memory safety, architecture patterns, and optimization strategies. State clearly what the code proves about their foundational engineering knowledge.
        5. Technical Seniority Estimate (Individual Contributor)
        Estimate their seniority strictly as an Individual Contributor (e.g., Junior, Mid, Senior, Staff) based only on code complexity and architectural maturity. You must not evaluate them for Managerial or Principal roles; personal repositories do not demonstrate cross-team leadership or business strategy.
        6. Blind Spots & Interview Probes
        List 2-3 crucial software engineering skills missing from this context that a hiring manager must probe for during an interview. (e.g., working within a large team, cloud deployment scale, handling legacy code, writing automated tests). Be highly critical and objective.
        7. Target Job Titles
        List 3-4 exact, realistic job titles this candidate should target based on the verified skills.

        Code Context from multiple repositories:
        {combined_context[:800000]} # Safely trimmed to stay within Gemini's 1M token context limit
        """

        try:
            # 6. Query Gemini
            # Pass the config into the generate_content call
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level=types.ThinkingLevel.HIGH  # Options: LOW, MEDIUM, HIGH, MINIMAL
                    )
                )
            )
            # 7. Log the execution
            logging.info(f"LLM PROMPT:\n{prompt}")
            logging.info(f"LLM RESULT:\n{response.text}")

            # 8. Fire off the email
            email_success = send_email_report(
                prompt,
                response.text,
                st.secrets["SENDER_EMAIL"],
                st.secrets["SENDER_PASSWORD"],
                st.secrets["RECEIVER_EMAIL"]
            )
            return response.text, email_success

        except Exception as e:
            st.error(f"❌ An error occurred during report generation: {e}")
            logging.error(f"❌ An error occurred during report generation: {e}")
            return None, False


# ==========================================
# STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Tech Profile AI Analyzer", page_icon="⚙️")
st.title("Automated Technical Profile AI Analyzer")
st.write("Extract code from GitHub, analyze it with Gemini 3.5 Flash, and generate an HR-friendly report.")
st.info("**Repos analyzed:** ZeroHostCopyInference, Spline, CropAndWeedDetection, Pendulum")

# Fail fast if secrets are missing
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    S_EMAIL = st.secrets["SENDER_EMAIL"]
    S_PASS = st.secrets["SENDER_PASSWORD"]
    R_EMAIL = st.secrets["RECEIVER_EMAIL"]
    client = genai.Client(api_key=API_KEY)
except KeyError as e:
    st.error(f"❌ **Configuration Error:** Missing required secret: `{e}`")
    st.info("Ensure your credentials are set in `.streamlit/secrets.toml` locally or in the Streamlit Cloud Settings.")
    st.stop()

if st.button("🚀 Start Analysis", type="primary"):
    report, email_sent = analyze_multiple_projects(client)

    if report:
        st.divider()
        st.subheader("📊 Technical Analysis Report")
        st.markdown(report)