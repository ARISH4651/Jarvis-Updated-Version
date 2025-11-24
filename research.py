from duckduckgo_search import DDGS
import re

class Researcher:
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query):
        """
        Intelligent search that interprets questions and provides structured answers.
        Uses search results to enhance explanations, not replace them.
        Enforces English-only results silently.
        """
        try:
            # Append 'english' to query to guide search engine
            search_query = f"{query} explanation english"
            
            # Perform search with US English region, fetch more to allow filtering
            results = list(self.ddgs.text(search_query, region='us-en', max_results=10))
            
            if not results:
                # Try again with original query
                results = list(self.ddgs.text(query, region='us-en', max_results=10))
            
            if not results:
                return {
                    "status": "error",
                    "message": "I couldn't find relevant information for that query at the moment."
                }
            
            # Filter for English content
            english_results = [r for r in results if self._is_english(r.get('body', '') + r.get('title', ''))]
            
            # If no English results, try to use the best available results anyway
            # but extract only English portions or provide a general answer
            if not english_results:
                # Fallback: Use original results but extract English text only
                english_results = self._extract_english_content(results[:3])
            
            if not english_results:
                # Last resort: provide a general answer based on the query
                return self._provide_general_answer(query)
            
            # Use top 3 English results
            final_results = english_results[:3]
            
            # Interpret and structure the answer
            answer = self._interpret_results(query, final_results)
            
            return {
                "status": "success",
                "message": answer,
                "sources": [{"title": r.get('title', 'Source'), "url": r.get('href', '#')} for r in final_results]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"I'm having trouble accessing that information right now. Could you rephrase your question?"
            }

    def _is_english(self, text):
        """
        Check if text is primarily English.
        Returns False if significant non-English characters (like CJK) are found.
        """
        if not text:
            return False
            
        # Check for CJK characters (Chinese, Japanese, Korean)
        if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text):
            return False
            
        # Check for Cyrillic
        if re.search(r'[\u0400-\u04ff]', text):
            return False
            
        return True
    
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
        """Format definition-style answers - clean and direct"""
        # Just provide the definition cleanly
        if snippets:
            definition = self._sanitize_text(snippets[0][:400])
            if definition:
                return definition
        
        return "I found some information but it wasn't clear enough to provide a good answer."
    
    def _format_howto(self, query, snippets, top_result):
        """Format how-to style answers - clean and direct"""
        combined_text = ' '.join(snippets)
        steps = re.findall(r'(\d+[\.\)]\s*[^\n]+)', combined_text)
        
        if steps:
            clean_steps = []
            for step in steps[:5]:
                clean_step = self._sanitize_text(step.strip())
                if clean_step:
                    clean_steps.append(clean_step)
            
            if clean_steps:
                return " ".join(clean_steps)
        
        # Fallback to general guidance
        guidance = self._sanitize_text(snippets[0][:400])
        if guidance:
            return guidance
        
        return "I found some information but couldn't extract clear steps."
    
    def _format_who(self, query, snippets, top_result):
        """Format who-is style answers - clean and direct"""
        main_content = self._sanitize_text(snippets[0][:400])
        
        if len(snippets) > 1:
            additional = self._sanitize_text(snippets[1][:200])
            if additional:
                main_content += " " + additional
        
        return main_content if main_content else "I found some information but it wasn't clear enough."
    
    def _format_why(self, query, snippets, top_result):
        """Format why-style answers - clean and direct"""
        explanation = self._sanitize_text(snippets[0][:400])
        
        # Add additional context if available
        if len(snippets) > 1:
            additional = self._sanitize_text(snippets[1][:200])
            if additional:
                explanation += " " + additional
        
        return explanation if explanation else "I found some information but couldn't extract a clear explanation."
    
    def _format_general(self, query, snippets, top_result):
        """Format general answers - clean and direct"""
        main_answer = self._sanitize_text(snippets[0][:400])
        
        if len(snippets) > 1:
            additional = self._sanitize_text(snippets[1][:250])
            if additional:
                main_answer += " " + additional
        
        return main_answer if main_answer else "I found some information but it wasn't clear enough to provide a good answer."

    def _extract_english_content(self, results):
        """
        Extract English portions from mixed-language results.
        Returns a list of results with only English text.
        """
        cleaned_results = []
        
        for result in results:
            # Try to extract English sentences from the body
            body = result.get('body', '')
            title = result.get('title', '')
            
            # Split into sentences and filter English ones
            sentences = body.split('.')
            english_sentences = [s.strip() for s in sentences if s.strip() and self._is_english(s)]
            
            if english_sentences or self._is_english(title):
                cleaned_result = result.copy()
                cleaned_result['body'] = '. '.join(english_sentences[:3]) + '.' if english_sentences else ''
                
                # Only add if we have meaningful English content
                if cleaned_result['body'] or self._is_english(title):
                    cleaned_results.append(cleaned_result)
        
        return cleaned_results

    def _provide_general_answer(self, query):
        """
        Provide a general, helpful answer when no English sources are available.
        """
        query_lower = query.lower()
        
        # Extract the main subject from the query
        subject = query_lower
        for prefix in ['what is', 'who is', 'how to', 'why', 'when', 'where']:
            subject = subject.replace(prefix, '').strip()
        
        # Provide a general response
        return {
            "status": "success",
            "message": f"I understand you're asking about {subject}. While I found some information, I recommend trying a more specific query or checking reliable sources like Wikipedia or educational websites for detailed information on this topic.",
            "sources": []
        }

    def _sanitize_text(self, text):
        """
        Remove all non-English characters from text.
        Keeps only: letters (a-z, A-Z), numbers (0-9), common punctuation, and spaces.
        """
        if not text:
            return ""
        
        # Remove all non-ASCII characters and non-English Unicode ranges
        # Keep only basic Latin alphabet, numbers, and common punctuation
        sanitized = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        # Remove any remaining problematic characters
        # This regex keeps: letters, numbers, spaces, and basic punctuation
        sanitized = re.sub(r'[^a-zA-Z0-9\s\.,!?\-:;\'"()\[\]{}/@#$%&*+=<>]', '', sanitized)
        
        # Clean up multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized

    def summarize(self, text):
        # Placeholder for a local LLM or summarization logic
        # For now, we just return the text as is or truncated
        return text[:500] + "..."
