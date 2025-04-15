import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from config import GOOGLE_API_KEY, TAVILY_API_KEY
from contacts_helpers import JobDetails, RankedProfiles, generate_search_queries, format_search_results_for_prompt


# --- LangChain Setup ---

# 1. LLM Initialization (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.3) # Adjust temperature as needed

# 2. Tool Initialization (Tavily Search)
#    Increase max_results to get more candidates for the LLM to filter
tavily_tool = TavilySearchResults(max_results=15, tavily_api_key=TAVILY_API_KEY)

# 3. Parsers
job_details_parser = PydanticOutputParser(pydantic_object=JobDetails)
ranked_profiles_parser = PydanticOutputParser(pydantic_object=RankedProfiles)

# Prompt for Step 1: Extract Key Search Parameters
extract_prompt_template = PromptTemplate(
    template="""Analyze the following job description. Your goal is to extract key information that will be used to search for people on LinkedIn holding similar roles (considering job function, scope, company, and industry) for networking purposes.
    Other things to consider: 
    1. When extracting specific technical, domain, or high-impact soft skills mentioned, avoid locations or generic phrases.
    2. Add keywords to improve the accuracy of the search results, especially if the job description or company name are common phrases used in other contexts. 

Job Description:
{job_description}

{format_instructions}
""",
    input_variables=["job_description"],
    partial_variables={"format_instructions": job_details_parser.get_format_instructions()}
)

# Prompt for Step 4: Filter and Rank LinkedIn Profiles
filter_rank_prompt_template = PromptTemplate(
    template="""Based on the target job information below, please evaluate the following web search results intended to find relevant LinkedIn profiles.

Target Job Information:
- Title: {primary_job_title}
- Company: {company_name}
- Key Skills: {key_skills_for_networking}

Web Search Results (Snippets from search engine for site:linkedin.com/in/):
{search_results_snippets}

Instructions:
1. Carefully review each search result snippet and its URL.
2. Filter out any results that are clearly irrelevant (e.g., links to job postings themselves, company pages, recruiter profiles if distinguishable, profiles with titles/companies/skills completely unrelated to the target job).
3. From the remaining potentially relevant profiles, select and rank the top 5-7 most promising ones that likely represent individuals currently or recently in roles *similar* to the target job, based *only* on the information in the snippet. Prioritize relevance based on matching title, company, and mentioned skills apparent in the snippet.
4. Provide your ranked list with justifications.

{format_instructions}
""",
    input_variables=["primary_job_title", "company_name", "key_skills_for_networking", "search_results_snippets"],
    partial_variables={"format_instructions": ranked_profiles_parser.get_format_instructions()}
)

# --- LangChain Chains ---

# Chain for Step 1
extract_chain = extract_prompt_template | llm | job_details_parser

# Chain for Step 4
filter_rank_chain = filter_rank_prompt_template | llm | ranked_profiles_parser


# --- Main Orchestration Function ---

