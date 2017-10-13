# Pygoogle Python3 Multilingual

The original pygoogle is here --> https://code.google.com/p/pygoogle/

I need it run in python3 and search the chinese queries,but it seems to lack of these features even in the newest version.
I also can't find any custom version of it fulfills my needs,so I do it by myself.This is just the python3 version support the chinese queries(works on other languages too I think).

***

Retrieve Google Search Result
The ajax api used by pygoogle seems not to perform very well and yield weird searching results in many conditions.
I directly download the google search result page and parse it by beautifulsoup.
