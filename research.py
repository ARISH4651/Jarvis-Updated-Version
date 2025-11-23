from duckduckgo_search import DDGS

class Researcher:
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query, max_results=3):
        """Performs a web search and returns a summary."""
        try:
            # Enforce English results with region='us-en'
            results = list(self.ddgs.text(query, region='us-en', max_results=max_results))
            if not results:
                return {"status": "error", "message": "No results found."}
            
            # Format results
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get('title'),
                    "link": r.get('href'),
                    "snippet": r.get('body')
                })
            
            return {
                "status": "success",
                "message": f"Found {len(formatted_results)} results for '{query}'.",
                "data": formatted_results
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def summarize(self, text):
        # Placeholder for a local LLM or summarization logic
        # For now, we just return the text as is or truncated
        return text[:500] + "..."
