"""
Gemini 2.0 Flash client for vision analysis and text generation.
Updated to use the new google.genai package.
"""
import os
from typing import Optional, Dict, List
from google import genai
from google.genai import types
from PIL import Image

class GeminiClient:
    """Client for interacting with Gemini 2.0 Flash API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google AI API key (reads from GEMINI_API_KEY env var if not provided)
        """
        # Client reads from GEMINI_API_KEY environment variable if api_key not provided
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self.model_id = 'gemini-3-flash-preview'
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze machinery/equipment image and extract relevant information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Prompt for machinery analysis
            prompt = """Analyze this machinery/equipment image and provide:
1. Equipment type and model (if visible)
2. Visible components and parts
3. Any apparent issues, damage, or wear
4. Relevant technical details or markings

Be specific and technical. If you cannot identify something, say so.
Format your response clearly with numbered sections."""
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, img]
            )
            
            return {
                "success": True,
                "analysis": response.text,
                "image_path": image_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }

    def check_image_relevance(self, image_path: str) -> Dict:
        """
        Check if the image is relevant to machinery/equipment repair.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with is_relevant (bool) and reason (str)
        """
        try:
            img = Image.open(image_path)
            
            prompt = """Analyze this image and determine if it shows machinery, equipment, tools, or technical diagrams relevant to repair/maintenance.
Answer with a JSON object:
{
  "is_relevant": true/false,
  "reason": "Brief explanation why"
}
Only output the JSON."""
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, img],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            import json
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            # On error, default to allowing (fail open) or blocking (fail safe)
            # Here we'll fail open with a warning
            return {
                "is_relevant": True,
                "reason": f"Relevance check failed: {str(e)}"
            }
    
    def enhance_query(self, image_analysis: str, user_query: Optional[str] = None) -> str:
        """
        Convert image analysis to a search query for the vector database.
        
        Args:
            image_analysis: Text from image analysis
            user_query: Optional user-provided query
            
        Returns:
            Enhanced search query
        """
        try:
            prompt = f"""Based on this image analysis, create a concise search query to find relevant information in a repair manual.

Image Analysis:
{image_analysis}

User Query: {user_query if user_query else "General troubleshooting"}

Generate a focused search query (1-2 sentences) that would help find relevant manual sections.
Only output the search query, nothing else."""
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text.strip()
            
        except Exception as e:
            # Fallback to user query or generic query
            return user_query if user_query else "equipment troubleshooting and repair"
    
    def generate_answer(
        self,
        query: str,
        context: List[Dict],
        image_analysis: Optional[str] = None
    ) -> Dict:
        """
        Generate answer using RAG context.
        
        Args:
            query: User's question
            context: Retrieved context from vector DB
            image_analysis: Optional image analysis results
            
        Returns:
            Dictionary with answer and citations
        """
        try:
            # Format context
            context_text = self._format_context(context)
            
            # Build prompt
            prompt = f"""You are a technical support assistant for machinery repair.

User Question: {query}
"""
            
            if image_analysis:
                prompt += f"""
Image Analysis:
{image_analysis}
"""
            
            prompt += f"""
Relevant Manual Sections:
{context_text}

Instructions:
1. Answer the user's question based ONLY on the provided manual sections
2. Be specific and technical
3. Include step numbers, torque specifications, and safety warnings if present
4. Cite the page numbers you reference in [Page X] format
5. If the manual doesn't contain the answer, say so clearly

Answer:"""
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            # Extract citations
            citations = self._extract_citations(context)
            
            return {
                "success": True,
                "answer": response.text,
                "citations": citations,
                "context_used": len(context)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "I encountered an error generating the response."
            }
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format retrieved context for the prompt."""
        formatted = []
        for i, ctx in enumerate(context, 1):
            page = ctx.get('metadata', {}).get('page_label', 'Unknown')
            text = ctx.get('text', '')
            formatted.append(f"[Section {i} - Page {page}]\n{text}\n")
        return "\n".join(formatted)
    
    def _extract_citations(self, context: List[Dict]) -> List[Dict]:
        """Extract citation information from context."""
        citations = []
        for ctx in context:
            metadata = ctx.get('metadata', {})
            citations.append({
                'page': metadata.get('page_label', 'Unknown'),
                'file': metadata.get('file_name', 'Unknown'),
                'score': ctx.get('score', 0.0)
            })
        return citations
