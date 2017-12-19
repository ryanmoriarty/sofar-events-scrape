
# coding: utf-8

# # Events scraping

# In[10]:


import urllib2
from bs4 import BeautifulSoup


# In[11]:


def available(s):
    if s.find('Apply for Tickets')>=0:
        a = 'Available'
    elif s.find('Event is full') >= 0:
        a = 'Sold out'
    else: a = s
    return a


# In[12]:


from datetime import datetime
import re
def cleandate(s):
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)
#d = 
#d = datetime.strptime('Tuesday, 5th', '%A, %d')
#d = datetime.strptime(cleandate('Friday, December 1st'), '%A, %B %d').strftime('%d/%m/2017')
#d


# In[13]:


domain = 'https://www.sofarsounds.com'


# In[14]:


import sqlalchemy as sqa
import pandas as pd
creds = {
    'user': 'ucoq7h2sabk90n',
    'password': 'p9707226g0i18s86582v9or2081',
    'hostname': 'ec2-52-30-189-58.eu-west-1.compute.amazonaws.com',
    'db': 'd5srqo93idqsph'
}

engine = sqa.create_engine('postgresql://{user}:{password}@{hostname}:5432/{db}'.format(**creds))


# ## Get cities list

# In[15]:


sql = """
select cached_slug
from public.cities;
"""
dfo = pd.read_sql_query(sql, engine)
#cities = ['oslo','madrid','london','liverpool','manchester','glasgow','leeds','nyc','la','chicago','san-francisco','toronto','seattle','boston','austin','dallas-fort-worth','berlin','nuremberg']
cities = dfo['cached_slug']


# In[16]:


# build a list of all events for each city
events = []
city_with_no_gigs = []
for city in cities:
    # go to city events page
    page = urllib2.urlopen(domain+'/'+city+'/events')
    
    # parse and find the events list
    soup = BeautifulSoup(page)
    event_list = soup.find("div",class_='events-row')

    # build a list of the events
    try:
        all_links=event_list.find_all("a")
        for link in all_links:
            if link.get("href").find('/events/') > 0: 
                events.append(link.get("href"))
    except: 
        city_with_no_gigs.append(city)


# In[17]:


len(events)


# In[18]:


locations = []
dates = []
closest_stations = []
arrival_times = []
availability = []
apply = []
event_id = []


for event in events:

    if event.find('/events/') < 0: continue

    #print(domain+event)
    event_page = urllib2.urlopen(domain+event)
    soup = BeautifulSoup(event_page)

    event_id.append(event)
    locations.append(soup.find("span",class_='event-rough-location').text)

    #date = soup.find("span",class_='event-date').text
    #date = datetime.strptime(cleandate(date), '%A, %B %d').strftime('%d/%m/2017')
    #print(date)
    dates.append(soup.find("span",class_='event-date').text)
    arrival_times.append(soup.find("span",class_='event-arrival-time').text)
    try: closest_stations.append(soup.find("span",class_='event-closest-station').text)
    except: closest_stations.append('none')

    avl = soup.find("div",{"class":"shortcut-container"}).text.strip()
    availability.append(avl)
    apply.append(available(avl))
    


# In[19]:


import datetime
import pandas as pd
df=pd.DataFrame(event_id,columns=['Event'])
df['Location']=locations
df['Dates']=dates
df['Closest_Station']=closest_stations
df['Arrival_time']=arrival_times
#df['Availability']=availability
df['Apply']=apply
df['Scrape_Time']=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
df


# In[20]:


filename = datetime.datetime.today().strftime('%Y%m%d_%H%M') + '_sofar_scrape.csv'
df.to_csv('/Users/ryan/Google Drive/Personal/Testing/'+filename,index=False,encoding='utf-8')


# In[ ]:


cities_page = urllib2.urlopen('https://www.sofarsounds.com/cities')
soup = BeautifulSoup(cities_page)
city_list = soup.find_all("a")
for city in city_list:
    print(city.get("href"))

