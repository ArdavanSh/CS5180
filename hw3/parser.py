import pymongo
from bs4 import BeautifulSoup

def main():
    # Connect to MongoDB
    client = pymongo.MongoClient()
    db = client['CPP']
    pages_collection = db['pages']
    professors_collection = db['professors']

    # Find the page(s) with faculty information
    target_pages = pages_collection.find({'target': True})

    for page in target_pages:
        html_text = page['html']
        soup = BeautifulSoup(html_text, 'html.parser')

        # Find the main content area
        main_content = soup.find('div', {'id': 'main'})
        if not main_content:
            print('Main content section not found.')
            continue

        # Find all h2 tags within the main content
        h2_tags = main_content.find_all('h2')
        for h2_tag in h2_tags:
            name = h2_tag.get_text(strip=True)
            p_tag = h2_tag.find_next_sibling('p')
            if not p_tag:
                print(f'Info not found for {name}')
                continue
            # Initialize fields
            title = ''
            office = ''
            phone = ''
            email = ''
            website = ''

            current_field = None
            for elem in p_tag.children:
                if elem.name == 'strong':
                    field_name = elem.get_text(strip=True).replace(':', '').lower()
                    current_field = field_name
                elif isinstance(elem, str):
                    text = elem.strip()
                    if current_field == 'title':
                        title += text
                    elif current_field == 'office':
                        office += text
                    elif current_field == 'phone':
                        phone += text
                elif elem.name == 'a':
                    link_text = elem.get_text(strip=True)
                    link_href = elem.get('href', '').strip()
                    if current_field == 'email':
                        email = link_text
                    elif current_field in ['web', 'website']:
                        website = link_href
                elif elem.name == 'br':
                    current_field = None

            # Clean up whitespace
            title = title.strip()
            office = office.strip()
            phone = phone.strip()
            email = email.strip()
            website = website.strip()

            # Create a dictionary for the professor
            professor_data = {
                'name': name,
                'title': title,
                'office': office,
                'phone': phone,
                'email': email,
                'website': website
            }

            # Insert the professor data into MongoDB
            professors_collection.insert_one(professor_data)

    print('Faculty data parsed and stored in MongoDB.')

if __name__ == '__main__':
    main()
