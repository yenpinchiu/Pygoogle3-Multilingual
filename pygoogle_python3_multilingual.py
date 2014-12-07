'''
the original pygoogle is here --> https://code.google.com/p/pygoogle/
this is just the python3 version of it which can support the chinese queries
'''
#!/usr/bin/python
"""
Google AJAX Search Module
http://code.google.com/apis/ajaxsearch/documentation/reference.html
Needs Python 2.6 or later
"""

try:
    import json
except ImportError:
    import simplejson as json
except ImportError:
    print(e)
    exit()

import sys
import logging
import argparse
import urllib.parse
import urllib.request

__author__ = "Kiran Bandla"
__version__ = "0.2"
URL = 'http://ajax.googleapis.com/ajax/services/search/web?'

#Web Search Specific Arguments
#http://code.google.com/apis/ajaxsearch/documentation/reference.html#_fonje_web
#SAFE,FILTER

SAFE_ACTIVE     = "active"
SAFE_MODERATE   = "moderate"
SAFE_OFF        = "off"

FILTER_OFF  = 0
FILTER_ON   = 1

#Standard URL Arguments
#http://code.google.com/apis/ajaxsearch/documentation/reference.html#_fonje_args
RSZ_SMALL = "small"
RSZ_LARGE = "large"

class pygoogle:
   
    def __init__(self,query,pages=10,hl='en',log_level=logging.INFO):
        self.pages = pages
        self.query = query
        self.filter = FILTER_ON     
        self.rsz = RSZ_LARGE
        self.safe = SAFE_OFF
        self.hl = hl
        self.__setup_logging(level=log_level)
       
    def __setup_logging(self, level):
        logger = logging.getLogger('pygoogle')
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(module)s %(levelname)s %(funcName)s| %(message)s'))
        logger.addHandler(handler)
        self.logger = logger

    def __search__(self,print_results=False):

        results = []
        for page in range(0,self.pages):
            rsz = 8
            if self.rsz == RSZ_SMALL:
                rsz = 4
            args = {'q' : self.query,
                    'v' : '1.0',
                    'start' : page*rsz,
                    'rsz': self.rsz,
                    'safe' : self.safe,
                    'filter' : self.filter,    
                    'hl'    : self.hl
                    }
            
            self.logger.debug('search: "%s" page# : %s'%(self.query, page))
            q = urllib.parse.urlencode(args)   
            search_results = urllib.request.urlopen(URL+q)
            data = json.loads(search_results.read().decode('utf-8'))
            if not 'responseStatus' in data:
                self.logger.error('response does not have a responseStatus key')
                continue
            if data.get('responseStatus') != 200:
                self.logger.debug('responseStatus is not 200')
                self.logger.error('responseDetails : %s'%(data.get('responseDetails', None)))
                continue
            if print_results:
                if 'responseData' in data and 'results' in data['responseData']:
                    for result in  data['responseData']['results']:
                        if result:
                            print('[%s]'%(urllib.parse.unquote(result['titleNoFormatting'])))
                            print(result['content'].strip("<b>...</b>").replace("<b>",'').replace("</b>",'').replace("&#39;","'").strip())
                            print(urllib.parse.unquote(result['unescapedUrl'])+'\n')                
                else:
                    self.logger.error('no responseData key found in response. very unusal')
            results.append(data)
        return results
   
    def search(self):
        results = {}
        search_results = self.__search__()
        if not search_results:
            self.logger.info('No results returned')
            return results
        for data in search_results:
            if 'responseData' in data and 'results' in data['responseData']:
                for result in data['responseData']['results']:
                    if result and 'titleNoFormatting' in result:
                        title = urllib.parse.unquote(result['titleNoFormatting'])
                        results[title] = urllib.parse.unquote(result['unescapedUrl'])
            else:
                self.logger.error('no responseData key found in response')
                self.logger.error(data)
        return results

    def search_page_wise(self):
        results = {}
        for page in range(0,self.pages):
            args = {'q' : self.query,
                    'v' : '1.0',
                    'start' : page,
                    'rsz': RSZ_LARGE,
                    'safe' : SAFE_OFF,
                    'filter' : FILTER_ON,    
                    }
            q = urllib.parse.urlencode(args)
            search_results = urllib.request.urlopen(URL+q)
            data = json.loads(search_results.read())
            urls = []
            if 'responseData' in data and 'results' in data['responseData']:
                for result in  data['responseData']['results']:
                    if result and 'unescapedUrl' in result:
                        url = urllib.parse.unquote(result['unescapedUrl'])
                        urls.append(url)            
            else:
                self.logger.error('no responseData key found in response')
            results[page] = urls
        return results
       
    def get_urls(self):
        results = []
        search_results = self.__search__()
        if not search_results:
            self.logger.info('No results returned')
            return results
        for data in search_results:
            if data and 'responseData' in data and data['responseData']['results']:
                for result in  data['responseData']['results']:
                    if result:
                        results.append(urllib.parse.unquote(result['unescapedUrl']))
        return results

    def get_result_count(self):
        temp = self.pages
        self.pages = 1
        result_count = 0
        search_results = self.__search__()
        if not search_results:
            return 0
        try:
            result_count = search_results[0]
            if not isinstance(result_count, dict):
                return 0
            result_count = result_count.get('responseData', None)
            if result_count:
                if 'cursor' in result_count and 'estimatedResultCount' in result_count['cursor']:
                    return result_count['cursor']['estimatedResultCount']
            return 0
        except Exception:
            self.logger.error(e)
        finally:
            self.pages = temp
        return result_count
       
    def display_results(self):
        self.__search__(True)

def main():
    parser = argparse.ArgumentParser(description='A simple Google search module for Python')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Verbose mode')
    parser.add_argument('-p', '--pages', dest='pages', action='store', default=1, help='Number of pages to return. Max 10')
    parser.add_argument('-hl', '--language', dest='language', action='store', default='en', help="language. default is 'en'")
    parser.add_argument('query', nargs='*', default=None)
    args = parser.parse_args()
    query = ' '.join(args.query)
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    if not query:
        parser.print_help()
        exit()
    search = pygoogle( log_level=log_level, query=query, pages=args.pages, hl=args.language)
    search.display_results()

if __name__ == "__main__":
    main()

