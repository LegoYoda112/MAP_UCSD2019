from requests import get

response = get("https://thomasgodden.com/test1")

print(response.text)


#scheme://netloc/path;parameters?query#fragment
