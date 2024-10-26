import selenium.webdriver as sl
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm


driver = sl.Chrome()




def scrape(link):
    driver.get(link)
    article = driver.find_element(By.TAG_NAME, 'article')

    paragraphs = article.find_elements(By.TAG_NAME, "p")
    lists = []
    children = article.find_elements(By.XPATH, "./*")
    for element in children:
        if element.tag_name == "ul":
            lists.append(element)
    with open('test.txt', 'a') as f:
        f.write("""\n""")
        for element in tqdm(paragraphs):
            f.write(element.text)
        f.write("""\n""")

        li = []

        for list in tqdm(lists):
            li = list.find_elements(By.TAG_NAME, "li")
            index = children.index(list)
            title = children[index-1].text
            if title.lower() == "read more:" or title.lower() == "table of contents":
                print("Hi")
                pass
            else:
                for text in li:
                    f.write(text.text)
        f.write("""\n""")
    print("All Done!")


links = [
    "https://byjus.com/chemistry/synthetic-fibre",
    "https://byjus.com/biology/crop-production-and-management/",
    "https://byjus.com/biology/microbiology/",
    "https://byjus.com/biology/coal-and-petroleum/",
    "https://byjus.com/chemistry/combustion-and-flames/",
    "https://byjus.com/biology/biodiversity-conservation/",
    "https://byjus.com/biology/reproduction-in-animals/",
    "https://byjus.com/biology/reaching-the-age-of-adolescence/",
    "https://byjus.com/physics/pressure/",
    "https://byjus.com/physics/force/",
    "https://byjus.com/physics/friction/",
    "https://byjus.com/free-ias-prep/sound/",
    "https://byjus.com/cbse-notes/cbse-class-9-science-notes-chapter-12-sound/",
    "https://byjus.com/physics/chemical-effects-of-electric-current/",
    "https://byjus.com/cbse-notes/cbse-class-8-science-notes-chapter-14-chemical-effects-of-electric-current/",
    "https://byjus.com/cbse-notes/cbse-class-8-science-notes-chapter-15-some-natural-phenomena/",
    "https://byjus.com/physics/light-sources/",
    "https://byjus.com/jee/properties-of-light/",
    "https://byjus.com/cbse-notes/cbse-class-10-science-notes-chapter-10-light-reflection-and-refraction/",
    "https://byjus.com/cbse-notes/cbse-class-8-science-notes-chapter-11-force-and-pressure/",
    "https://byjus.com/ncert-solutions-class-8-science/chapter-10-reaching-the-age-of-adolescence/",
    "https://byjus.com/cbse-notes/cbse-class-8-science-notes-chapter-5-coal-and-petroleum/",
    "https://byjus.com/cbse-notes/cbse-class-8-science-notes-chapter-7-conservation-of-plants-and-animals/"
    ]
for link in links:
    scrape(link)

driver.quit()
