from datetime import date, datetime, timedelta
import pytz
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import requests
import time
from twilio.rest import Client
from csv import DictWriter


#Twilio SMS API creds
account_sid = 'xxx'
auth_token = 'xxx'

#Oddds-API URLs and creds
events_url = 'https://odds-api1.p.rapidapi.com/events'
odds_url = 'https://odds-api1.p.rapidapi.com/odds'

headers = {
	"x-rapidapi-key": "xxx",
	"x-rapidapi-host": "odds-api1.p.rapidapi.com"
}

all_tournanments = {'Brasileiro Serie A':325, 'Premier League':17, 'Ligue 1':34, 'Bundesliga':35, 'UEFA Champions League':7, 'Serie A':23, 'LaLiga':8, 'MLS':242, 'NFL':31, 'NCAA':850, 'MLB':109, 'NPB':1036, 'NBA':132, 'Euroleague':138, 'International Matchups':24327, 'NHL':234, 'World Championship':3, 'NRL Premiership':294, 'Super League':302, 'Wimbledon Men Singles': 2555, 'French Open Men Singles':2579, 'Australian Open Men Singles':2567, 'US Open Men Singles':2591}
active_tournanments = {'MLB':109}

all_bookmakers = ['10bet', '188BET', '18Bet', '198Bet', '1xBet', '1xBit', '20Bet', '22Bet', '31Bet', '32Red', '3et', '7Bet LT', 'Admiral AT', 'All British Casino', 'AlphaWin', 'Apuesta Total', 'ATG SE', 'Bally Bet', 'BC.Game', 'Bet3000', 'bet365', 'bet365 DE', 'Bet9ja', 'Betano', 'Betcenter BE', 'Betcity NL', 'BetClic FR', 'BetClic PL', 'BetClic PT', 'BetFair Exchange', 'BetFair Sportsbook', 'Betfred', 'Betfury', 'BetiBet', 'Betika KE', 'BetMGM', 'Betnacional', 'BetOnRed', 'BetParx', 'BetPlay', 'BetRivers', 'Betsafe', 'Betsafe LT', 'Betsson', 'BetUK', 'Betway', 'BetWinner', 'BFB247', 'Bingoal BE', 'Bluechip', 'Bolsa de Aposta Sportsbook', 'Borgata Online Sports', 'BoyleSports', 'Bpremium', 'Bwin', 'Caliente MX', 'CampeonBet', 'CASHPOINT', 'Cloudbet', 'Coolbet', 'Coral', 'Cricbaba', 'DACHBET', 'Dafabet', 'Draftkings', 'Dream.bet', 'Duelbits', 'ESPN Bet', 'Esportiva Bet', 'Estrela Bet', 'FanDuel', 'FDJ', 'FEZbet', 'FreshBet', 'Fun88 UK', 'Gamebookers', 'Goldenbet', 'GreatWin', 'Grosvenor', 'Hollywoodbets', 'INDIBET', 'Interwetten', 'IviBet', 'JackBit', 'Jacks', 'Kaiyun Sports', 'KTO', 'Ladbrokes', 'Ladbrokes DE', 'LeoVegas', 'LibraBet', 'LiliBet', 'LiveScoreBet', 'Lottoland', 'MARCAapuestas', 'MegaPari', 'Merkur Bets', 'MrBit RO', 'MrGreen', 'MyStake', 'N1Bet', 'Napoleon Sports BE', 'NetBet', 'Nextbet', 'Ninecasino', 'NordicBet', 'OddSet', 'Paddy Power', 'paf', 'PremiumBet77', 'Pinnacle Sports', 'Piwi247', 'Pix Bet', 'PMU', 'PointsBet', 'PokerStars', 'Powbet', 'PS3838', 'Qbet', 'QuickWin', 'Rabona', 'RajBet', 'RocketPlay', 'Rollbit', 'Rolletto', 'Roobet', 'Rushbet CO', 'SBOBET', 'SharpBet', 'SingBet', 'Sisal IT', 'SkyBet', 'Smarkets', '888Sport', '888Sport IT', 'Sportaza', 'SportingBet', 'sportwetten.de', 'SportyBet', 'Spreadex', 'Stake.com', 'Starcasino BE', 'Stoiximan', 'STS PL', 'SugarHouse', 'Sultanbet', 'Superbet', 'TABtouch', 'theScore', 'Tipico DE', 'TipTorro', 'Unibet', 'Unibet BE', 'Unibet UK', 'Unibet AU', 'Unibet DK', 'Unibet FR', 'Unibet IT', 'Unibet NL', 'Unibet RO', 'Unibet SE', 'Vave', 'Vertex', 'Virginbet', 'Vistabet', 'Wazamba', 'WELTBET', 'Wettarena', 'WilliamHill', 'Winamax DE', 'WinBet BG', 'WinBet RO', 'Winpot MX', 'Winz.io', 'WOLFBET', 'WPlay CO', 'YesPlay']
my_bookmakers = 'Pinnacle, Betsafe, bet365, Betano, BetMGM, Betway, Bwin, Draftkings, FanDuel, LeoVegas, PointsBet, 888Sport, theScore, Unibet, PokerStars'

