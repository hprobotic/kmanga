# -*- coding: utf-8 -*-
#
# (c) 2017 Alberto Planas <aplanas@gmail.com>
#
# This file is part of KManga.
#
# KManga is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KManga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KManga.  If not, see <http://www.gnu.org/licenses/>.

from datetime import date

import scrapy

from scraper.pipelines import convert_to_date
from scraper.items import Genres, Manga, Issue, IssuePage

from .mangaspider import MangaSpider


class MangaHere(MangaSpider):
    name = 'mangahere'
    allowed_domains = ['mangahere.co']

    def get_genres_url(self):
        return 'http://www.mangahere.co/advsearch.htm'

    def get_catalog_url(self):
        return 'http://www.mangahere.co/mangalist/'

    def get_latest_url(self, until):
        return 'http://www.mangahere.co/latest/'

    def parse_genres(self, response):
        """Generate the list of genres.

        @url http://www.mangahere.co/advsearch.htm
        @returns items 1
        @returns request 0
        @scrapes names
        """

        xp = '//a[@class="either"]/text()'
        genres = Genres()
        genres['names'] = response.xpath(xp).extract()
        return genres

    def parse_catalog(self, response):
        """Generate the catalog (list of mangas) of the site.

        @url http://www.mangahere.co/mangalist/
        @returns items 0
        @returns request 15000 20000
        """

        xp = '//a[@class="manga_info"]'
        for item in response.xpath(xp):
            manga = Manga()
            # URL
            xp = './@href'
            manga['url'] = response.urljoin(item.xpath(xp).extract_first())
            meta = {'manga': manga}
            request = scrapy.Request(manga['url'], self.parse_collection,
                                     meta=meta)
            yield request

    def parse_collection(self, response, manga=None):
        """Generate the list of issues for a manga

        @url http://www.mangahere.co/manga/angel_densetsu/
        @returns items 1
        @returns request 0
        @scrapes url name alt_name author artist reading_direction
        @scrapes status genres rank rank_order description image_urls
        @scrapes issues
        """

        if 'manga' in response.meta:
            manga = response.meta['manga']
        else:
            manga = Manga(url=response.url)

        # MangaHere returns 200 for 404 pages
        xp = '//div[@class="error_404"]'
        if response.xpath(xp).extract():
            return

        # Check if manga is licensed
        xp = '//div[@class="detail_list"]/div[@class="mt10 color_ff00 mb10"]'
        if response.xpath(xp).extract():
            return

        # URL
        manga['url'] = response.url
        # Name
        xp = '//meta[@property="og:title"]/@content'
        manga['name'] = response.xpath(xp).extract()
        # Alternate name
        xp = '//li[label[contains(text(),"%s")]]/text()'
        manga['alt_name'] = response.xpath(
            xp % 'Alternative Name:').re(r'([^;]+)')
        # Author
        xp = '//li[label[contains(text(),"%s")]]/a/text()'
        manga['author'] = response.xpath(xp % 'Author(s):').extract()
        # Artist
        manga['artist'] = response.xpath(xp % 'Artist(s):').extract()
        # Reading direction
        manga['reading_direction'] = 'RL'
        # Status
        xp = '//li[label[contains(text(),"%s")]]/text()'
        manga['status'] = response.xpath(xp % 'Status:').extract_first()
        # Genres
        manga['genres'] = response.xpath(xp % 'Genre(s):').re(r'([^,]+)')
        # Rank
        manga['rank'] = response.xpath(xp % 'Rank:').extract()
        # Rank order
        manga['rank_order'] = 'ASC'
        # Description
        xp = '//li[label[contains(text(),"%s")]]/p[@id="show"]/text()'
        manga['description'] = response.xpath(xp % 'Summary:').extract()
        # Cover image
        xp = '//img[@class="img"]/@src'
        manga['image_urls'] = response.xpath(xp).extract()

        # Parse the manga issues list
        manga['issues'] = []
        xp = '//div[@class="detail_list"]/ul[not(@class)]/li'
        lines = response.xpath(xp)

        # Check if the lines are empty
        if len(lines) == 1 and 'No Manga Chapter' in lines[0].extract():
            return

        for line in lines:
            issue = Issue(language='EN')
            # Name
            xp = './/a/text()'
            name_1 = line.xpath(xp).extract()
            xp = './/span[@class="mr6"]/text()'
            name_2 = line.xpath(xp).extract()
            xp = './/span[@class="left"]/text()'
            name_3 = line.xpath(xp).extract()
            issue['name'] = name_1 + name_2 + name_3
            # Number
            xp = './/a/text()'
            issue['number'] = line.xpath(xp).re(
                r'([.\d]+)\s*$')
            # Order
            issue['order'] = len(lines) - len(manga['issues'])
            # Release
            xp = './/span[@class="right"]/text()'
            issue['release'] = line.xpath(xp).extract()
            # URL
            xp = './/a/@href'
            url = line.xpath(xp).extract_first()
            issue['url'] = response.urljoin(url)
            manga['issues'].append(issue)
        return manga

    def parse_latest(self, response, until=None):
        """Generate the list of new mangas until a date

        @url http://www.mangahere.co/latest/
        @returns items 0
        @returns request 25 200
        """

        if not until:
            if 'until' in response.meta:
                until = response.meta['until']
            else:
                until = date.today()

        # Get all manga's URL from the same page and update it via
        # `parse_collection`
        xp = '//a[@class="manga_info"]/@href'
        for url in response.xpath(xp).extract():
            manga = Manga(url=url)
            meta = {'manga': manga}
            request = scrapy.Request(url, self.parse_collection, meta=meta)
            yield request

        # Check the oldest update date
        xp = '//span[@class="time"]/text()'
        update_date = response.xpath(xp).extract()[-1]
        update_date = convert_to_date(update_date)
        if update_date < until:
            return

        # Next page
        xp = '//a[@class="next"]/@href'
        next_url = response.xpath(xp).extract_first()
        if next_url:
            next_url = response.urljoin(next_url)
            meta = {'until': until}
            yield scrapy.Request(next_url, self.parse_latest, meta=meta)

    def parse_manga(self, response, manga, issue):
        xp = '//select[@class="wid60"]/option/@value'
        for number, url in enumerate(response.xpath(xp).extract()):
            meta = {
                'manga': manga,
                'issue': issue,
                'number': number + 1,
            }
            yield scrapy.Request(response.urljoin(url),
                                 self._parse_page, meta=meta)

    def _parse_page(self, response):
        manga = response.meta['manga']
        issue = response.meta['issue']
        number = response.meta['number']

        xp = '//img[@id="image"]/@src'
        url = response.xpath(xp).extract()
        issue_page = IssuePage(
            manga=manga,
            issue=issue,
            number=number,
            image_urls=url
        )
        return issue_page
