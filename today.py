import datetime
from dateutil import relativedelta
import requests
import os
import sys
from lxml import etree
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
import build_contrib

TOKEN = os.environ.get('ACCESS_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Set ACCESS_TOKEN (or run inside Actions, which provides GITHUB_TOKEN)')
HEADERS = {'authorization': 'token ' + TOKEN}
USER_NAME = os.environ.get('USER_NAME') or os.environ.get('GITHUB_REPOSITORY_OWNER') or 'Sudhanshub27'
if not USER_NAME:
    raise SystemExit('Set USER_NAME to your GitHub login')
BIRTHDAY = datetime.datetime(2004, 9, 27)
QUERY_COUNT = {'contribution_calendar': 0}


def daily_readme(birthday):
    """
    Returns the length of time since I was born
    e.g. 'XX years, XX months, XX days'
    """
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}{}'.format(
        diff.years, 'year' + format_plural(diff.years),
        diff.months, 'month' + format_plural(diff.months),
        diff.days, 'day' + format_plural(diff.days),
        ' 🎂' if (diff.months == 0 and diff.days == 0) else '')


def format_plural(unit):
    """
    Returns a properly formatted number
    e.g. 'day' + format_plural(diff.days) == 5 >>> '5 days'
    """
    return 's' if unit != 1 else ''


def simple_request(func_name, query, variables):
    """
    Returns a request, or raises an Exception if the response does not succeed.
    """
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
    if request.status_code == 200:
        return request
    raise Exception(func_name, ' has failed with a', request.status_code, request.text, QUERY_COUNT)


def contribution_calendar():
    """
    Uses GitHub's GraphQL v4 API to return the last year of daily contribution counts,
    in the same week/weekday shape as GitHub's own contribution graph.
    """
    query_count('contribution_calendar')
    query = '''
    query($login: String!) {
        user(login: $login) {
            contributionsCollection {
                contributionCalendar {
                    weeks {
                        contributionDays {
                            date
                            contributionCount
                            weekday
                        }
                    }
                }
            }
        }
    }'''
    request = simple_request(contribution_calendar.__name__, query, {'login': USER_NAME})
    calendar = request.json()['data']['user']['contributionsCollection']['contributionCalendar']
    return calendar['weeks']


def svg_overwrite(filename, age_data, weeks):
    """
    Parse SVG files and update elements with age and contribution graph
    """
    tree = etree.parse(filename)
    root = tree.getroot()
    find_and_replace(root, 'age_data', age_data)
    widget_overwrite(root, filename, weeks)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def widget_overwrite(root, filename, weeks):
    """
    Rebuilds the activity widget from scratch each run.
    """
    target = root.find(".//*[@id='activity_widget']")
    if target is None:
        return
    for child in list(target):
        target.remove(child)
    card_width = float(root.get('width').replace('px', ''))
    theme = build_contrib.WIDGET_THEMES[filename]
    fragment = build_contrib.render_widget(theme, card_width, weeks)
    target.append(etree.fromstring(fragment))


def find_and_replace(root, element_id, new_text):
    """
    Finds the element in the SVG file and replaces its text with a new value
    """
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text


def query_count(funct_id):
    """
    Counts how many times the GitHub GraphQL API is called
    """
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1


def perf_counter(funct, *args):
    """
    Calculates the time it takes for a function to run
    """
    start = time.perf_counter()
    funct_return = funct(*args)
    return funct_return, time.perf_counter() - start


def formatter(query_type, difference, funct_return=False, whitespace=0):
    """
    Prints a formatted time differential
    """
    print('{:<23}'.format('   ' + query_type + ':'), sep='', end='')
    print('{:>12}'.format('%.4f' % difference + ' s ')) if difference > 1 else print('{:>12}'.format('%.4f' % (difference * 1000) + ' ms'))
    if whitespace:
        return f"{'{:,}'.format(funct_return): <{whitespace}}"
    return funct_return


def update_readme_cache_buster():
    """Updates README.md with a Unix timestamp query parameter so GitHub Camo CDN proxy always purges cache."""
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        import re
        ts = int(time.time())
        new_content = re.sub(r'card_dark\.svg\?v=\w+', f'card_dark.svg?v={ts}', content)
        new_content = re.sub(r'card_light\.svg\?v=\w+', f'card_light.svg?v={ts}', new_content)
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)


if __name__ == '__main__':
    print('Calculation times:')
    age_data, age_time = perf_counter(daily_readme, BIRTHDAY)
    formatter('age calculation', age_time)
    weeks, weeks_time = perf_counter(contribution_calendar)
    formatter('contribution calendar', weeks_time)

    svg_overwrite('card_dark.svg', age_data, weeks)
    svg_overwrite('card_light.svg', age_data, weeks)
    update_readme_cache_buster()

    print('Total GitHub GraphQL API calls:', '{:>3}'.format(sum(QUERY_COUNT.values())))
