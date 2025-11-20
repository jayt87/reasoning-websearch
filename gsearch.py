def google_search(query: str, num_results: int = 5, max_chars: int = 150001) -> list:  # type: ignore[type-arg]
    import os
    import time

    import requests
    from bs4 import BeautifulSoup
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        raise ValueError("API key or Search Engine ID not found in environment variables")

    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {"key": str(api_key), "cx": str(search_engine_id), "q": str(query), "num": str(num_results)}
    
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.json())
        raise Exception(f"Error in API request: {response.status_code}")

    results = response.json().get("items", [])

    def get_page_content(url: str) -> str:
        try:
            response = requests.get(url, timeout=6)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            words = text.split()
            content = ""
            for word in words:
                if len(content) + len(word) + 1 > max_chars:
                    break
                content += " " + word
            return content.strip()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    enriched_results = []
    for item in results:
        try:
            body = get_page_content(item["link"])
            enriched_results.append(
                {"title": item["title"], "link": item["link"], "snippet": item["snippet"], "body": body}
            )
            time.sleep(0.01)  # Be respectful to the servers
        except Exception as e:
            print(f"Error processing item {item['link']}: {str(e)}")
            continue
    # Concatenate all results into a big string
    concatenated_text = ""
    for item in enriched_results:
        concatenated_text += f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item['snippet']}\nBody: {item['body']}\n\n"

    return concatenated_text