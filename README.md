# 👨‍💻 Automated Tech Profile AI Analyzer

A self-service portfolio evaluation tool built for hiring managers and technical recruiters to extract multiple GitHub repositories and provide an automated, objective technical analysis using Google's Gemini LLM.

Reviewing candidate repositories takes time. To streamline the evaluation process, I built this Streamlit application to automatically ingest my GitHub projects, analyze the raw code using Google's Gemini 3.5 Flash (High-Thinking mode), and generate a highly critical technical brief.

## 🎯 The Motivation

LLMs are notoriously sycophantic and prone to flattering users. This tool is explicitly engineered not to do that. The underlying prompt architecture forces the model to:

* **Act as an objective, highly critical Lead Systems Engineer.**
* **Strictly evaluate capabilities as an Individual Contributor** (ignoring managerial inflation).
* **Identify explicitly verified skills** based only on written code syntax.
* **Highlight blind spots:** The model is instructed to flag 2-3 crucial software engineering skills *missing* from my public repositories so hiring managers know exactly what to probe for during an interview.

## ⚙️ How It Works

1. **Context Ingestion:** Uses `gitingest` to pull the directory structure, metadata, and raw code from my primary repositories.
2. **Analysis:** The context is fed to `gemini-3.6-flash` utilizing advanced thinking configurations for deep architectural analysis.
3. **Report Generation & Dispatch:** The resulting Markdown report is displayed on the UI.

## 📚 Analyzed Repositories

This application currently evaluates the following projects from my portfolio:

* **[ZeroHostCopyInference](https://github.com/Igkho/ZeroHostCopyInference):** A high-performance Zero-Host-Copy video inference pipeline written in C++/CUDA, utilizing TensorRT and ONNX backends for real-time edge processing.
* **[Spline](https://github.com/Igkho/Spline):** A C++/CUDA library for manipulating 2D parametric B-splines, featuring custom optimization algorithms (RMSProp, Newton-Raphson) for intersection finding.
* **[CropAndWeedDetection](https://github.com/Igkho/CropAndWeedDetection):** A complete PyTorch and YOLOv8 computer vision research pipeline for seedling detection, including ByteTrack object tracking and INT8 quantization.
* **[Pendulum](https://github.com/Igkho/Pendulum):** A Python-based numerical solver and simulator for differential-algebraic systems of equations using fourth-order Runge-Kutta (RK4) methods.
* **[TechProfileAI](https://github.com/Igkho/TechProfileAI):** A Python/Streamlit LLM application utilizing Google's Gemini Flash and Gitingest for automated, objective GitHub portfolio evaluation, featuring dynamic prompt engineering, PDF report generation, and automated Docker CI/CD deployments.

## 🛠️ Tech Stack

* **Frontend/Hosting:** Streamlit Community Cloud
* **LLM Engine:** Google GenAI SDK (gemini-3.5-flash)
* **Repository Processing:** Gitingest
* **Backend:** Python

## 🚀 Running Locally

If you prefer to run this analyzer locally rather than using the web version:

1. Clone this repository.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Streamlit secrets. Create a .streamlit/secrets.toml file in the root directory:
   ```Ini, TOML
   GEMINI_API_KEY = "your_google_api_key"
   SENDER_EMAIL = "your_sender_email@gmail.com"
   SENDER_PASSWORD = "your_app_password"
   RECEIVER_EMAIL = "your_destination_email@example.com"
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```
## 📄 License

This project is licensed under the MIT License.

**Third-Party Assets:** This repository includes the open-source [DejaVu Fonts](https://dejavu-fonts.github.io/) (located in the `fonts/` directory) to ensure consistent PDF report generation across all environments. The DejaVu fonts are distributed under their free and open-source license.