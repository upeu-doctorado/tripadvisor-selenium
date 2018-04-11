# Programa que hace scripting a tripadvisor para comentarios de atractivos turisticos
#!/usr/bin/env python
# https://chromedriver.storage.googleapis.com/index.html?path=2.37/

import time
import json
import csv
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class Tripadvisor(object):

    def __init__(self, path_to_chromedriver):
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        self.browser = webdriver.Chrome(
            executable_path=path_to_chromedriver,
            chrome_options=chrome_options)
        self.browser.maximize_window()

    def get_coments(self, url):
        self.browser.get(url)
        self.data = []
        # Obtiene de la cabecera de los comentarios el numero total de opiniones
        all_coments = re.findall(
            r'\d+,\d+|\d+', self.browser.find_element_by_class_name('pagination-details').text)[-1]
        print('N° de comentarios: ', all_coments)
        self.__get_page_coments()

    def __get_page_coments(self):
        # Sirve para que haga click los "ver más" de los comentarios largos
        self.browser.execute_script(
            'Array.from(document.getElementsByClassName("ulBlueLinks")).forEach(function(item){item.click()});')
        time.sleep(1)# Necesario porque se demora actualizar el DOM
        reviews = self.browser.find_elements_by_class_name('review-container')
        for review in reviews:
            try:
                # print(self.browser.execute_script(
                #    'return arguments[0].querySelector(".noQuotes").textContent', review))
                self.data.append(dict(
                    rating=self.browser.execute_script(
                        'return arguments[0].querySelector(".reviewItemInline").childNodes[0].className', review)[-2:-1],
                    date=self.browser.execute_script(
                        'return arguments[0].querySelector(".reviewItemInline").childNodes[1].title', review),
                    coment_title=self.browser.execute_script(
                        'return arguments[0].querySelector(".noQuotes").textContent', review),
                    coment_description=self.browser.execute_script(
                        'return arguments[0].querySelector(".partial_entry").textContent', review)
                ))
            except Exception as e:
                print(e)
                time.sleep(3)
        # Para la paginacion
        has_next = self.browser.execute_script(
            'return !document.querySelector(".ui_pagination>.next").classList.contains("disabled")')
        print("Count: ", len(self.data))
        if has_next:
            self.browser.execute_script(
                'document.querySelector(".ui_pagination>.next").click()')
            time.sleep(0.5)
            self.__get_page_coments()

    def to_json(self, filename):
        with open(filename+'.json', 'w') as jsonfile:
            json.dump(self.data, jsonfile, ensure_ascii=False)

    def to_csv(self, filename):
        fieldnames = list(self.data[0].keys())
        try:
            with open(filename+'.csv', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for d in self.data:
                    writer.writerow(d)
        except IOError as e:
            print(e)

    def close(self):
        self.browser.quit()


if __name__ == "__main__":
    CRHOMEDRIVER_PATH = os.getcwd() + '\chromedriver'
    tripadvisor = Tripadvisor(CRHOMEDRIVER_PATH)
    atractions_urls = [
        ('LagoTiticaca', 'https://www.tripadvisor.com.pe/Attraction_Review-g298442-d311728'),
        
    ]
    for name, url in atractions_urls[:]:
        tripadvisor.get_coments(url)
        tripadvisor.to_csv('.\datasets')
    # tripadvisor.close()

# ,encoding='utf-8'
#('Silustani', 'https://www.tripadvisor.com.pe/Attraction_Review-g298442-d317514'),
#        ('IslaTaquile', 'https://www.tripadvisor.com.pe/Attraction_Review-g298442-d313934')