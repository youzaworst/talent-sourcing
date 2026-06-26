import json
import time
import arxiv
import sys
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field

# Define the database schema using Pydantic
class AuthorData(BaseModel):
    author_name: str = Field(description="Full name of the author")
    affiliation: str = Field(description="Current university, research institution, or corporate lab")
    previous_companies: str = Field(description="Comma-separated list of previous companies or institutions they worked for. 'None' if unknown.")
    notable_work: str = Field(description="Other famous papers, architectures, or software packages they contributed to.")
    education: str = Field(description="Degrees obtained and universities attended. 'Unknown' if not found.")
    areas_of_expertise: str = Field(description="Core domain specializations (e.g., Evaluation Design, Benchmarking, LLM Testing, Metrics).")
    paper_title: str = Field(description="The title of the paper they wrote that triggered this search.")
    paper_link: str = Field(description="The arXiv URL link to the paper.")
    date_of_publication: str = Field(description="The publication date of the paper (YYYY-MM-DD format).")

class AuthorDatabasePayload(BaseModel):
    records: list[AuthorData]

def build_author_database_records():
    # Insert your active API key here
    API_KEY = "YOUR_ACTUAL_API_KEY_HERE" 
    
    if API_KEY == "YOUR_ACTUAL_API_KEY_HERE":
        print("Error: Please replace 'YOUR_ACTUAL_API_KEY_HERE' with your real Gemini API key.")
        return
        
    client = genai.Client(api_key=API_KEY)

    print("Connecting to arXiv...")
    # CHANGED: Query updated to target Evaluation Design and Benchmarking
    query = (
        'ti:"evaluation design" OR abs:"evaluation design" OR '
        'ti:"benchmark design" OR abs:"benchmark design" OR '
        'ti:"evaluation framework" OR abs:"evaluation framework" OR '
        'ti:"evals" OR abs:"evals"'
    )
    search = arxiv.Search(query=query, max_results=20, sort_by=arxiv.SortCriterion.Relevance)
    arxiv_client = arxiv.Client()
    all_results = list(arxiv_client.results(search))
    
    print(f"Total papers found on arXiv: {len(all_results)}")
    print(f"Processing the first {min(20, len(all_results))} papers into independent database records...\n")
    
    database_ready_records = []
    
    for idx, paper in enumerate(all_results[:20], 1):
        print(f"-> Processing Paper {idx} ('{paper.title[:40]}...')...")
        authors_str = ", ".join([author.name for author in paper.authors])
        
        prompt = f"""
        Extract the professional profile background for EACH individual author listed below.
        Paper Title: {paper.title}
        Paper Link: {paper.entry_id}
        Publication Date: {paper.published.strftime('%Y-%m-%d')}
        Authors to process: {authors_str}
        Generate exactly one database item for each person listed. Use your training knowledge to find their career details.
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AuthorDatabasePayload,
                    system_instruction="You are a tabular data engine. Output valid raw JSON arrays only."
                )
            )
            
            batch_data = json.loads(response.text)
            if "records" in batch_data:
                for record in batch_data["records"]:
                    database_ready_records.append(record)
                print(f"   Successfully added authors for Paper {idx}!")
                    
        except APIError as ae:
            print(f"   ❌ Google API Error ({ae.code}): {ae.message}")
        except Exception as e:
            print(f"   ❌ Encountered parsing error: {e}")
            
        time.sleep(3)

    print(f"\nGenerated {len(database_ready_records)} independent database records!\n")
    if database_ready_records:
        print(json.dumps(database_ready_records, indent=4))
        
        # CHANGED: Target output file renamed sequentially to '6'
        with open("author_records_6.json", "w") as f:
            json.dump(database_ready_records, f, indent=4)
        print("\nRecords saved to 'author_records_6.json'")

if __name__ == "__main__":
    build_author_database_records()
