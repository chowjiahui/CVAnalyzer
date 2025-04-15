from typing import List, Optional

from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Output ---

class JobDetails(BaseModel):
    """Structure to hold extracted job details relevant for searching contacts."""
    primary_job_title: str = Field(description="The most accurate primary job title mentioned.")
    company_name: str = Field(description="The name of the hiring company.")
    industry: Optional[str] = Field(description="The company's industry (inferred if not explicitly stated).")
    location: Optional[str] = Field(description="The primary work location (e.g., city, region, remote) if specified.")
    key_skills_for_networking: List[str] = Field(description="List of 3-5 specific technical, domain, or high-impact soft skills mentioned, useful for identifying relevant people.", max_items=7)
    suggested_search_titles: List[str] = Field(description="List of 2-3 alternative but closely related job titles for broader searching.", max_items=3)
    accuracy_keywords: str = Field(description="Keywords used to improve accuracy of search results.")

class ProfileResult(BaseModel):
    """Structure for a single ranked LinkedIn profile result."""
    url: str = Field(description="The direct URL to the LinkedIn profile.")
    justification: str = Field(description="Brief (1-sentence) justification for relevance based strictly on the search snippet content.")

class RankedProfiles(BaseModel):
    """Structure for the final list of ranked profiles."""
    profiles: List[ProfileResult] = Field(description="A ranked list of the most relevant LinkedIn profile URLs and justifications.")



# --- Helper Functions ---

def generate_search_queries(details: JobDetails) -> List[str]:
    """Generates targeted search queries for Tavily based on extracted details."""
    linkedin_site = "site:linkedin.com/in/"

    # 1. Primary title at the specific company
    base_query = f'{linkedin_site} "{details.primary_job_title}" "{details.company_name}" company '
    base_query_acc = base_query + details.accuracy_keywords
    no_title_query = f'{linkedin_site} "{details.company_name}" company ' + details.accuracy_keywords

    queries = [base_query, base_query_acc, no_title_query]

    # 2. add key skills to the same base query
    if details.key_skills_for_networking:
        for skill in details.key_skills_for_networking:
            queries.append(base_query + f' "{skill}"')

    # 3. Alternative titles at the company
    for alt_title in details.suggested_search_titles:
        queries.append(f'{linkedin_site} "{alt_title}" "{details.company_name}" company')

    # Add location if available and seems useful
    if details.location and details.location.lower() != 'remote':
         queries.append(f'{linkedin_site} "{details.primary_job_title}" "{details.company_name}" company "{details.location}"')

    # Deduplicate and limit number of queries if necessary
    unique_queries = list(dict.fromkeys(queries))
    print(f"unique queries generated: {unique_queries}")
    return unique_queries[:10] # Limit to a reasonable number of search API calls

def format_search_results_for_prompt(results: List[dict]) -> str:
    """Formats Tavily results into a string suitable for the LLM prompt."""
    formatted = ""
    for i, result in enumerate(results):
        # Tavily search results are often dictionaries with 'url' and 'content'
        url = result.get('url', 'N/A')
        content = result.get('content', 'No snippet available')
        formatted += f"Result {i+1}:\nURL: {url}\nSnippet: {content}\n---\n"
    return formatted if formatted else "No search results found."