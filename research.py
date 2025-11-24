from duckduckgo_search import DDGS
import re

class Researcher:
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query):
        """
        Intelligent search that interprets questions and provides structured answers.
        Uses search results to enhance explanations, not replace them.
        """
        try:
            # Perform search with US English region
            results = list(self.ddgs.text(query, region='us-en', max_results=5))
            
            if not results:
                return {
                    "status": "error",
                    "message": "I couldn't find relevant information for that query."
                }
            
            # Interpret and structure the answer
            answer = self._interpret_results(query, results)
            
            return {
                "status": "success",
                "message": answer,
                "sources": [{"title": r['title'], "url": r['href']} for r in results[:3]]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Research module encountered an error: {str(e)}"
            }
    
    def _interpret_results(self, query, results):
        """
        Interpret search results and provide a structured, intelligent answer.
        """
        # Extract key information from top results
        top_result = results[0]
        snippets = [r.get('body', '') for r in results[:3] if r.get('body')]
        
        # Determine query type
        query_lower = query.lower()
        
        # Definition questions
        if any(word in query_lower for word in ['what is', 'what are', 'define']):
            return self._format_definition(query, snippets, top_result)
        
        # How-to questions
        elif any(word in query_lower for word in ['how to', 'how do', 'how can']):
            return self._format_howto(query, snippets, top_result)
        
        # Who questions
        elif 'who is' in query_lower or 'who are' in query_lower:
            return self._format_who(query, snippets, top_result)
        
        # Why questions
        elif 'why' in query_lower:
            return self._format_why(query, snippets, top_result)
        
        # General questions
        else:
            return self._format_general(query, snippets, top_result)
    
    def _format_definition(self, query, snippets, top_result):
        """Format definition-style answers"""
        subject = query.lower().replace('what is', '').replace('what are', '').replace('define', '').strip()
        
        answer = f"**{subject.title()}**\n\n"
        
        # Extract definition from snippets
        if snippets:
            # Clean and combine snippets
            definition = snippets[0][:300]
            answer += f"{definition}\n\n"
        
        answer += f"**Key Points:**\n"
        for i, snippet in enumerate(snippets[:3], 1):
            # Extract first sentence
            first_sentence = snippet.split('.')[0] if '.' in snippet else snippet[:100]
            answer += f"{i}. {first_sentence}\n"
        
        answer += f"\n📚 Source: {top_result['title']}"
        return answer
    
    def _format_howto(self, query, snippets, top_result):
        """Format how-to style answers with steps"""
        answer = f"**How to {query.lower().replace('how to', '').replace('how do i', '').replace('how can i', '').strip()}**\n\n"
        
        # Try to extract steps
        combined_text = ' '.join(snippets)
        
        # Look for numbered steps
        steps = re.findall(r'(\d+[\.\)]\s*[^\n]+)', combined_text)
        
        if steps:
            answer += "**Steps:**\n"
            for step in steps[:5]:
                answer += f"• {step.strip()}\n"
        else:
            # Provide general guidance
            answer += f"**Guidance:**\n{snippets[0][:400]}\n"
        
        answer += f"\n📚 Source: {top_result['title']}"
        return answer
    
    def _format_who(self, query, snippets, top_result):
        """Format who-is style answers"""
        subject = query.lower().replace('who is', '').replace('who are', '').strip()
        
        answer = f"**About {subject.title()}**\n\n"
        answer += f"{snippets[0][:350]}\n\n"
        
        answer += f"**Additional Context:**\n"
        if len(snippets) > 1:
            answer += f"{snippets[1][:200]}\n"
        
        answer += f"\n📚 Source: {top_result['title']}"
        return answer
    
    def _format_why(self, query, snippets, top_result):
        """Format why-style answers with reasoning"""
        answer = f"**{query.title()}**\n\n"
        
        answer += f"**Explanation:**\n{snippets[0][:350]}\n\n"
        
        answer += f"**Key Reasons:**\n"
        for i, snippet in enumerate(snippets[:3], 1):
            reason = snippet.split('.')[0] if '.' in snippet else snippet[:100]
            answer += f"{i}. {reason}\n"
        
        answer += f"\n📚 Source: {top_result['title']}"
        return answer
    
    def _format_general(self, query, snippets, top_result):
        """Format general answers"""
        answer = f"**{query.title()}**\n\n"
        
        # Provide comprehensive answer
        answer += f"{snippets[0][:400]}\n\n"
        
        if len(snippets) > 1:
            answer += f"**Additional Information:**\n{snippets[1][:250]}\n"
        
        answer += f"\n📚 Source: {top_result['title']}"
        return answer

    def summarize(self, text):
        # Placeholder for a local LLM or summarization logic
        # For now, we just return the text as is or truncated
        return text[:500] + "..."
