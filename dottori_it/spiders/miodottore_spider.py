import json
import scrapy
import re
import csv
import os.path
from scrapy_selenium import SeleniumRequest


class MiodottoreSpider(scrapy.Spider):
    name = 'dottori'
    title = 'dottori it'
    base_url = 'https://www.dottori.it'
    start_urls = [
        'https://www.dottori.it/psicologo'
    ]
    count = 0
    count_links = 0

    @classmethod
    def clean_data(cls, data):
        if data and isinstance(data, str):
            data = data.encode('ascii', 'ignore').decode()
        return data

    @classmethod
    def get_index(cls, lst, index, default=''):
        """
        return element on given index from list
        :param lst: list from which we will return element
        :param index: index of element
        :param default: return value if index out of range
        :return:
        """
        return cls.clean_data(lst[index]) if isinstance(lst, list) and len(lst) > index else default

    def get_dict_value(self, data, key_list, default=''):
        """
        gets a dictionary and key_list, apply key_list sequentially on dictionary and return value
        :param data: dictionary
        :param key_list: list of key
        :param default: return value if key not found
        :return:
        """
        for key in key_list:
            if data and isinstance(data, dict):
                data = data.get(key, default)
            elif data and isinstance(data, list):
                data = self.get_index(data, key) if isinstance(key, int) else default
            else:
                return default
        return self.clean_data(data)

    def parse(self, response):
        profile_links = response.css(".gtDoctorNameMedCen::attr(href)").extract()
        for each_link in profile_links:
            yield response.follow(each_link, callback=self.parse_profile)
        next_page = self.get_index(response.css(".doc-page-item"), -1).css("a::attr(href)").extract_first()
        if next_page is not None:
            self.count_links = self.count_links + 1
            print(self.count_links)
            yield SeleniumRequest(url='{}{}'.format(self.base_url, next_page), callback=self.parse, wait_time=3)

    def parse_profile(self, response):
        if response.status != 200:
            print(response.url)
            return
        item = dict()
        item['sequential_id'] = self.count
        item['global_id'] = None
        item['source'] = 'https://www.dottori.it'
        item['scrape_URL'] = response.url
        item['is_therapist'] = None
        item['title'] = response.css(".doc-title-label::text").extract_first()
        item["name"] = response.css('h1[itemprop="name"]::text').extract_first()
        item["is_verified"] = True if response.css(".icon-check") else False
        if response.css('a[href="#view-feedback"]'):
            item['review_number'] = self.get_index(
                re.findall("[0-9]+", response.css('a[href="#view-feedback"]::text').extract_first()), 0)
        else:
            item['review_number'] = None
        positive_review_number = 0
        reviews_number_2021 = 0
        positive_review_number_2021 = 0
        reviews_number_2020 = 0
        positive_review_number_2020 = 0
        reviews_number_2019 = 0
        positive_review_number_2019 = 0
        reviews_number_2018 = 0
        positive_review_number_2018 = 0
        for each_review in response.css(".doc-modal-body #view-feedback .doc-comments-grid .doc-bubble-comment"):
            if each_review.css(".icon-like"):
                positive_review_number += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '20':
                    reviews_number_2020 += 1
            if each_review.css("header span+span.icon-unlike"):
                if each_review.css("header+p span::text").extract_first().split("/")[-1].strip() == '20':
                    reviews_number_2020 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '20':
                    positive_review_number_2020 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '19':
                    reviews_number_2019 += 1
            if each_review.css("header span+span.icon-unlike"):
                if each_review.css("header+p span::text").extract_first().split("/")[-1].strip() == '19':
                    reviews_number_2019 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '19':
                    positive_review_number_2019 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '18':
                    reviews_number_2018 += 1
            if each_review.css("header span+span.icon-unlike"):
                if each_review.css("header+p span::text").extract_first().split("/")[-1].strip() == '18':
                    reviews_number_2018 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '18':
                    positive_review_number_2018 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '21':
                    reviews_number_2021 += 1
            if each_review.css("header span+span.icon-unlike"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1] == '21':
                    reviews_number_2021 += 1
            if each_review.css("header span+span.icon-like"):
                if each_review.css(".mb-2 .doc-comment-head::text").extract_first().split("/")[-1].strip() == '21':
                    positive_review_number_2021 += 1

        item['positive_review_number'] = positive_review_number
        item['reviews_number_2021'] = reviews_number_2021
        item['reviews_number_2020'] = reviews_number_2020
        item['reviews_number_2019'] = reviews_number_2019
        item['reviews_number_2018'] = reviews_number_2018
        item['positive_review_number_2021'] = positive_review_number_2021
        item['positive_review_number_2020'] = positive_review_number_2020
        item['positive_review_number_2019'] = positive_review_number_2019
        item['positive_review_number_2018'] = positive_review_number_2018
        item["address_1"] = None
        item["city_1"] = None
        item['latitude_1'] = None
        item['longitude_1'] = None
        item["label_1"] = None
        item["address_2"] = None
        item["city_2"] = None
        item['latitude_2'] = None
        item['longitude_2'] = None
        item["label_2"] = None
        item["address_3"] = None
        item["city_3"] = None
        item['latitude_3'] = None
        item['longitude_3'] = None
        item["label_3"] = None
        item["address_4"] = None
        item["city_4"] = None
        item['latitude_4'] = None
        item['longitude_4'] = None
        item["label_4"] = None
        response.css("div[data-medical-centers]::attr(data-medical-centers)").extract_first()
        data = response.css("div[data-medical-centers]::attr(data-medical-centers)").extract_first()
        addrees_json = response.css('script[type="application/ld+json"]::text').extract_first()
        try:
            json_data = json.loads(addrees_json)
        except:
            print("json parsing error")
        for index, each_address in enumerate(json_data.get("hasPOS")):

            if index == 0:
                item["address_1"] = each_address.get("geo").get("address").get("streetAddress")
                item["city_1"] = each_address.get("geo").get("address").get("addressLocality")
                item['latitude_1'] = each_address.get("geo").get('latitude')
                item['longitude_1'] = each_address.get("geo").get('longitude')
                item["label_1"] = each_address.get('name')
            if index == 1:
                item["address_2"] = each_address.get("geo").get("address").get("streetAddress")
                item["city_2"] = each_address.get("geo").get("address").get("addressLocality")
                item['latitude_2'] = each_address.get("geo").get('latitude')
                item['longitude_2'] = each_address.get("geo").get('longitude')
                item["label_2"] = each_address.get('name')
            if index == 2:
                item["address_3"] = each_address.get("geo").get("address").get("streetAddress")
                item["city_3"] = each_address.get("geo").get("address").get("addressLocality")
                item['latitude_3'] = each_address.get("geo").get('latitude')
                item['longitude_3'] = each_address.get("geo").get('longitude')
                item["label_3"] = each_address.get('name')
            if index == 3:
                item["address_4"] = each_address.get("geo").get("address").get("streetAddress")
                item["city_4"] = each_address.get("geo").get("address").get("addressLocality")
                item['latitude_4'] = each_address.get("geo").get('latitude')
                item['longitude_4'] = each_address.get("geo").get('longitude')
                item["label_4"] = each_address.get('name')

        item["works_online"] = True if response.css(".doc-card__mode-label--video") else False
        online_price_list = []
        offline_price_list = []
        if response.css("#tariffe #profile-health-service-preview"):
            for each_price in response.css("#tariffe #profile-health-service-preview p"):
                matches_offline = ["online", "gruppo", "gruppi", "coppia", "coppie", "skype", "whatsapp", "internet",
                                   "video"]
                matches_online = ["online", "skype", "whatsapp", "internet", "video"]
                if any(x in each_price.css("::text").extract_first() for x in matches_online):
                    if each_price.css(".font-weight-normal::text").extract_first():
                        if "da €" in each_price.css(".font-weight-normal::text").extract_first():
                            price_range = re.findall("[0-9]+\.[0-9]+|[0-9]+",
                                                     each_price.css(".font-weight-normal::text").extract_first())
                            online_price_list.append(int(self.get_index(price_range, 0).replace(".", "")))
                        elif re.search("[0-9]+\.[0-9]+", each_price.css(".font-weight-normal::text").extract_first()):
                            online_price_list.append(int(self.get_index(re.findall("[0-9]+", each_price.css(
                                ".font-weight-normal::text").extract_first().replace(".", "")), 0)))
                        else:
                            online_price_list.append(int(self.get_index(
                                re.findall("[0-9]+", each_price.css(".font-weight-normal::text").extract_first()), 0)))
                if any(x in each_price.css("::text").extract_first() for x in matches_offline):
                    pass
                else:
                    if each_price.css(".font-weight-normal::text").extract_first() == None or each_price.css(
                            ".font-weight-normal::text").extract_first() == "":
                        pass
                    else:
                        if "da €" in each_price.css(".font-weight-normal::text").extract_first():
                            price_range = re.findall("[0-9]+\.[0-9]+|[0-9]+",
                                                     each_price.css(".font-weight-normal::text").extract_first())
                            offline_price_list.append(int(self.get_index(price_range, 0).replace(".", "")))
                        elif re.search("[0-9]+\.[0-9]+", each_price.css(".font-weight-normal::text").extract_first()):
                            offline_price_list.append(int(self.get_index(re.findall("[0-9]+", each_price.css(
                                ".font-weight-normal::text").extract_first().replace(".", "")), 0)))
                        else:
                            offline_price_list.append(int(
                                self.get_index(
                                    re.findall("[0-9]+", each_price.css(".font-weight-normal::text").extract_first()),

                                    0)))
        if online_price_list:
            item["price_online"] = min(online_price_list)
        else:
            item["price_online"] = None
        if offline_price_list:
            item["price_offline"] = min(offline_price_list)
        else:
            item["price_offline"] = None
        item["telephone_1"] = self.get_index(response.css("a[href^='tel:']::text").extract(), 0)
        item["telephone_2"] = self.get_index(response.css("a[href^='tel:']::text").extract(), 1)
        item["telephone_3"] = self.get_index(response.css("a[href^='tel:']::text").extract(), 2)
        item["email"] = None
        item["website"] = None
        item["description"] = "".join(response.css(".doc-text-box p::text").extract())
        item["conditions"] = ",".join(response.css("#patologie p::text").extract())
        specalization_list = []
        for each in response.css("#patologie ul li"):
            if each.css("li span[data-placement]"):
                specalization_list.append(each.css("li p::text").extract_first())
        item["specialties"] = ",".join(specalization_list)
        item["ages_treated"] = None
        item["therapy_type"] = None
        item["social_instagram"] = None
        item["social_facebook"] = None
        item["social_linkedin"] = None
        item["does_qa"] = None
        item["albo"] = None
        item["albo_numero"] = None
        item["has_publications"] = None
        item["photo"] = response.css(".doc-photo img::attr(data-src)").extract_first()
        item["photo_large"] = None
        item["qualifications_dottori.it"] = ",".join(
            response.css(".profile-header-card__profile h1+div span::text").extract())
        for each in response.css(".mb-3"):
            if 'Abilitazione' in each.css("h4 strong::text").extract():
                item["albo"] = " ".join([w for w in each.css("ul li::text").extract_first().split() if not w.isdigit()])
                item["albo_numero"] = self.get_index(re.findall("[0-9]+", each.css("ul li::text").extract_first()), 0)
        item["website"] = response.css(".website-link::attr(href)").extract_first()
        file_name = "dottori_it.csv"
        file_exists = os.path.isfile(file_name)
        with open(file_name, 'a', encoding="utf-8") as csvfile:
            headers = item.keys()
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header
            writer.writerow(item)
        yield
