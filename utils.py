import random
import aiohttp


def minutes_to_degrees(minutes):
    if minutes:
        return float(float(minutes) / 60)
    return 0


def seconds_to_desgrees(seconds):
    if seconds:
        return float(float(seconds) / 3600)
    return 0


def notam_coords_to_degrees(coord):
    return str(float(coord[:2]) + minutes_to_degrees(coord[2:4]) + seconds_to_desgrees(coord[4:6]))


def is_digital_and_letters(word):
    return any(char.isdigit() for char in word) and any(char.isalpha() for char in word)


# return north,east
def get_coordinates(north, east):
    return notam_coords_to_degrees(north) + "," + notam_coords_to_degrees(east.lstrip("0"))


async def get_html(session, url):
    async with session.get(url, ssl=False) as res:
        return await res.json()



async def get_html_content(url):
    UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
           "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
           "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
           "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
           )
    ua = UAS[random.randrange(len(UAS))]

    headers = {'user-agent': ua}
    async with aiohttp.ClientSession(headers=headers) as session:
        content = await get_html(session, url)
        return content