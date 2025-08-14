import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_static_content(url, proxy=None):
    """
    Scrape static content from a URL using requests and BeautifulSoup
    """
    try:
        # Configure proxy if provided
        proxies = None
        if proxy:
            # Handle both string and dict proxy formats
            if isinstance(proxy, dict) and 'http' in proxy:
                proxies = proxy
            elif isinstance(proxy, str):
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            elif isinstance(proxy, dict) and 'url' in proxy:
                proxies = {
                    'http': proxy['url'],
                    'https': proxy['url']
                }
        
        # Make request with headers to avoid basic bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def scrape_dynamic_content(url, proxy=None):
    """
    Scrape dynamic content from a URL using Selenium
    """
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy if provided
        # Note: Selenium doesn't natively support authenticated proxies
        # For now, we'll skip proxy for dynamic scraping
        # A full implementation would require a proxy authentication extension
        if proxy:
            print("Note: Proxy authentication not supported in dynamic mode without extension")
        
        # Initialize driver with automatic ChromeDriver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to URL
        driver.get(url)
        
        # Wait for page to load (adjust timeout as needed)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Additional wait for JavaScript to complete
        time.sleep(2)
        
        # Get page source
        page_source = driver.page_source
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Close driver
        driver.quit()
        
        return text
        
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"