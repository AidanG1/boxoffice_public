from session import S

title = "superman"


url = (
    f"https://www.fandango.com/napi/home/autocompleteDesktopSearch?search={title}"
)

"""curl 'https://www.fandango.com/napi/home/autocompleteDesktopSearch?search=superman' \
  --compressed \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Referer: https://www.fandango.com/superman-2025-230934/movie-overview' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'DNT: 1' \
  -H 'Sec-GPC: 1' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: akamai_generated_location={"zip":"94010-94011","city":"BURLINGAME","state":"CA","county":"SANMATEO","areacode":"650","lat":"37.5670","long":"-122.3669","countrycode":"US","continent":"NA"}; WPPCLdoC=A1VjpQqYAQAAPbuGC03KYWHkESip5ZUYDpszNHc-lMRkK0T54kN2duVsP1lWAYe0gH-cuN4VwH8AADQwAAAAAA^|1^|0^|134d535f5bae22f2112f633b8cedbc4a24686268; akamai_location=%7B%22zip%22%3A%2294010-94011%22%2C%22city%22%3A%22BURLINGAME%22%2C%22state%22%3A%22CA%22%2C%22county%22%3A%22SANMATEO%22%2C%22areacode%22%3A%22650%22%2C%22lat%22%3A%2237.5670%22%2C%22long%22%3A%22-122.3669%22%2C%22countrycode%22%3A%22US%22%7D; pcontext=AAQSG,238737,6/14/2025 12:00:00 AM,1:00 PM; zip=94010; akamai_set_zip=true; searchcity=BURLINGAME; searchstate=CA; searchlocation=lat%3D37.5670%26long%3D-122.3669%26name%3DBURLINGAME%252C%2520CA; AffiliateId=13038; PurchaseChannel=1; bandid=208; superbandid=27; ak_bmsc=C965B2141BA1119AB597B889719BDBCF~000000000000000000000000000000~YAAQl17WF57imcmXAQAAcKSiChy0CRz4yeVpD9I9L5baQ3jmNveWc9AaRR+jOgwqfG/x4zYi4merOk9b6G/o8+SFq7BTjbXCGgKxtMqbBQB1QVDMd2XPXIiCfL3Fp1zV6L8M5UvBhMwXT9LLjtnEo87cgCMtgLsTJTmoAglaNT6K85j+DNBjr9w4OtNwV3hwYrozbpOgiPXFuwVdrlVo3Yva1seSgPWHTJszjJgziCkbRt0YvSAfTOgqE1wM4qN/+zyQA1hGJuTkhkr9oZBwDhTB+Yqb67nkAVMfzEbdkNPz4UtRaHSTr2ATQVldbdcy1RsqtUIQxjEnyLq62L1CZuzZR6XeKEtKaVF5BhU0h52wCZq9iy4fIpWguJn+5C7Dlua2AdZNjRki94TQnKo=; concession-announcement-shown=true; color-palette=JIJzTIJX-QxBgHm36dR87DpFV3W5-xGh5Ajc_uHMp_OGDqSapzuQ; theme-options=1752525088029; mbox=session#bb72b4064bdb4d92b8763921e367516f#1752526949; at_check=true' \
  -H 'TE: trailers'"""
# If-None-Match	W/"674-ri2uhqxZevcQgUPP1G8mIjeZJ4Y"
headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.fandango.com/superman-2025-230934/movie-overview",
    "X-Requested-With": "XMLHttpRequest",
    "DNT": "1",
    "Sec-GPC": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}

r = S.get(url, headers=headers)

# print the request headers
print(r.request.headers)
print(r.request.body)

r.raise_for_status()
print(r.text)
