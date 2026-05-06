
import re
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote_plus, urljoin
import random
from typing import List, Dict, Tuple, Optional

class ContactFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Indian phone number patterns
        self.phone_patterns = [
            r'\+91[\s-]?[6-9]\d{9}',  # +91 format
            r'\b[6-9]\d{9}\b',        # 10-digit starting with 6-9
            r'\b0[6-9]\d{9}\b',       # 11-digit with leading 0
        ]

    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Indian phone numbers from text"""
        phones = []
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)

        # Clean and validate
        cleaned_phones = []
        for phone in phones:
            # Remove non-digits
            clean_phone = re.sub(r'[^\d]', '', phone)

            # Handle different formats
            if len(clean_phone) == 13 and clean_phone.startswith('91'):
                clean_phone = clean_phone[2:]
            elif len(clean_phone) == 11 and clean_phone.startswith('0'):
                clean_phone = clean_phone[1:]

            # Validate
            if len(clean_phone) == 10 and clean_phone[0] in '6789':
                # Check for repeated digits (likely invalid)
                if not (len(set(clean_phone)) <= 3):
                    cleaned_phones.append(clean_phone)

        return list(set(cleaned_phones))  # Remove duplicates

    def search_google(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search Google and return results"""
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            results = []
            for g in soup.find_all('div', class_='g')[:num_results]:
                title_elem = g.find('h3')
                link_elem = g.find('a')
                snippet_elem = g.find('span', class_=['st', 'aCOpRe'])

                if title_elem and link_elem:
                    title = title_elem.get_text()
                    link = link_elem.get('href', '')
                    snippet = snippet_elem.get_text() if snippet_elem else ''

                    if link.startswith('/url?q='):
                        link = link.split('/url?q=')[1].split('&')[0]

                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })

            return results
        except Exception as e:
            print(f"Google search error: {e}")
            return []

    def scrape_website(self, url: str) -> Tuple[str, str]:
        """Scrape website content and extract phone numbers"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            phones = self.extract_phone_numbers(text)

            # Determine confidence based on URL
            confidence = "High" if any(domain in url.lower() for domain in ['justdial', 'indiamart']) else "Medium"

            return phones, confidence
        except Exception as e:
            print(f"Website scraping error for {url}: {e}")
            return [], "Low"

    def generate_search_queries(self, company_name: str, director_name: str = None, cin: str = None) -> List[str]:
        """Generate multiple search queries"""
        queries = []

        if company_name:
            queries.extend([
                f'"{company_name}" phone number contact',
                f'"{company_name}" contact details',
                f'"{company_name}" office phone',
                f'"{company_name}" customer care number'
            ])

        if director_name:
            queries.extend([
                f'"{director_name}" "{company_name}" phone',
                f'"{director_name}" chartered accountant contact',
                f'"{director_name}" CA phone number'
            ])

        if cin:
            queries.extend([
                f'"{cin}" company contact details',
                f'"{cin}" phone number'
            ])

        return queries[:6]  # Limit to 6 queries

    def find_contact_for_company(self, company_name: str, director_name: str = None, cin: str = None) -> Dict:
        """Find contact for a single company"""
        print(f"Searching for: {company_name}")

        queries = self.generate_search_queries(company_name, director_name, cin)
        all_phones = []
        best_confidence = "Low"

        for query in queries:
            print(f"  Query: {query}")

            # Search Google
            search_results = self.search_google(query, 3)

            for result in search_results:
                # Extract phones from snippet
                snippet_phones = self.extract_phone_numbers(result['snippet'])
                if snippet_phones:
                    all_phones.extend([(phone, "Medium") for phone in snippet_phones])

                # Try to scrape the website
                if result['link'] and not any(skip in result['link'] for skip in ['youtube.com', 'facebook.com', 'linkedin.com']):
                    website_phones, confidence = self.scrape_website(result['link'])
                    if website_phones:
                        all_phones.extend([(phone, confidence) for phone in website_phones])
                        if confidence == "High":
                            best_confidence = "High"
                        elif confidence == "Medium" and best_confidence != "High":
                            best_confidence = "Medium"

            # Rate limiting
            time.sleep(random.uniform(2, 4))

        # Process results
        if all_phones:
            # Remove duplicates while preserving confidence
            phone_dict = {}
            for phone, conf in all_phones:
                if phone not in phone_dict or (conf == "High" and phone_dict[phone] != "High"):
                    phone_dict[phone] = conf

            # Return the first high-confidence number, or first medium, or first low
            for conf_level in ["High", "Medium", "Low"]:
                for phone, conf in phone_dict.items():
                    if conf == conf_level:
                        return {
                            'phone_number': phone,
                            'confidence': conf
                        }

        return {
            'phone_number': 'Not Available',
            'confidence': 'N/A'
        }

    def process_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process entire CSV file"""
        results = []

        for idx, row in df.iterrows():
            company_name = row.get('company_name', '').strip()
            director_name = row.get('director_name', '').strip() if 'director_name' in row else None
            cin = row.get('cin', '').strip() if 'cin' in row else None

            if not company_name:
                results.append({
                    'phone_number': 'Not Available',
                    'confidence': 'N/A'
                })
                continue

            try:
                result = self.find_contact_for_company(company_name, director_name, cin)
                results.append(result)
                print(f"  Result: {result['phone_number']} ({result['confidence']})")
            except Exception as e:
                print(f"Error processing {company_name}: {e}")
                results.append({
                    'phone_number': 'Not Available',
                    'confidence': 'N/A'
                })

            # Progress indicator
            print(f"Progress: {idx + 1}/{len(df)} completed\n")

        # Add results to dataframe
        result_df = df.copy()
        result_df['phone_number'] = [r['phone_number'] for r in results]
        result_df['confidence'] = [r['confidence'] for r in results]

        return result_df
