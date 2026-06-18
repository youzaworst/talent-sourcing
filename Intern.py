import arxiv

def search_llm_judge_papers(max_results=100):
    query = (
        'ti:"llm as a judge" OR abs:"llm as a judge" OR '
        'ti:"llm-as-a-judge" OR abs:"llm-as-a-judge" OR '
        '(ti:llm AND ti:judge) OR (abs:llm AND abs:judge)'
    )
    
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    client = arxiv.Client()
    
    # Fetch results into a list to calculate exact totals
    all_results = list(client.results(search))
    total_found = len(all_results)
    
    print(f"=== SEARCH METRICS ===")
    print(f"Total papers matching criteria found: {total_found}\n")
    print(f"=== DISPLAYING PAPERS ===")
    
    for idx, paper in enumerate(all_results, 1):
        print(f"--- Paper {idx} of {total_found} ---")
        
        # Format the author extraction block
        for author in paper.authors:
            print(f"• Author: {author.name}")
            
            # NOTE: The following fields are not provided by the arXiv database.
            # To populate these, an external API integration like OpenAlex or Semantic Scholar is required.
            print(f"  └ Affiliation: [Not available natively on arXiv]")
            print(f"  └ Previous Companies: [Not available natively on arXiv]")
            print(f"  └ Notable Work: [Not available natively on arXiv]")
            print(f"  └ Education: [Not available natively on arXiv]")
            print(f"  └ Areas of Expertise: [Not available natively on arXiv]")
            
        print(f"• Link to Paper: {paper.entry_id}")
        print(f"• Date of Publication: {paper.published.strftime('%Y-%m-%d')}")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    search_llm_judge_papers(100)