def find_linkedin_profiles(job_description: str) -> Optional[RankedProfiles]:
    """
    Orchestrates the workflow to find relevant LinkedIn profiles.

    Args:
        job_description: The job description text pasted by the user.

    Returns:
        A RankedProfiles object containing the list of profiles, or None if an error occurs.
    """
    try:
        # Step 1: Extract Key Search Parameters
        st.write("Step 1: Analyzing job description...")
        job_details: JobDetails = extract_chain.invoke({"job_description": job_description})
        st.success("✓ Job details extracted.")
        # st.json(job_details.dict()) # Optional: Display extracted details for debugging

        # Step 2: Construct LinkedIn Search Queries
        st.write("Step 2: Generating search queries...")
        search_queries = generate_search_queries(job_details)
        if not search_queries:
            st.warning("Could not generate specific search queries from the job description.")
            return None
        st.success(f"✓ Generated {len(search_queries)} search queries.")
        # st.write(search_queries) # Optional: Display queries

        # Step 3: Execute Web Search for LinkedIn Profiles
        st.write(
            f"Step 3: Searching the web for LinkedIn profiles (using {len(search_queries)} queries in parallel)...")
        start_time = time.time()
        all_search_results = []
        # Use max_workers suitable for your environment, maybe = len(search_queries) or slightly more/less
        with ThreadPoolExecutor(max_workers=len(search_queries) or 5) as executor:
            # Submit all tasks
            future_to_query = {executor.submit(tavily_tool.invoke, query): query for query in search_queries}
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    results = future.result()  # Get result from completed future
                    if isinstance(results, list):
                        all_search_results.extend(results)
                    elif isinstance(results, str):
                        st.info(f"Note: Tavily returned a summary string for query '{query}', skipping addition.")
                    else:
                        st.warning(f"Unexpected result type from Tavily for query '{query}': {type(results)}")
                except Exception as exc:
                    st.warning(f"Query '{query}' generated an exception: {exc}")

        search_duration = time.time() - start_time
        st.write(f"Search took {search_duration:.2f} seconds.")  # See how much time it took

        if not all_search_results:
            st.error("No potential LinkedIn profiles found via web search.")
            return None
        st.success(f"✓ Found {len(all_search_results)} potential profile snippets.")
        print(f"Results found: {all_search_results} profile snippets.")

        # Step 4: Filter and Rank LinkedIn Profiles
        st.write("Step 4: Filtering and ranking profiles using AI...")
        formatted_snippets = format_search_results_for_prompt(all_search_results)

        ranked_profiles: RankedProfiles = filter_rank_chain.invoke({
            "primary_job_title": job_details.primary_job_title,
            "company_name": job_details.company_name,
            "key_skills_for_networking": ", ".join(job_details.key_skills_for_networking), # Pass as string
            "search_results_snippets": formatted_snippets
        })
        st.success("✓ AI filtering and ranking complete.")

        return ranked_profiles

    except Exception as e:
        st.error(f"An error occurred during the process: {e}")
        import traceback
        st.error(traceback.format_exc()) # Print full traceback for debugging
        return None

# # --- Streamlit App Interface ---
#
# st.set_page_config(layout="wide")
# st.title("🔗 LinkedIn Profile Finder for Networking")
# st.markdown("Paste a job description below to find people on LinkedIn with similar roles for informational interviews.")
#
# # # Add placeholders for API keys if not found
# # if not google_api_key or not tavily_api_key:
# #     st.warning("API keys are missing. Please configure them in secrets.toml or environment variables.")
# #     google_api_key_input = st.text_input("Enter Google API Key (or set in secrets)", type="password")
# #     tavily_api_key_input = st.text_input("Enter Tavily API Key (or set in secrets)", type="password")
# #     if google_api_key_input: google_api_key = google_api_key_input
# #     if tavily_api_key_input: tavily_api_key = tavily_api_key_input
# #     # Re-initialize LLM and Tool if keys were entered manually
# #     if google_api_key and tavily_api_key:
# #         llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key, temperature=0.3)
# #         tavily_tool = TavilySearchResults(max_results=15, tavily_api_key=tavily_api_key)
# #         extract_chain = extract_prompt_template | llm | job_details_parser
# #         filter_rank_chain = filter_rank_prompt_template | llm | ranked_profiles_parser
# #         st.info("API Keys provided. Ready.")
# #     else:
# #         st.stop() # Stop if keys are still missing
#
# job_desc_input = st.text_area("Paste Job Description Here:", height=300, key="job_desc")
#
# if st.button("Find Relevant Profiles", key="find_profiles_button"):
#     if job_desc_input:
#         with st.spinner("Working... This may take a minute or two."):
#             final_results = find_linkedin_profiles(job_desc_input)
#
#         if final_results and final_results.profiles:
#             st.header("👥 Potential Networking Contacts")
#             st.markdown("---")
#             st.markdown(
#                 """
#                 **Disclaimer:** These potential contacts were identified using web search and AI analysis of publicly available snippets.
#                 Please review profiles carefully before reaching out. Always be professional and respectful when initiating contact for networking or informational interviews.
#                 Direct automated access to LinkedIn is against their Terms of Service.
#                 """
#             )
#             st.markdown("---")
#
#             for i, profile in enumerate(final_results.profiles):
#                 st.subheader(f"{i+1}. Potential Contact")
#                 st.markdown(f"**Profile URL:** [{profile.url}]({profile.url})")
#                 st.markdown(f"**AI Reason for Relevance:** {profile.justification}")
#                 st.markdown("---")
#         elif final_results and not final_results.profiles:
#              st.warning("The AI analysis filtered out all initial search results. Try refining the job description or the process might need tuning.")
#         else:
#             # Error messages are handled within find_linkedin_profiles
#             st.info("Process finished, check messages above.")
#     else:
#         st.warning("Please paste a job description first.")
