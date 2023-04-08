import streamlit as st
from urllib import request
from urllib.request import Request, urlopen
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd 
import numpy as np
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from PIL import Image
import time
import re
import streamlit_ext as ste
import plotly.express as px
import plotly.graph_objects as go


# python -m streamlit
def getdata(page):
    source = Request(page, headers={"User-Agent": "Mozilla/5.0"})
    source = urlopen(source).read()
    soup = BeautifulSoup(source,'html.parser')
    return soup

def getnextpage(soup,city,pagecount):
    if soup.find("span",{"class":"icon--24-chevron-right-v2 navigation-button-icon__09f24__Bmrde css-1kq79li"}):
        url = "https://www.yelp.co.uk/search?find_desc=Restaurants&find_loc={}&start={}0".format(city,str(pagecount))
        return url
    else:
        return 

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']  
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data





    
st.title("Foodie's Map")  
st.write("Created by [Sum Yu Ng]")  
image = Image.open("image.jpg")
st.image(image,caption='Food Gallary')


progress_text = "Download in progress. Please wait.     🦘🦘🦘🦘"   

st.text("")

#create progress bar
my_bar = st.progress(0, text= "🍙🍭🍨🍣🍩🍔🍕🥐🍢🫕🫔🥗🍱🍜🥞🍝🍟🍯🍅🍚🥜🍦🥔🥕🍎🥓🍥🍠🫑🍲🫖🍛🧋🥙🥘🍞")
#image = Image.open("image.jpeg")
#st.image(image,use_column_width=True)



# create uk city drop down 
uk_city = np.genfromtxt("UK city.csv",delimiter=',', dtype=str)
uk_city = uk_city[:].tolist()
city = st.sidebar.selectbox(
         label = 'UK City Name',
         options = uk_city).title()
city = city.replace(" ","+")

restaurant_table = pd.DataFrame(columns = ["City" ,
                           "Restaurant",
                           "Cuisine",
                           "Price" ,
                           "Rating" ,
                           "Number of Reviews",
                           "Open Now",
                           "Openign Times",
                           "Address" ,
                           "Website",
                           "Phone Number"])



yelp_restaurant = "https://www.yelp.co.uk/search?find_desc=Restaurants&find_loc={}&start={}0".format(city,"")
base_url = "https://www.yelp.co.uk/"
pagecount = 1
restaurant_count = 0
# Connect to Website and pull in data
# ["City","Restaurant","Cuisine","Price","Rating","Number of Reviews","Open Now","Openign Hour","Postcode","Website"]

# select box 
if st.sidebar.button('Extract Now'):
    while True:
        time.sleep(0.1)
        if restaurant_count > 100: 
            my_bar.progress(100, text= "{}\n{} restaurants have been downloaded".format(progress_text,str(restaurant_count)))
        else:
            my_bar.progress(restaurant_count,text= "{}\n{} restaurants have been downloaded".format(progress_text,str(restaurant_count)))
        page_soup = getdata(yelp_restaurant)
        restaurant_webs = page_soup.find_all("a",{"rel":"noopener","class":"css-1m051bw","href":True})
        for rest in restaurant_webs:
            rest_href = base_url+rest['href']
            restaurant_soup = getdata(rest_href)
            rest_soup = etree.HTML(str(restaurant_soup))
            try:
                try:
                    restaurant_name = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[1]/h1")[0].text
                except:
                    restaurant_name = restaurant_soup.find("h1",{"class":"css-1se8maq"}).text
                try:
                    cuisine = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/span[3]/span/a")[0].text
                except:
                    if restaurant_soup.find_all("a",{"class":"css-1m051bw"})[1].text != "Unclaimed":
                        cuisine = restaurant_soup.find_all("a",{"class":"css-1m051bw"})[1].text
                    else:
                        cuisine = restaurant_soup.find_all("a",{"class":"css-1m051bw"})[2].text
                price = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/span[2]/span")[0].text
                rating = str(restaurant_soup.find("div",{"aria-label": re.compile('.*star rating$')})).split()
                rating = rating[1]
                rating = rating.replace('aria-label="','')
                
                try:
                    number_of_reviews = restaurant_soup.find("a",{"href":"#reviews","class":"css-1m051bw"}).text
                    
                except:
                    try:
                        number_of_reviews = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/span[2]")[0].text
                       
                    except:
                        try:
                            number_of_reviews = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/span[2]/a")[0].text
                        except:
                            number_of_reviews = 0
                try:
                    open = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[3]/div[1]/div/div/span[1]")[0].text
                except:
                    open = "N/A"
                try:
                    open_times = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[3]/div[1]/div/div/span[2]/span")[0].text
                except:
                    open_times = "Please go to restuarant's website to see more information"
                try:
                    address = rest_soup.xpath("//*[@id='location-and-hours']/section/div[2]/div[1]/div/div/div/div[1]/address/p[1]/a/span")[0].text + " " + rest_soup.xpath("//*[@id='location-and-hours']/section/div[2]/div[1]/div/div/div/div[1]/address/p[2]/span")[0].text
                except:
                    address = rest_soup.xpath("//*[@id='location-and-hours']/section/div[2]/div[1]/div/div/div/div[1]/address/p[1]/a/span")[0].text
                try:
                    website = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[2]/div/aside/div/section/div/div[1]/div/div[1]/p[2]/a")[0].text
                except:
                    website = rest_href
                try:
                    phone_number = rest_soup.xpath("/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[2]/div/aside/div/section/div/div[2]/div/div[1]/p[2]")[0].text
                except:
                    phone_number = "N/A"
                rest_dictionary = {"City" : city.replace("+"," "),
                                "Restaurant": restaurant_name,
                                "Cuisine":cuisine,
                                "Price" :price,
                                "Rating" : rating,
                                "Number of Reviews":number_of_reviews.replace("(","").replace(")",""),
                                "Open Now":open,
                                "Openign Times":open_times,
                                "Address" : address,
                                "Website" : website,
                                "Phone Number" : phone_number
                                }
                restaurant_count += 1
                restaurant_table = restaurant_table._append(rest_dictionary,ignore_index=True)
            except Exception as e:
                pass
        yelp_restaurant = getnextpage(page_soup,city,pagecount)
        if not yelp_restaurant:
            my_bar.progress(100, text=progress_text + str(restaurant_count) + " have been downloaded")
            st.success(str(restaurant_count) + " restaurants have been found",icon="📚")
            break
        pagecount +=1
    
    
    
    st.divider()
    
    cuisine_df = restaurant_table.groupby('Cuisine').count().reset_index()
    cuisine_df = cuisine_df.rename(columns={"Restaurant": "No of Restaurant"})  
    fig = go.Figure() 
    fig.add_trace(go.Bar(
             x=cuisine_df['Cuisine'],
             y=cuisine_df['No of Restaurant'],
             name='Number of Restaurant',
            marker=dict(color='LightSkyBlue')))
    fig.update_layout(
            autosize=False,
            width=800,
            height=600)
    city = city.replace("+"," ")
    st.header(f"No of Restaurant by Cuisine\n {city}")
    st.plotly_chart(fig)
    
    st.divider()  
    st.write(restaurant_table)    
    rest_xlsx = to_excel(restaurant_table)
    st.text("{Yelp. “Yelp.” Yelp, www.yelp.co.uk.}")
    ste.download_button(label='📥 Download Result',
                                data= rest_xlsx,
                                file_name= city + '_restaurant.xlsx') 
else:
    st.sidebar.write('👆 Click here to extract data')