active_markets = [101,104,1010,131,1326,121]


def get_pinnacle_odds(response,market):
    '''get_pinnacle_odds(response=json response from get_odds api call, market=string of number representing the particular market of interest [full time result or totals or whatever])
        Returns a list of the odds of a particular market from Pinnacle. Can accomodate two-way or three-way markets'''
    if str(market) not in response['markets'].keys():
        return None
    if 'pinnacle' not in response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'].keys():
        return None
    if response['markets'][str(market)]['oddsType'] == "3Way":
        team_1 = response['markets'][str(market)]['outcomes'][str(market)]['bookmakers']['pinnacle']['price']
        team_x = response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers']['pinnacle']['price']
        team_2 = response['markets'][str(market)]['outcomes'][str(int(market)+2)]['bookmakers']['pinnacle']['price']
        p = [team_1,team_x,team_2]
    else:
        team_1 = response['markets'][str(market)]['outcomes'][str(market)]['bookmakers']['pinnacle']['price']
        team_2 = response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers']['pinnacle']['price']
        p = [team_1,team_2]
    return p


def odds_to_prob(odds: list):
    '''Converts list of odds for a market into list of probabilities--almost exclusively used to derive probabilities out outcomes from Pinnacle odds.'''
    total = sum([1/d for d in odds])
    prob = [(1/d)/total for d in odds]
    return prob

def true_odds(prob):
    '''Converts list of probabilities into list of odds representing the fair odds of that event occuring i.e. no-hold or no-juice lines.
        Used to compare against odds from softer books for expected value calculation'''
    true_odds = [1/p for p in prob]
    return true_odds

def get_bookmaker_odds(response,market):
    '''Returns a dict of all the books and their odds from get_odds response for a particular bet given by market param.'''
    books = []
    master_odds = []
    if response['markets'][str(market)]['oddsType'] == "3Way":
        for book in response['markets'][str(market)]['outcomes'][str(market)]['bookmakers']:
            if book == 'bestPrice': continue
            books.append(book)
            odds = []
            odds.append(response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][book]['price'])
            odds.append(response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][book]['price'])
            odds.append(response['markets'][str(market)]['outcomes'][str(int(market)+2)]['bookmakers'][book]['price'])
            master_odds.append(odds)
        odds_dict = dict(zip(books,master_odds))
    else:
        for book in response['markets'][str(market)]['outcomes'][str(market)]['bookmakers']:
            if book == 'bestPrice': continue
            books.append(book)
            odds = []
            odds.append(response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][book]['price'])
            odds.append(response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][book]['price'])
            master_odds.append(odds)
        odds_dict = dict(zip(books,master_odds))
        return odds_dict

def calc_ev(odds:dict,prob):
    '''calc_ev(odds=dict of books and their odds given by get_bookmaker_odds(), prob=list of probabilities derived from the odds taken from Pinnacle)
        Returns a dict of all the books and the expected values (EV) of their bets in the same format as get_bookmaker_odds().'''
    ev = []
    for book in odds:
        odd = odds[book]
        book_ev = list(map(lambda x, y: x * (y-1) - (1-x), prob, odd))
        ev.append(book_ev)
    final_ev = dict(zip(odds.keys(),ev))
    return final_ev

def bet_select(evs,min=0.01):
    '''bet_select(evs=dict of books and their EVs given by calc_ev(), min=minimum acceptable expected value to be worth betting--default to 1%)
        Returns a list of the bet with the highest EV of all the books for a particular market. List index 0 is the book, index 1 is the bet's position in the original odds list, index 2 is the corresponding EV.'''
    book_list = []
    bet_list = []
    odds_list = []
    for book in evs:
        for odds in range(len(evs[book])):
            if evs[book][odds] > min:
                bet_list.append(evs[book].index(evs[book][odds]))
                book_list.append(book)
                odds_list.append(evs[book][odds])
    if odds_list == []:
        return None
    bet = odds_list.index(max(odds_list))
    return [book_list[bet],bet_list[bet],odds_list[bet]]

