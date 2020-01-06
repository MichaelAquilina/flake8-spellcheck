import re


def write_Whitelist():
    """
    add words to the whitelist.txt for spelling check
    """
    words = dict()
    whitelist = open(r'/Users/logan.li/project/django.txt', 'a')

    # cache: run `flake8 django/ > whitelist.cache`
    with open(r'/Users/logan.li/project/whitelist.cache', 'r+') as cache:
        for line in cache.readlines():
            word = re.match(".* SC200 .*'(.*)'", line)
            if word:
                word = word.group(1).lower()
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1

                                
     # write words to whiltelist.txt
    for aWord in words:
        if words[aWord] >= 5:
            whitelist.write(aWord + '\n')
    
    whitelist.close()

if __name__=="__main__":
    write_Whitelist()

