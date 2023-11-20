from lxml import etree
import requests
import html

def test():
    response = requests.get("https://www.kapwing.com/642c11d0603909036b652b97/studio/editor")
    # print(response.text)
    object = etree.HTML(response.text)

    nodes = object.xpath("//main")

    # script_nodes = object.xpath("//script")
    # for node in script_nodes:
    #     print(node)
    #     node.getparent().remove(node)

    for node in nodes:
        # print(node)
        print(etree.tostring(node).decode("utf-8"))


def get_html_elements_for_llm():
    """Returns list of elements for use in GPT Index."""

    elements = []
    blacklisted_elements = ["head", "title", "meta", "script", "style", "path", "svg", "br", "::marker"]
    # blacklisted_attributes = set(["style", "ping", "src", "item*", "aria*", "js*", "data-*"])

    html = driver.find_element(By.TAG_NAME, "html")
    html_string = html.get_attribute("outerHTML")
    # soup = BeautifulSoup(html_string, "lxml")

    object = etree.HTML(html_string)
    nodes = object.xpath("//link")


    # blacklisted_nodes = [object.xpath(f"//{element}") for element in blacklisted_elements]
    # for node in blacklisted_nodes:
    #     node.getparent().remove(node)

    for node in nodes:
        element = etree.tostring(node).decode("utf-8")
        elements.append(element)

    '''
    for blacklisted in blacklisted_elements:
        for tag in soup.find_all(blacklisted):
            tag.decompose()

    for tag in soup.find_all(True):
        for attr in tag.attrs.copy():
            for pattern in blacklisted_attributes:
                if re.match(pattern, attr):
                    del tag[attr]

    elements = soup.find_all()
    [ele.clear() if ele.contents else ele for ele in elements if ele.contents]
    elements = [ele for ele in elements if ele.attrs]
    '''

    return elements
    

if __name__ == "__main__":
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.webdriver import WebDriver

    def get_xpath(driver: WebDriver, text: str) -> str:
        xpath = f'//*[contains(text(), "{text}")]'
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return xpath
        except:
            return None
