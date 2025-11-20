import os
from groq import Groq

class LLMProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GROQ_API')
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
    
    def summarize_article(self, article):
        """Summarize an article using Groq"""
        prompt = f"""
        You're a senior tech journalist writing for a major publication. Craft a compelling summary of this AI article.

        STORY: {article['title']}
        DETAILS: {article['summary'][:1000]}

        Write your summary as:

        📰 LEAD PARAGRAPH:
        [Engaging opening that summarizes the main story]

        🔍 KEY INSIGHTS:
        • [Insight 1]
        • [Insight 2]
        • [Insight 3]

        💡 THE BIG PICTURE:
        [Why this matters in the broader AI landscape]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Summary not available: {e}"
    
    def classify_topic(self, article):
        """Classify the article by AI theme"""
        topics = ["ML Research", "AI Ethics", "Industry News", "Tools & Frameworks", "Startups"]
        return topics[0]  # Temporary