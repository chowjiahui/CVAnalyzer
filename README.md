# Your Dream Job Planner ✨

Stop dreaming, start planning! Analyze your CV against your desired role - identify gaps, have an action plan, and find inspiring role models on LinkedIn to guide your journey.

Try it [here](https://dream-job-planner.streamlit.app)!

---

## 🤔 Why Does This Exist?

><em>"Right now, is where the suffering arises. Between the sound and the projection, between things-as-they-are and things as we-want-them-to-be. This is what the Buddha taught: to misperceive reality is to suffer."</em><br>
> Yongey Mingyur Rinpoche, In Love with the World: A Monk's Journey Through the Bardos of Living and Dying

Landing your dream job can feel heavy and the path is often unknown. It's challenging to:

*   **Objectively assess** how well your current experience aligns with a specific job description.
*   **Pinpoint the exact skills or experiences** you need to develop.
*   **Create a concrete plan** to bridge those gaps effectively.
*   **Find relatable examples** of people who have successfully navigated a similar path.
 
This tool tackles these challenges head-on, from your CV and dream job description.

## 🚀 Key Features

*   **Gap Analysis:** Compare your CV against the job description to highlight missing keywords, skills, and potential experience gaps.
*   **Personalized Action Plan:** 
    *   Skills to acquire or deepen.
    *   Types of projects to undertake.
    *   Relevant online courses or certifications.
    *   Keywords to emphasize in your CV update.
*   **LinkedIn Role Model Finder:** Individuals currently in similar roles or companies, whom you might want to reach out for coffee.

## 📸 Screenshots / Demo

*Include 1-3 screenshots of your app in action here! Visuals are very helpful.*

**(Example Screenshot Placeholder 1: Upload Interface)**
![Upload Interface](link/to/your/screenshot1.png)

**(Example Screenshot Placeholder 2: Gap Analysis Results)**
![Gap Analysis](link/to/your/screenshot2.png)

**(Example Screenshot Placeholder 3: Action Plan & Role Models)**
![Action Plan](link/to/your/screenshot3.png)

*(Strongly recommend adding a short GIF or linking to a video demo if possible!)*

## 🛠️ How It Works

1.  **Input:** The user uploads their CV and pastes the job description text.
2.  **Parsing:** Text is extracted from the CV document.
3.  **Analysis:** Semantic analysis with Gemini model to compare the content of the CV against the requirements listed in the job description.
4.  **Gap Identification:** Differences and missing elements (skills, keywords, qualifications) are identified.
5.  **Action Plan:** Based on the identified gaps, actionable steps and learning resources are suggested.
6.  **Role Model Search:** Keywords derived from the job title and description are used to surface, filter and rank relevant LinkedIn profiles.

## ⚙️ Technology Stack

*   **Frontend:** Streamlit
*   **Key Libraries:**
    *   File reading: `PyPDF2`, `python-docx`
    *   Foundation model: `gemini-1.5-flash`
    *   Profile search: `langchain`, `Tavily`

## 📄 License

This project is licensed under the [Choose a License, e.g., MIT] License - see the `LICENSE` file for details.

