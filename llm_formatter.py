"""
LLM-Friendly Output Formatter
Converts scraped content into formats optimized for Large Language Models
"""

import re
import json
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib

class LLMFormatter:
    """Formats scraped content for optimal LLM consumption"""
    
    def __init__(self):
        self.format_types = [
            'clean_text',      # Plain text with minimal formatting
            'structured_qa',   # Q&A format for training
            'markdown',        # Markdown with headers and lists
            'conversation',    # Dialog format
            'summary',         # Key points extraction
            'json_ld',        # Structured data extraction
            'narrative'       # Natural language description
        ]
    
    def format(self, html_content: str, format_type: str = 'clean_text', 
               metadata: Dict = None) -> str:
        """
        Format HTML content for LLM consumption
        
        Args:
            html_content: Raw HTML from scraper
            format_type: Output format type
            metadata: Additional context (URL, timestamp, etc.)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        if format_type == 'clean_text':
            return self._format_clean_text(soup, metadata)
        elif format_type == 'structured_qa':
            return self._format_qa(soup, metadata)
        elif format_type == 'markdown':
            return self._format_markdown(soup, metadata)
        elif format_type == 'conversation':
            return self._format_conversation(soup, metadata)
        elif format_type == 'summary':
            return self._format_summary(soup, metadata)
        elif format_type == 'json_ld':
            return self._format_json_ld(soup, metadata)
        elif format_type == 'narrative':
            return self._format_narrative(soup, metadata)
        else:
            return self._format_clean_text(soup, metadata)
    
    def _format_clean_text(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Clean, readable text format"""
        # Extract main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if not main_content:
            main_content = soup
        
        # Get text with proper spacing
        text = main_content.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Add metadata header
        output = []
        if metadata:
            output.append(f"Source: {metadata.get('url', 'Unknown')}")
            output.append(f"Accessed: {metadata.get('timestamp', datetime.now().isoformat())}")
            output.append("---\n")
        
        output.append(text)
        
        return '\n'.join(output)
    
    def _format_qa(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Question-Answer format for training"""
        output = []
        
        # Extract title as main question
        title = soup.find('title')
        if title:
            output.append(f"Q: What is this page about?")
            output.append(f"A: {title.get_text(strip=True)}\n")
        
        # Extract headings and their content as Q&A pairs
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text(strip=True)
            
            # Find content after heading
            content = []
            for sibling in heading.find_next_siblings():
                if sibling.name and sibling.name.startswith('h'):
                    break
                content.append(sibling.get_text(strip=True))
            
            if content:
                output.append(f"Q: {heading_text}")
                output.append(f"A: {' '.join(content[:3])}\n")  # Limit to first 3 paragraphs
        
        # Extract lists as Q&A
        for ul in soup.find_all('ul')[:5]:  # Limit to first 5 lists
            items = [li.get_text(strip=True) for li in ul.find_all('li')[:10]]
            if items:
                output.append(f"Q: What are the key points mentioned?")
                output.append(f"A: The key points are: {', '.join(items)}\n")
        
        return '\n'.join(output)
    
    def _format_markdown(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Markdown format with structure"""
        output = []
        
        # Add metadata as frontmatter
        if metadata:
            output.append("---")
            output.append(f"source: {metadata.get('url', 'Unknown')}")
            output.append(f"date: {metadata.get('timestamp', datetime.now().isoformat())}")
            output.append("---\n")
        
        # Convert HTML to Markdown
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote']):
            if element.name.startswith('h'):
                level = int(element.name[1])
                output.append(f"{'#' * level} {element.get_text(strip=True)}\n")
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    output.append(f"{text}\n")
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    prefix = '-' if element.name == 'ul' else '1.'
                    output.append(f"{prefix} {li.get_text(strip=True)}")
                output.append("")
            elif element.name == 'blockquote':
                output.append(f"> {element.get_text(strip=True)}\n")
        
        return '\n'.join(output)
    
    def _format_conversation(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Dialog/conversation format"""
        output = []
        
        output.append("System: I've analyzed the following webpage content.\n")
        
        if metadata and metadata.get('url'):
            output.append(f"User: What information is available at {metadata['url']}?\n")
        
        # Title as introduction
        title = soup.find('title')
        if title:
            output.append(f"Assistant: This page is about '{title.get_text(strip=True)}'.\n")
        
        # Main points as conversation
        headings = soup.find_all(['h1', 'h2', 'h3'])[:5]
        for i, heading in enumerate(headings):
            if i == 0:
                output.append("User: What are the main topics covered?\n")
                output.append(f"Assistant: The main topics include:\n")
            
            output.append(f"- {heading.get_text(strip=True)}")
            
            # Add some content
            next_p = heading.find_next_sibling('p')
            if next_p:
                output.append(f"  {next_p.get_text(strip=True)[:200]}...")
        
        output.append("\nUser: Is there any additional important information?")
        
        # Find important elements
        important = soup.find_all(['strong', 'em', 'mark'])[:5]
        if important:
            output.append("\nAssistant: Yes, the following points are emphasized:")
            for elem in important:
                output.append(f"- {elem.get_text(strip=True)}")
        
        return '\n'.join(output)
    
    def _format_summary(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Executive summary format"""
        output = []
        
        output.append("=== CONTENT SUMMARY ===\n")
        
        # URL and timestamp
        if metadata:
            output.append(f"SOURCE: {metadata.get('url', 'Unknown')}")
            output.append(f"DATE: {metadata.get('timestamp', datetime.now().isoformat())}\n")
        
        # Title
        title = soup.find('title')
        if title:
            output.append(f"TITLE: {title.get_text(strip=True)}\n")
        
        # Key sections
        output.append("KEY SECTIONS:")
        for heading in soup.find_all(['h1', 'h2'])[:5]:
            output.append(f"• {heading.get_text(strip=True)}")
        
        # Extract key facts (numbers, dates, names)
        output.append("\nKEY FACTS:")
        
        # Find sentences with numbers
        text = soup.get_text()
        sentences = text.split('.')
        facts = []
        
        for sentence in sentences[:50]:  # Check first 50 sentences
            # Look for numbers, percentages, dates
            if re.search(r'\d+%|\$\d+|\d{4}|\d+\.\d+', sentence):
                facts.append(sentence.strip())
        
        for fact in facts[:5]:
            output.append(f"• {fact}")
        
        # Important links
        links = soup.find_all('a', href=True)[:10]
        if links:
            output.append("\nIMPORTANT LINKS:")
            for link in links[:5]:
                if link.get_text(strip=True):
                    output.append(f"• {link.get_text(strip=True)}: {link['href']}")
        
        return '\n'.join(output)
    
    def _format_json_ld(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Extract and format structured data"""
        output = {
            'metadata': metadata or {},
            'structured_data': {},
            'content': {}
        }
        
        # Extract JSON-LD data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                output['structured_data'].update(data)
            except:
                pass
        
        # Extract OpenGraph data
        og_data = {}
        for meta in soup.find_all('meta', property=True):
            if meta['property'].startswith('og:'):
                og_data[meta['property']] = meta.get('content', '')
        output['structured_data']['opengraph'] = og_data
        
        # Extract main content
        output['content'] = {
            'title': soup.find('title').get_text(strip=True) if soup.find('title') else None,
            'headings': [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])[:10]],
            'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')[:10]],
            'lists': [[li.get_text(strip=True) for li in ul.find_all('li')] 
                     for ul in soup.find_all('ul')[:5]]
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _format_narrative(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Natural language narrative description"""
        output = []
        
        # Start with context
        if metadata and metadata.get('url'):
            domain = metadata['url'].split('/')[2] if '/' in metadata['url'] else metadata['url']
            output.append(f"I found the following information on {domain}:")
        
        # Title introduction
        title = soup.find('title')
        if title:
            output.append(f"\nThe page is titled '{title.get_text(strip=True)}' and contains detailed information about this topic.")
        
        # Main content narrative
        main_headings = soup.find_all(['h1', 'h2'])[:3]
        if main_headings:
            output.append(f"\nThe content is organized into {len(main_headings)} main sections:")
            
            for i, heading in enumerate(main_headings, 1):
                heading_text = heading.get_text(strip=True)
                output.append(f"\n{i}. {heading_text}")
                
                # Add narrative about the section
                paragraphs = []
                for sibling in heading.find_next_siblings():
                    if sibling.name == 'p':
                        paragraphs.append(sibling.get_text(strip=True))
                    if sibling.name and sibling.name.startswith('h'):
                        break
                    if len(paragraphs) >= 2:
                        break
                
                if paragraphs:
                    output.append(f"   This section explains that {paragraphs[0][:200]}...")
        
        # Mention lists and important points
        lists = soup.find_all('ul')[:2]
        if lists:
            total_items = sum(len(ul.find_all('li')) for ul in lists)
            output.append(f"\nThe page also includes {total_items} key points organized in lists, covering important details and specifications.")
        
        # Conclusion
        output.append("\nThis information appears to be comprehensive and well-structured for understanding the topic.")
        
        return '\n'.join(output)
    
    def batch_format(self, contents: List[Dict], format_type: str = 'clean_text') -> List[str]:
        """Format multiple pieces of content"""
        formatted = []
        for content in contents:
            html = content.get('html', '')
            metadata = content.get('metadata', {})
            formatted.append(self.format(html, format_type, metadata))
        return formatted
    
    def optimal_format_for_task(self, task_type: str) -> str:
        """Recommend optimal format for specific LLM tasks"""
        task_formats = {
            'summarization': 'summary',
            'qa_training': 'structured_qa',
            'content_analysis': 'markdown',
            'information_extraction': 'json_ld',
            'conversation_training': 'conversation',
            'text_generation': 'narrative',
            'classification': 'clean_text'
        }
        return task_formats.get(task_type, 'clean_text')

# Singleton instance
llm_formatter = LLMFormatter()