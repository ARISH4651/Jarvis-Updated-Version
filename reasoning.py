"""
Reasoning Engine for JARVIS
Provides intelligent interpretation and context-aware responses without requiring web search.
"""

class ReasoningEngine:
    def __init__(self):
        self.knowledge_base = {
            # AI & Machine Learning
            "ai": "Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation. AI systems learn from experience, adjust to new inputs, and perform human-like tasks.",
            "artificial intelligence": "Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation. AI systems learn from experience, adjust to new inputs, and perform human-like tasks.",
            "machine learning": "Machine Learning is a subset of AI where systems learn from data and improve their performance over time without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions based on those patterns.",
            "deep learning": "Deep Learning is a subset of machine learning using neural networks with multiple layers (deep neural networks) to learn hierarchical representations of data. It's particularly effective for image recognition, natural language processing, and complex pattern recognition.",
            "neural network": "A neural network is a computing system inspired by biological neural networks, consisting of interconnected nodes (neurons) organized in layers. Each connection has a weight that adjusts as learning proceeds, allowing the network to recognize patterns and make predictions.",
            
            # Programming Languages
            "python": "Python is a high-level, interpreted programming language known for its simplicity, readability, and versatility. Created by Guido van Rossum in 1991, it's widely used in data science, web development, automation, artificial intelligence, and scientific computing.",
            "javascript": "JavaScript is a high-level, interpreted programming language primarily used for web development to create interactive and dynamic web pages. It runs in web browsers and can also be used on servers through Node.js.",
            "java": "Java is a class-based, object-oriented programming language designed to have minimal implementation dependencies. It follows the principle of 'write once, run anywhere' (WORA), meaning compiled Java code can run on any platform that supports Java.",
            
            # Web & APIs
            "api": "An API (Application Programming Interface) is a set of rules, protocols, and tools that allows different software applications to communicate with each other. It defines the methods and data formats that applications can use to request and exchange information.",
            "rest api": "REST (Representational State Transfer) API is an architectural style for designing networked applications. It uses HTTP requests to access and manipulate data, typically using GET, POST, PUT, and DELETE operations.",
            
            # Data & Databases
            "database": "A database is an organized collection of structured data stored electronically in a computer system. It's typically controlled by a database management system (DBMS) that allows users to create, read, update, and delete data efficiently.",
            "sql": "SQL (Structured Query Language) is a standardized programming language used for managing and manipulating relational databases. It's used to perform tasks such as querying data, updating records, and creating database structures.",
            
            # Cloud & Infrastructure
            "cloud computing": "Cloud computing delivers computing services (servers, storage, databases, networking, software) over the internet ('the cloud'), allowing flexible resources, faster innovation, and economies of scale. Users typically pay only for the cloud services they use.",
            
            # Data Science
            "data science": "Data Science is an interdisciplinary field that combines statistics, programming, and domain expertise to extract insights and knowledge from structured and unstructured data. It involves data collection, cleaning, analysis, visualization, and interpretation.",
            
            # Programming Concepts
            "algorithm": "An algorithm is a step-by-step procedure or formula for solving a problem or completing a task. It's a finite sequence of well-defined instructions that can be implemented in code to achieve a specific outcome.",
            "function": "A function is a reusable block of code that performs a specific task. It can accept inputs (parameters), process them, and return outputs. Functions help organize code, reduce repetition, and improve maintainability.",
            "variable": "A variable is a named storage location in computer memory that holds a value which can change during program execution. It has a name, a data type, and a value that can be read or modified.",
            "loop": "A loop is a programming construct that repeats a block of code multiple times until a specified condition is met. Common types include for loops, while loops, and do-while loops.",
            
            # System Components
            "cpu": "The CPU (Central Processing Unit) is the primary component of a computer that executes instructions and performs calculations. Often called the 'brain' of the computer, it processes data and controls other hardware components.",
            "ram": "RAM (Random Access Memory) is volatile memory that temporarily stores data and programs currently being used by the computer. It provides fast read and write access, but loses its contents when power is turned off.",
            "gpu": "The GPU (Graphics Processing Unit) is a specialized processor originally designed for rendering graphics. Modern GPUs are also used for parallel computations in AI, scientific simulations, and cryptocurrency mining due to their ability to process many operations simultaneously.",
            
            # Science & Mathematics
            "physics": "Physics is the natural science that studies matter, energy, and the fundamental forces of nature. It seeks to understand how the universe behaves through observation, experimentation, and mathematical analysis. Major branches include mechanics, thermodynamics, electromagnetism, and quantum physics.",
            "chemistry": "Chemistry is the scientific study of matter, its properties, composition, structure, and the changes it undergoes during chemical reactions. It explores how substances interact, combine, and transform at the molecular and atomic level.",
            "biology": "Biology is the scientific study of life and living organisms, including their structure, function, growth, evolution, distribution, and taxonomy. It encompasses diverse fields from molecular biology to ecology.",
            "mathematics": "Mathematics is the abstract science of numbers, quantity, structure, space, and change. It uses logic and symbolic notation to study patterns, relationships, and properties through rigorous proof and reasoning.",
        }
        
        self.context_memory = {}
    
    def can_answer_directly(self, query):
        """
        Determine if the query can be answered through reasoning without web search.
        """
        query_lower = query.lower()
        
        # Check if it's a simple definition in our knowledge base
        for term, definition in self.knowledge_base.items():
            if term in query_lower:
                return True
        
        # Check if it's a reasoning/logic question
        reasoning_indicators = [
            "why would", "how does", "explain the difference",
            "what happens if", "what's the relationship",
            "compare", "contrast", "pros and cons"
        ]
        
        if any(indicator in query_lower for indicator in reasoning_indicators):
            return True
        
        # Questions that require current/specific information need search
        current_info_indicators = [
            "latest", "current", "today", "now", "recent",
            "who is the president", "what is the weather",
            "stock price", "news about"
        ]
        
        if any(indicator in query_lower for indicator in current_info_indicators):
            return False
        
        return False
    
    def answer(self, query, context=None):
        """
        Provide a reasoned answer to the query.
        Returns clean, complete answers without source labels.
        """
        query_lower = query.lower()
        
        # Check knowledge base first
        for term, definition in self.knowledge_base.items():
            if term in query_lower:
                # Return clean answer without source labels
                return {
                    "status": "success",
                    "message": definition,
                    "source": "reasoning"
                }
        
        # Handle comparison questions
        if "difference between" in query_lower or "compare" in query_lower:
            result = self._handle_comparison(query_lower)
            if result['status'] == 'success':
                return result
        
        # Handle "how does" questions
        if "how does" in query_lower or "how do" in query_lower:
            result = self._handle_how_question(query_lower)
            if result['status'] == 'success':
                return result
        
        # Handle "why" questions with general reasoning
        if query_lower.startswith("why"):
            result = self._handle_why_question(query_lower)
            if result['status'] == 'success':
                return result
        
        # If we can't answer directly, indicate search is needed
        return {
            "status": "needs_search",
            "message": "I need to research that for you."
        }
    
    def _handle_comparison(self, query):
        """Handle comparison questions with clean, direct answers."""
        comparisons = {
            ("python", "javascript"): "Python is primarily used for backend development, data science, and automation with simpler syntax. JavaScript is mainly used for frontend web development and runs in browsers, though it can also run on servers via Node.js. Python is interpreted and emphasizes readability, while JavaScript is event-driven and asynchronous.",
            ("machine learning", "deep learning"): "Machine Learning is a broader field that includes various algorithms for learning from data, such as decision trees, random forests, and support vector machines. Deep Learning is a specialized subset that uses neural networks with multiple layers to automatically learn complex patterns, particularly effective for image recognition and natural language processing.",
            ("cpu", "gpu"): "CPUs have fewer, more powerful cores optimized for sequential processing and general-purpose computing. GPUs have thousands of smaller cores designed for parallel processing, making them ideal for graphics rendering, AI training, and scientific computations that can be parallelized.",
            ("ai", "machine learning"): "Artificial Intelligence is the broader concept of machines being able to carry out tasks in a smart way. Machine Learning is a specific subset of AI that focuses on the idea that machines can learn from data and improve from experience without being explicitly programmed for every scenario.",
        }
        
        for (term1, term2), explanation in comparisons.items():
            if term1 in query and term2 in query:
                return {
                    "status": "success",
                    "message": explanation,
                    "source": "reasoning"
                }
        
        return {"status": "needs_search", "message": "I need more information to compare those."}
    
    def _handle_how_question(self, query):
        """Handle 'how does' questions with clear explanations."""
        if "work" in query:
            if "neural network" in query or "ai" in query:
                return {
                    "status": "success",
                    "message": "Neural networks work by mimicking how the human brain processes information. They consist of layers of interconnected nodes (neurons). The input layer receives data, hidden layers process it through weighted connections, and the output layer produces predictions. During training, the network adjusts these weights through backpropagation, learning to recognize patterns by minimizing errors between predictions and actual results. This allows them to learn complex relationships in data for tasks like image recognition and language processing.",
                    "source": "reasoning"
                }
            elif "machine learning" in query:
                return {
                    "status": "success",
                    "message": "Machine learning works by training algorithms on data to recognize patterns and make predictions. The process involves: 1) Collecting and preparing training data, 2) Choosing an appropriate algorithm, 3) Training the model by feeding it data and adjusting parameters to minimize errors, 4) Validating the model on new data, and 5) Using the trained model to make predictions on unseen data. The system improves its performance over time as it processes more examples.",
                    "source": "reasoning"
                }
        
        return {"status": "needs_search", "message": "I need to research that mechanism."}
    
    def _handle_why_question(self, query):
        """Handle 'why' questions that can be reasoned about."""
        # Add common why questions here
        if "python" in query and "popular" in query:
            return {
                "status": "success",
                "message": "Python is popular because of its simple, readable syntax that resembles natural language, making it easy to learn for beginners. It has extensive libraries for data science, web development, and automation. The language is versatile, working across different platforms, and has strong community support with abundant resources and documentation. Its interpreted nature allows for rapid development and testing.",
                "source": "reasoning"
            }
        
        return {"status": "needs_search", "message": "I need to research that reason."}
    
    def set_context(self, key, value):
        """Store context for follow-up questions."""
        self.context_memory[key] = value
    
    def get_context(self, key):
        """Retrieve context."""
        return self.context_memory.get(key)
