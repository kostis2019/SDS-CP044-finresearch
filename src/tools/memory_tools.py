from langchain.tools import tool
from crewai.tools import tool
from .memory_store import FinancialMemory

# Initialize the memory instance globally so all tools share it
memory_db = FinancialMemory()

class MemoryTools:
    
    @tool("Save Finding to Memory")
    def save_finding(content: str, source: str):
        """
        Useful for the Researcher Agent. 
        Use this tool to save important financial facts, news, or data snippets 
        into the shared memory for other agents to use later.
        Args:
            content: The fact or text to remember.
            source: Where it came from (e.g. 'Yahoo Finance', 'News Article').
        """       

        # We define a metadata dictionary
        meta = {"source": source}
        memory_db.save_context(content, meta)
        return "Finding successfully saved to long-term memory."

    @tool("Query Shared Memory")
    def search_memory(query: str):
        """
        Useful for the Analyst or Reporter Agent.
        Use this tool to search the shared database for previously found facts 
        about a company or topic.
        Args:
            query: The topic you are looking for (e.g. 'Tesla Q3 earnings').
        """      

        results = memory_db.query_memory(query)
        if not results:
            return "No relevant information found in memory."
        return f"Here is what I found in memory:\n{results}"