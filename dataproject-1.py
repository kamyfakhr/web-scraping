import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import unicodedata
import re
import json
import matplotlib.pyplot as plt
import numpy as np

task1_dic = {}
task2_dic = {}
task3_dic = {}
headlines = []
visited_links = []
names = []
name_list = []
scores = []
name_repeat = {}
first_mentioned_player = []
game_differences = {}
avg_game_difference = {}
total_links = 0
win_percentage = {}
pattern = r'(\(?\d{1}-\d{1}\)?[\ ]){2,5}'

with open('tennis.json') as file:
    tennis_data = json.load(file)

print(" Three csv files and 2 png files have been saved on your deivce!")    
for dic in tennis_data:
   
    name_repeat[dic["name"]] = 0
    
    game_differences[dic["name"]] = 0
    avg_game_difference[dic["name"]] = 0
    names.append(dic["name"])

for dic in tennis_data:
    win_pct = re.sub('%', '', dic["wonPct"])
    win_percentage[dic["name"]] = float(win_pct)




base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'
seed_item = 'index.html'
seed_url = base_url + seed_item
page = requests.get(seed_url)
soup = BeautifulSoup(page.text, 'html.parser')

visited = {}; 
visited[seed_url] = True
pages_visited = 1
#print(seed_url)

#Remove index.html
links = soup.findAll('a')
seed_link = soup.findAll('a', href=re.compile("^index.html"))
#to_visit_relative = list(set(links) - set(seed_link))
to_visit_relative = [l for l in links if l not in seed_link]


# Resolve to absolute urls
to_visit = []
for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))

    
#Find all outbound links on succsesor pages and explore each one 
while (to_visit):
    # Impose a limit to avoid breaking the site 
        
    # consume the list of urls
    link = to_visit.pop(0)
    #print(link)
    visited_links.append(link)

    page = requests.get(link)
    
    # scarping code goes here
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # mark the item as visited, i.e., add to visited list, remove from to_visit
    visited[link] = True
    to_visit
    # find the headline of webpage
    next_title = soup.find(attrs={"class": "headline"})
    headlines.append(next_title.text.strip())
    
    # the whole article text
    article_text = soup.find(attrs={"id": "articleDetail"})
    
    paragraphs = article_text.find('p')
      
    main_p = unicodedata.normalize("NFKD", paragraphs.text.strip())
    
    # search to find the first score in the article
    if (re.search(pattern, str(article_text))):
        score = re.search(pattern, str(article_text)).group(0)
        
        simple_score = re.sub('\(.*\)', '', score)
        
        scores.append(score)
    else:
        scores.append(' ')
    sets = r'([0-7]-[0-7])'
    
    # find the sets for game difference calculation
    real = re.findall(sets, simple_score)
    game_difference = 0
    
    for _set in real:
        difference = (int(_set[0])-int(_set[2]))
        game_difference += difference
    
    # find the names in the article
    split_p = str(main_p).split()
    boolean = 0
    article_player = []
    for name in names:
        for i in range(len(split_p)-1):
            if (split_p[i].lower()+' '+split_p[i+1].lower()) in name.lower():
                article_player.append(name)
                boolean = 1
    if boolean == 0:
        article_player.append('No Name')

    # remove all the names except the first one
    name_list.append(article_player[0])   

    if article_player[0] in name_repeat:
        name_repeat[article_player[0]] += 1
        game_differences[article_player[0]] += abs(game_difference)

    
            
    # find the links inside the current webpage  
    new_links = soup.findAll('a')
    for new_link in new_links :
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)
        
    pages_visited = pages_visited + 1

# sorting names by repeat           
sorted_players_name = {k: v for k, v in sorted(name_repeat.items(), key=lambda item: item[1], reverse=True)}

# producing task1 csv file
task1_dic['Urls'] = visited_links
task1_dic['Headlines'] = headlines
task1 = pd.DataFrame(task1_dic)
task1.to_csv('task1.csv')

# avg game difference calculation
for player in avg_game_difference:
    if name_repeat[player] > 0:
        avg_game_difference[player] = game_differences[player]/name_repeat[player]
print(task1)


# producing task2 csv file
task2_dic['Urls'] = visited_links
task2_dic['Headlines'] = headlines
task2_dic['Player'] = name_list
task2_dic['Score'] = scores
task2 = pd.DataFrame(task2_dic)
print(task2)
task2.to_csv('task2.csv')


# producing task3 csv file
task3_dic['Player'] = []
task3_dic['Average game difference'] = []
for player in avg_game_difference:
    if avg_game_difference[player] != 0:
        task3_dic['Player'].append(player)
        task3_dic['Average game difference'].append(avg_game_difference[player])

task3 = pd.DataFrame(task3_dic)
print(task3)
task3.to_csv('task3.csv')


# producing the task4 plot
data1_columns = ['player', 'number of articles']
record1 = []
for player in sorted_players_name:
    alist = []
    alist.append(player)
    alist.append(sorted_players_name[player])
    record1.append(alist)
tennis_data1 = pd.DataFrame(record1[:5], columns = data1_columns)

plt.figure(figsize=(10,10))
plt.bar(tennis_data1['player'], tennis_data1['number of articles'])
plt.ylabel('Number of articles')
plt.title("Number of articles per players")
plt.xticks(rotation=45)
plt.rcParams.update({'font.size': 22})
plt.savefig('task4.png')
#plt.clf()

# producing task5 plot
data2_columns = ['player', 'avg game difference', 'win percentage']
record2 = []

tennis_data3 = {}
for player in avg_game_difference:

    if name_repeat[player] > 0:
        alist = []
        alist.append(player)
        
        alist.append(avg_game_difference[player])
        alist.append(win_percentage[player])
        record2.append(alist)
tennis_data2 = pd.DataFrame(record2, columns = data2_columns)


width = 0.35
fig, ax1 = plt.subplots()
plt.xticks(rotation=80)
plt.title(" Players avg game difference & win percentage ", fontsize=12)
ax2 = ax1.twinx() 

ax1.bar(tennis_data2['player'], tennis_data2['win percentage'], width=0.4)
ax2.plot(tennis_data2['player'], tennis_data2['avg game difference'], 'y-', marker ='o')
ax1.set_xticklabels(tennis_data2['player'], fontsize=4)
ax1.set_ylabel('Win %', color='b', fontsize=8)
ax2.set_ylabel('avg game difference', color='y', fontsize=8)
ax1.set_ylim(0,100)
ax2.set_ylim(0,12)
ax1.set_yticks((0,10,20,30,40,50,60,70,80,90,100))

plt.savefig('task5.png')
#plt.show()