def kelly_bet_size(response, market, bet:list, bankroll:int):
    '''kelly_bet_size(response=json response from get_odds api call, market=string of number representing the particular market of interest [full time result or totals or whatever], bet=list containing selected bet information from bet_select(), bankroll=int of current bankroll balance to be used to optimize Kelly criterion bet size)
        Returns the optimal bet size in dollars under the Kelly criterion for a given probability, odds, and bankroll size. '''
    if response['markets'][str(market)]['oddsType'] == "3Way":
        odds = [response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][bet[0]]['price'], response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][bet[0]]['price'], response['markets'][str(market)]['outcomes'][str(int(market)+2)]['bookmakers'][bet[0]]['price']]
        odds = odds[bet[1]]
    else:
        odds = [response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][bet[0]]['price'], response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][bet[0]]['price']]
        odds = odds[bet[1]]
    pin_odds = get_pinnacle_odds(response,market)
    prob = odds_to_prob(pin_odds)
    prob = prob[bet[1]]
    kelly = prob - ((1 - prob) / (odds - 1))
    kelly_bet = kelly * bankroll
    kelly_bet = round(kelly_bet,2)
    return kelly_bet

def bet_details(response, market, bet, bankroll):
    '''bet_details(response=json response from get_odds api call, market=string of number representing the particular market of interest [full time result or totals or whatever], bet=list containing selected bet information from bet_select(), bankroll=int of current bankroll balance to be used to optimize Kelly criterion bet size).
    Returns a dict of all the details of the bet that should be made. Used as a final output to the user to then manually enter the bet through the particular bookmaker.'''
    if bet == None:
        return None
    details = {}
    details['eventID'] = response['eventId']
    dt = datetime.strptime(response['date'] + ' ' + response['time'], '%Y-%m-%d %H:%M:%S')
    dt = dt.replace(tzinfo=pytz.UTC)
    dt = dt.astimezone(pytz.timezone("US/Eastern"))
    details['datetime'] = dt
    details['match'] = response['participant1'] + ' vs. ' + response['participant2']
    details['sport'] = response['sportSlug']
    if response['markets'][str(market)]['oddsType'] == "Over/Under":
        details['market'] = response['markets'][str(market)]['marketNameShort'] + ' ' + response['markets'][str(market)]['handicap']
    else:
        details['market'] = response['markets'][str(market)]['marketName']
    details['bet type'] = response['markets'][str(market)]['oddsType']
    if response['markets'][str(market)]['oddsType'] == "3Way":
        teams = ['participant1','draw','participant2']
        details['bet side'] = response[teams[bet[1]]]
        odds = [response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][bet[0]]['price'],response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][bet[0]]['price'],response['markets'][str(market)]['outcomes'][str(int(market)+2)]['bookmakers'][bet[0]]['price']]
        details['odds'] = odds[bet[1]]
    elif response['markets'][str(market)]['oddsType'] == "Over/Under":
        teams = ['Over','Under']
        details['bet side'] = teams[bet[1]]
        odds = [response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][bet[0]]['price'],response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][bet[0]]['price']]
        details['odds'] = odds[bet[1]]
    else:
        teams = ['participant1','participant2']
        details['bet side'] = response[teams[bet[1]]]
        odds = [response['markets'][str(market)]['outcomes'][str(market)]['bookmakers'][bet[0]]['price'],response['markets'][str(market)]['outcomes'][str(int(market)+1)]['bookmakers'][bet[0]]['price']]
        details['odds'] = odds[bet[1]]
    details['bet size'] = kelly_bet_size(response, market, bet, bankroll)
    details['expected value (%)'] = bet[2]
    details['book'] = bet[0]
    details['link'] = response['bookmakers'][bet[0]]['eventPath']

    return details

def convert_tz(event):
    '''Helper function to convert the date and time from an Events API call (given in UTC) to Eastern Time so as to avoid confusion in the start times. '''
    dt = datetime.strptime(event['date'] + ' ' + event['time'], '%Y-%m-%d %H:%M:%S')
    dt = dt.replace(tzinfo=pytz.UTC)
    dt = dt.astimezone(pytz.timezone("US/Eastern"))
    return dt

#if there is nothing for that league then it will return 400 error with message:"tournament exists but is not active at the moment"


def get_events(tournamentID: int):
    '''Calls Events endpoint of API and returns a response of the matches scheduled for a particular league given by the tounamentID'''
    querystring = {'tournamentId':f'{tournamentID}','media':'false'}
    response = requests.get(events_url, headers=headers, params=querystring)
    if response.status_code != 200:
        print(response.status_code, response.reason)
        return None
    else:
        return response.json()

