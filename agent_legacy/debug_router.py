import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_router(ip):
    url = f"http://{ip}/"
    logger.info(f"Connecting to {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {response.headers}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.info(f"Page Title: {soup.title.string if soup.title else 'No title'}")
        
        forms = soup.find_all('form')
        logger.info(f"Found {len(forms)} forms.")
        
        for i, form in enumerate(forms):
            logger.info(f"--- Form {i+1} ---")
            logger.info(f"Action: {form.get('action')}")
            logger.info(f"Method: {form.get('method')}")
            inputs = form.find_all('input')
            for inp in inputs:
                logger.info(f"Input: name={inp.get('name')}, type={inp.get('type')}, value={inp.get('value')}")
                
        # Check for specific TP-Link JS variables if forms are empty
        if not forms:
            logger.info("No forms found. Checking for JS based auth hints...")
            if "PCLogin" in response.text:
                logger.info("Found 'PCLogin' - possible TP-Link JS auth.")
            if "encrypt" in response.text.lower():
                 logger.info("Found 'encrypt' keyword - password likely hashed.")

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    inspect_router("192.168.100.1")
