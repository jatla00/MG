# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 lambda

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


import re,urllib,urlparse

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['ororo.tv']
        self.base_link = 'https://www2.ororo.tv'
        self.moviesearch_link = '/en/movies'
        self.tvsearch_link = '/en'

        self.cookie = None
        self.lang = 'locale=en; nl=true'
        self.sign = 'https://www2.ororo.tv/en/users/sign_in'
        self.user = control.setting('ororo.user')
        self.password = control.setting('ororo.pass')
        self.headers = {'User-Agent': 'Exodus for Kodi'}
        self.post = {'user[email]': self.user, 'user[password]': self.password, 'user[remember_me]': 1}
        self.post = urllib.urlencode(self.post)


    def movie(self, imdb, title, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()

            if self.cookie == None: self.cookie = client.source(self.sign, post=self.post, headers=self.headers, cookie=self.lang, output='cookie')

            url = urlparse.urljoin(self.base_link, self.moviesearch_link)

            result = client.source(url, cookie='%s; %s' % (self.cookie, self.lang))

            title = cleantitle.get(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = client.parseDOM(result, 'div', attrs = {'class': 'index show'})
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', attrs = {'class': 'name'}), client.parseDOM(i, 'span', attrs = {'class': 'value'})) for i in result]
            result = [(i[0][0], i[1][0], i[2][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            result = [i for i in result if title == cleantitle.get(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()

            if self.cookie == None: self.cookie = client.source(self.sign, post=self.post, headers=self.headers, cookie=self.lang, output='cookie')

            url = urlparse.urljoin(self.base_link, self.tvsearch_link)

            result = client.source(url, cookie='%s; %s' % (self.cookie, self.lang))

            tvshowtitle = cleantitle.get(tvshowtitle)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = client.parseDOM(result, 'div', attrs = {'class': 'index show'})
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', attrs = {'class': 'name'}), client.parseDOM(i, 'span', attrs = {'class': 'value'})) for i in result]
            result = [(i[0][0], i[1][0], i[2][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            result = [i for i in result if tvshowtitle == cleantitle.get(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if (self.user == '' or self.password == ''): raise Exception()

            if url == None: return

            url = '%s#%01d-%01d' % (url, int(season), int(episode))
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if (self.user == '' or self.password == ''): raise Exception()

            if self.cookie == None: self.cookie = client.source(self.sign, post=self.post, headers=self.headers, cookie=self.lang, output='cookie')


            try: url, season, episode = re.compile('(.+?)#(\d*)-(\d*)$').findall(url)[0]
            except: pass
            try: href = '#%01d-%01d' % (int(season), int(episode))
            except: href = '.+?'


            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url, cookie='%s; %s' % (self.cookie, self.lang))

            url = client.parseDOM(result, 'a', ret='data-href', attrs = {'href': href})[0]
            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url, cookie='%s; %s' % (self.cookie, self.lang))

            headers = '|%s' % urllib.urlencode({'User-Agent': self.headers['User-Agent'], 'Cookie': str(self.cookie)})

            url = client.parseDOM(result, 'source', ret='src', attrs = {'type': 'video/mp4'})
            url += client.parseDOM(result, 'source', ret='src', attrs = {'type': 'video/.+?'})
            url = url[0] + headers

            sources.append({'source': 'ororo', 'quality': 'HD', 'provider': 'Ororo', 'url': url, 'direct': True, 'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