def get_odds(eventID: str, bookmakers:str):
    '''Calls Odds endpoint of API and returns a response of the the odds for all specified bookmakers for a single match.
    eventID must be one single match, and bookmakers must be a comma separated string.'''
    querystring = {'eventId':f'{eventID}','bookmakers':bookmakers,'oddsFormat':'decimal','raw':'false'}
    response = requests.get(odds_url, headers=headers, params=querystring)
    if response.status_code != 200:
        print(response.status_code, response.reason)
        return None
    else:
        return response.json()

def check_upcoming_events(response):
    '''Checks for matches occuring today from response of Events API call. Used to later determine which matches to pull odds from given their scheduled date and time.'''
    events = []
    date_time = []
    
    for event in response['events']:
        event_datetime = convert_tz(response['events'][event])
        if event_datetime.date() == datetime.now().date() and event_datetime - datetime.now().astimezone(pytz.timezone("US/Eastern")) > timedelta(minutes=0.5):
            events.append(response['events'][event]['eventId'])
            date_time.append(event_datetime)
    upcoming_events = dict(zip(events,date_time))
    return upcoming_events

def get_all_events(tournaments: dict):
    '''Makes an Events API call for every league and checks the dates of all matches in each league to see if they are occurring today. Returns a dictionary of the eventID and datetime of each upcoming match. used to narrow down the universe of potential matches to check in the final stretch before pre-match betting closes, limiting the number of total API calls. '''
    all_events = dict()
    for id in tournaments.values():
        try:
            response = get_events(id)
        except:
            continue
        if response == None:
            continue
        all_events.update(check_upcoming_events(response))
    return all_events

def check_odds(all_events:dict, markets, bankroll, within=20):
    '''Cycles through events scheduled for today and makes and API call to get the odds of events occuring in <30 minutes from now. For events that are <30 minutes from now, if Pinnacle has odds for that event, then calculate the probabilities and expected values of major bets and returns a dict of bets that should be made.'''
    for event in all_events:
        if all_events[event] - datetime.now().astimezone(pytz.timezone("US/Eastern")) < timedelta(minutes=within):
            odds_response = get_odds(event,my_bookmakers)
            if odds_response == None:
                continue
            if 'pinnacle' in odds_response['bookmakers']:
                    for market in markets:
                        p_odds = get_pinnacle_odds(odds_response,market)
                        if p_odds == None:
                            continue
                        prob = odds_to_prob(p_odds)
                        all_odds = get_bookmaker_odds(odds_response,market)
                        evs = calc_ev(all_odds,prob)
                        bets = bet_select(evs)
                        if bets == None:
                            print(f'Nothing in {odds_response['markets'][str(int(market))]['marketNameShort']} for {odds_response['participant1']} vs. {odds_response['participant2']}')
                            continue
                        details = bet_details(odds_response,str(market),bets,bankroll)
                        return [event, details]
            else:
               print('Pinnacle not supported')
               continue
        else:
            print(f'Match in {all_events[event] - datetime.now().astimezone(pytz.timezone("US/Eastern"))}')
            continue

def send_SMS(details):
    ''''Twillio API to send text message notifications for bets to place'''
    if details == None: return None
    twilio_client = Client(account_sid, auth_token)
    message = twilio_client.messages.create(
    from_='+19384005658',
    body=f"Match: {details['match']}\nTime: {details['datetime'].strftime('%c')}\nSport: {details['sport'].title()}\nMarket: {details['market']}\nTeam: {details['bet side']}\nBet Size: {details['bet size']}\nOdds: {details['odds']}\nBookmaker: {details['book']}\nLink: {details['link']}",
    to='+16138900270'
    )

def add_csv(details:dict):
    with open('bet_list.csv', 'a') as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=list(details.keys()))
        dictwriter_object.writerow(details)
        f_object.close()


#Run script on loop until manually closed or matches run out

#get today's events
today_games = get_all_events(active_tournanments)
if len(today_games) == 0:
    print("No matches scheduled for today.")
    exit()
else:
    print('Checking games...')
    print(today_games)
    check = 1

while True:
    #check if today's events has already started
    if len(today_games) != 0:
        for event in today_games.copy():
            if today_games[event] - datetime.now().astimezone(pytz.timezone("US/Eastern")) < timedelta(minutes=1.5):
                today_games.pop(event)
                if len(today_games) == 0:
                    print('No more matches scheduled for today.')
                    exit()
    else:
        print('No more matches scheduled for today.')
        exit()

    #check odds for today's events and send SMS notification if it fits criteria
    results = check_odds(today_games,active_markets,5000)
    if results != None:
        send_SMS(results[1])
        add_csv(results[1])
        today_games.pop(results[0])

    #wait and recheck in 60 seconds
    time.sleep(90)
    check +=1
    print(f'Check #{check}')

