# Your Dream Job Planner

Analyze your CV against your desired role - this tool helps identify gaps in your CV, take action, find relevant people on LinkedIn you could reach out to for coffee.

Try it [here](https://dream-job-planner.streamlit.app).

---

## 🤔 Why Does This Exist?

><em>"Right now, is where the suffering arises. Between the sound and the projection, between things-as-they-are and things as we-want-them-to-be. This is what the Buddha taught: to misperceive reality is to suffer."</em><br>
> Yongey Mingyur Rinpoche, In Love with the World: A Monk's Journey Through the Bardos of Living and Dying

This tool has an optimistic name, but the reality is, preparing for specific roles that speak to your heart can be a heavy process. It's challenging to:

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

