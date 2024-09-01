import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to get the HTML content from a URL
def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None

# Function to parse and extract data from a single page
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    entries = soup.find_all('div', class_='seasonal-anime')  # Adjust this class if needed
    
    page_data = []
    for entry in entries:
        title_tag = entry.find('a', class_='link-title')
        title = title_tag.text.strip() if title_tag else "Unknown Title"
        
        genres = [genre.text for genre in entry.find_all('span', class_='genre')]
        description_tag = entry.find('p', class_='preline')
        description = description_tag.text.strip() if description_tag else "No description available."
        
        page_data.append({
            'title': title,
            'genres': ', '.join(genres),
            'description': description,
        })

    return page_data

# Function to scrape each genre page by page
def scrape_genre(start_url, genre_id, category="Unknown"):
    data = []
    page_number = 1
    
    while True:
        url = f"{start_url}/{genre_id}?page={page_number}"
        print(f"Scraping URL: {url}")
        html = get_html(url)
        
        if html:
            page_data = parse_page(html)
            if not page_data:
                print(f"No more data to scrape for {category}, genre {genre_id} at page {page_number}")
                break

            # Print the first title of the batch
            if page_data:
                print(f"First title scraped in this batch: {page_data[0]['title']}")
            
            data.extend(page_data)
            print(f"Scraped {len(page_data)} unique entries, page: {page_number}")
        else:
            print(f"Failed to retrieve data at page {page_number}. Stopping scraping for {category}, genre {genre_id}.")
            break
        
        page_number += 1  # Move to the next page
        time.sleep(2)  # Sleep to avoid hitting the server too hard

    return data

def main():
    base_url_anime = "https://myanimelist.net/anime/genre"
    base_url_manga = "https://myanimelist.net/manga/genre"
    
    # First cycle through all genres for anime and save to CSV
    all_anime_data = []
    for genre_id in range(1, 46):
        anime_data = scrape_genre(base_url_anime, genre_id, category="anime")
        for entry in anime_data:
            entry['category'] = "anime"
            entry['genre_id'] = genre_id
        all_anime_data.extend(anime_data)

    # Save anime data to CSV
    anime_df = pd.DataFrame(all_anime_data)
    anime_df.to_csv('anime_data.csv', index=False)
    print("Anime data saved to anime_data.csv")

    # Then cycle through all genres for manga and save to CSV
    all_manga_data = []
    for genre_id in range(1, 46):
        manga_data = scrape_genre(base_url_manga, genre_id, category="manga")
        for entry in manga_data:
            entry['category'] = "manga"
            entry['genre_id'] = genre_id
        all_manga_data.extend(manga_data)

    # Save manga data to CSV
    manga_df = pd.DataFrame(all_manga_data)
    manga_df.to_csv('manga_data.csv', index=False)
    print("Manga data saved to manga_data.csv")

if __name__ == "__main__":
    main()
