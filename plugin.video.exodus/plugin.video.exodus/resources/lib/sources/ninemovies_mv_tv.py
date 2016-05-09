# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,urllib,urlparse,json,time

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.domains = ['9movies.to']
        self.base_link = 'http://9movies.to'
        self.search_link = '/sitemap'


    def movie(self, imdb, title, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def ninemovies_cache(self):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)

            result = client.source(url)
            result = result.split('>Movies and TV-Shows<')[-1]
            result = client.parseDOM(result, 'ul', attrs = {'class': 'sub-menu'})[0]
            result = re.compile('href="(.+?)">(.+?)<').findall(result)
            result = [(re.sub('http.+?//.+?/','/', i[0]), re.sub('&#\d*;','', i[1])) for i in result]
            return result
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            try:
                result = ''

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
                title = cleantitle.get(title)

                try: episode = data['episode']
                except: pass

                url = cache.get(self.ninemovies_cache, 120)

                url = [(i[0], i[1], cleantitle.get(i[1])) for i in url]
                url = [(i[0], i[1], i[2], re.sub('\d*$', '', i[2])) for i in url]
                url = [i for i in url if title == i[2]] + [i for i in url if title == i[3]]

                if 'season' in data and int(data['season']) > 1:
                    url = [(i[0], re.compile('\s+(\d*)$').findall(i[1])) for i in url]
                    url = [(i[0], i[1][0]) for i in url if len(i[1]) > 0]
                    url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[1])]

                url = url[0][0]
                url = urlparse.urljoin(self.base_link, url)

                result = client.source(url)

                years = re.findall('(\d{4})', data['premiered'])[0] if 'tvshowtitle' in data else data['year']
                years = ['%s' % str(years), '%s' % str(int(years)+1), '%s' % str(int(years)-1)]

                year = re.compile('<dd>(\d{4})</dd>').findall(result)[0]
                if not year in years: return sources
            except:
                pass

            try:
                if not result == '': raise Exception()

                url = urlparse.urljoin(self.base_link, url)

                try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
                except: pass

                result = client.source(url)
            except:
                pass

            try: quality = client.parseDOM(result, 'dd', attrs = {'class': 'quality'})[0].lower()
            except: quality = 'hd'
            if quality == 'cam' or quality == 'ts': quality = 'CAM'
            elif quality == 'hd' or 'hd ' in quality: quality = 'HD'
            else: quality = 'SD'

            result = client.parseDOM(result, 'ul', attrs = {'class': 'episodes'})
            result = zip(client.parseDOM(result, 'a', ret='data-id'), client.parseDOM(result, 'a'))
            result = [(i[0], re.findall('(\d+)', i[1])) for i in result]
            result = [(i[0], ''.join(i[1][:1])) for i in result]

            try: result = [i for i in result if '%01d' % int(i[1]) == '%01d' % int(episode)]
            except: pass

            links = [urllib.urlencode({'hash_id': i[0], 'referer': url}) for i in result]

            for i in links: sources.append({'source': 'gvideo', 'quality': quality, 'provider': 'Ninemovies', 'url': i, 'direct': True, 'debridonly': False})

            try:
                if not quality == 'HD': raise Exception()
                quality = directstream.googletag(self.resolve(links[0]))[0]['quality']
                if not quality == 'SD': raise Exception()
                for i in sources: i['quality'] = 'SD'
            except:
                pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            headers = {'X-Requested-With': 'XMLHttpRequest'}

            now = time.localtime()
            url = '/ajax/film/episode?hash_id=%s&f=&p=%s' % (data['hash_id'], now.tm_hour + now.tm_min)
            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url, headers=headers, referer=data['referer'])
            result = json.loads(result)

            grabber = {'flash': 1, 'json': 1, 's': now.tm_min, 'link': result['videoUrlHash'], '_': int(time.time())}
            grabber = result['grabber'] + '?' + urllib.urlencode(grabber)

            result = client.source(grabber, headers=headers, referer=url)
            result = json.loads(result)

            url = [(re.findall('(\d+)', i['label']), i['file']) for i in result if 'label' in i and 'file' in i]
            url = [(int(i[0][0]), i[1]) for i in url if len(i[0]) > 0]
            url = sorted(url, key=lambda k: k[0])
            url = url[-1][1]

            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return


