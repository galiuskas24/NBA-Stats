from selenium import webdriver
import sys
import argparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def check_element(element):
    try:
        myElem = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, element)))
        print("\t-> Element wiht ID={} is ready!".format(element))

    except TimeoutException:
        print("\t-> Loading took too much time!")


def get_element(n):
    if n == 0:
        print('\t-> [***ERROR***]\n')
        return None

    try:
        print('\t-> Opening: {}'.format(complete_url))
        driver.get(complete_url)
        check_element('content')

        print('\t-> Executing .js script...', end='')
        sys.stdout.flush()
        driver.execute_script(
            'var buttons = document.querySelectorAll(\'button\');for (var i=0, l=buttons.length; i<l; i++) {if (buttons[i].firstChild.nodeValue == "Get table as CSV (for Excel)"){buttons[i].click();}}')
        print('DONE')

        if type == 0:
            check_element('csv_pgl_basic')
            elements = driver.find_elements_by_id(id_='csv_pgl_basic')
            games = elements[0].get_attribute("innerHTML").splitlines()

        if type == 1:
            check_element('csv_pgl_basic_playoffs')
            elements = driver.find_elements_by_id(id_='csv_pgl_basic_playoffs')
            games = elements[0].get_attribute("innerHTML").splitlines()

        elif type == 2:
            check_element('csv_pgl_basic')
            check_element('csv_pgl_basic_playoffs')
            elements_r = driver.find_elements_by_id(id_='csv_pgl_basic')
            elements_p = driver.find_elements_by_id(id_='csv_pgl_basic_playoffs')
            games_r = elements_r[0].get_attribute("innerHTML").splitlines()
            games_p = elements_p[0].get_attribute("innerHTML").splitlines()
            games = games_r + games_p[2:]

        print('\t-> [LOADED]\n')
        return games
    except:
        return get_element(n-1)  # try again


#---------------------MAIN------------------------


#popravit output za vise igrača
#popravit all games loadanje dodat error file
#----------------RUN EXAMPLE----------------------
# python3 get_player_career.py michael jordan 1985 2003 jordan_career.csv
#-------------------------------------------------

# ---------------PARSE INPUT STDIN AND ARGUMENTS------------
players = [line.rstrip().split() for line in sys.stdin]

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-o', '--output', help='Output path (.csv)', required=True)
parser.add_argument(
    '-t', '--type',
    help='Types:\n0 -> Regular season (default)\t1 -> Only playoff games\t2 -> 1 and 2 (all games ever played)',
    required=False,
    default=0,
    type=int)
parser.add_argument('-w', '--wait', help='Wait to load the page.',
                    required=False, default=10, type=int)
parser.add_argument('-r', '--repeat', help='Try r times to establish connection.',
                    required=False, default=3, type=int)
args = vars(parser.parse_args())

output_path = args['output']
delay = args['wait']
try_again = args['repeat']
type = args['type']
game_types = {0: 'Regular games', 1: 'Playoff games', 2: 'All games'}
indicators = ['Did Not Dress', 'Inactive', 'Did Not Play', 'Not With Team']

print('Welcome to NBA Loader!')
print('[LOG] delay={} repeat={} games={}'.format(delay, try_again, game_types[type]))
print('[LOG] Creating webdriver...', end='')
sys.stdout.flush()

#------------------------INITIALIZATION-----------------------------------
opts = webdriver.FirefoxOptions()
opts.headless = True
driver = webdriver.Firefox(options=opts)
print('DONE')


for player in players:
    f_name, l_name, start_year, end_year = player
    start_year, end_year = int(start_year), int(end_year)

    #"https://www.basketball-reference.com/players/b/bryanko01/gamelog/2007/"
    main_url = "https://www.basketball-reference.com/players/"
    main_url += l_name[0] + '/'
    main_url += l_name if len(l_name) < 6 else l_name[:5]
    main_url += f_name[:2] + '01/gamelog/'

    print('[LOG] Loading {} for {} {}'.format(game_types[type].lower(), f_name.capitalize(), l_name.capitalize()))
    with open(output_path, 'w') as file:
        for year in range(start_year, end_year + 1):
            print("[DOWNLOAD] Season {}".format(year))

            complete_url = main_url + str(year) + '/'
            csv = get_element(try_again)
            if csv == None:
                continue

            csv = csv[2:] if year != start_year else csv[1:]

            for line in csv:
                if not any(indicator in line for indicator in indicators):
                    file.write(line + '\n')
                else:
                    file.write(
                        '67,51,2019-03-10,30-157,MIN,,NYK,W (+11),0,7:58,2,5,.400,0,0,,0,0,,1,0,1,1,1,0,0,0,0,0,0\n')
