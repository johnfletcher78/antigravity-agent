"""
Web Scraping Service
Allows NAT to fetch and analyze website content
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

class WebScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_url(self, url: str, max_length: int = 5000):
        """
        Fetch and parse content from a URL
        
        Args:
            url: The URL to fetch
            max_length: Maximum content length to return (default 5000 chars)
        
        Returns:
            dict with url, title, content, and meta information
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {"error": "Invalid URL format"}
            
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else "No title"
            
            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag['content']
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            # Extract main headings
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3'], limit=10):
                heading_text = h.get_text().strip()
                if heading_text:
                    headings.append(heading_text)
            
            # Extract links
            links = []
            base_domain = parsed.netloc
            for link in soup.find_all('a', href=True, limit=50):
                href = link.get('href')
                link_text = link.get_text().strip()
                
                # Parse the link
                if href.startswith('http'):
                    link_url = href
                elif href.startswith('/'):
                    link_url = f"{parsed.scheme}://{parsed.netloc}{href}"
                else:
                    continue
                
                # Categorize as internal or external
                link_domain = urlparse(link_url).netloc
                is_internal = link_domain == base_domain
                
                if link_text and len(link_text) < 100:
                    links.append({
                        'url': link_url,
                        'text': link_text,
                        'type': 'internal' if is_internal else 'external'
                    })
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "meta_description": meta_desc,
                "headings": headings,
                "links": links,
                "content": text,
                "content_length": len(text)
            }
            
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}
        except Exception as e:
            return {"error": f"Error parsing content: {str(e)}"}
    
    def analyze_seo(self, url: str):
        """
        Analyze basic SEO elements of a webpage
        
        Args:
            url: The URL to analyze
        
        Returns:
            dict with SEO analysis
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                "success": True,
                "url": url,
                "seo_elements": {}
            }
            
            # Title tag
            title = soup.find('title')
            analysis["seo_elements"]["title"] = {
                "present": bool(title),
                "content": title.string if title else None,
                "length": len(title.string) if title else 0,
                "optimal": 50 <= len(title.string) <= 60 if title else False
            }
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            desc_content = meta_desc.get('content') if meta_desc else None
            analysis["seo_elements"]["meta_description"] = {
                "present": bool(meta_desc),
                "content": desc_content,
                "length": len(desc_content) if desc_content else 0,
                "optimal": 150 <= len(desc_content) <= 160 if desc_content else False
            }
            
            # H1 tags
            h1_tags = soup.find_all('h1')
            analysis["seo_elements"]["h1_tags"] = {
                "count": len(h1_tags),
                "content": [h1.get_text().strip() for h1 in h1_tags],
                "optimal": len(h1_tags) == 1
            }
            
            # Images without alt text
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            analysis["seo_elements"]["images"] = {
                "total": len(images),
                "without_alt": len(images_without_alt),
                "alt_text_coverage": f"{((len(images) - len(images_without_alt)) / len(images) * 100):.1f}%" if images else "N/A"
            }
            
            # Check for canonical tag
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            analysis["seo_elements"]["canonical"] = {
                "present": bool(canonical),
                "url": canonical.get('href') if canonical else None
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"SEO analysis failed: {str(e)}"}
