
# coding: utf-8


from urllib2 import urlopen
import lxml
from bs4 import BeautifulSoup
import re
from time import sleep
import random
import sys
import json
import gc



BASE_URL = "http://www.delish.com/"

def generate_landingfeed_link(pagenum):
    """
    Each landing page contains a chunk (~60) of recipes. Get new pages by 
    incrementing the page number in the url string 'XXX'  '...special/1/XXX?&id=.....
    """
        
    #concatenate relevent fragments of a url with a pagenumber
    if pagenum <= 71: #only 71 pages exist
        landing_page_link = (BASE_URL + '/landing-feed-special/1/' + str(pagenum) +
                             '?&id=12&template=contenttype&landing=recipes')
        print "Generated link for landing page: %i" %(pagenum)
        return landing_page_link
    else:
        print "Didn\'t get link. There are only 71 landing pages.\n"
        return -1
    

def get_recipe_links(lp_link):
    """
    Gets all the href links on a given landing page.
    """
    try:
        html = urlopen(lp_link).read()
        print "Succesfully opened link: %s\n" %(lp_link)
    except:
        print "%s is not a working link.\n" %(lp_link)
        return -1
    
    soup = BeautifulSoup(html,'lxml')
    #put all links for a given page in a list
    recipe_links = [BASE_URL + a['href'] for a in soup.findAll("a","landing-feed--special-title link link-txt")]
    soup.decompose()
    del html
    gc.collect()
    return recipe_links
    
    #return ####
    

def read_recipe_link(recipe_link):
    """
    Given a link to a recipe on Delish.com, get the name of the recipe and the list of ingredients
    """
    try:
        html = urlopen(recipe_link).read()
    except:
        print "%s is not a working link.\n" %(recipe_link)
        return -1
    
    soup = BeautifulSoup(html,'lxml')
    #this line gets the recipe name from the article-header
    recipe_name = soup.find("header","article-header").h1.string
    #print "Succesfully read recipe name from recipe link: %s "%(recipe_link) #####testing
    soup_objs = soup.find('ul','recipe-list recipe-ingredients-list').findAll('li','recipe-ingredients-item')
    #get the ingredients list. Every ingredient is preceded by an annoying newline character. Remove it
    #before adding to the list. Make sure elem.string returns a string, otherwise skip it.
    ingredients = [elem.string.replace('\n','') for elem in soup_objs if isinstance(elem.string, basestring)]
    #return the name of the recipe and its ingredients in a dictionary object
    soup.decompose()
    """
    del soup_objs
    del html
    gc.collect()
    """
    
    return {recipe_name:ingredients}
    
    #return###
    
def get_all_recipes(page_range):
    """
    Get all the recipes names and ingredients and store them in a dictionary where the keys are the name and
    the ingredients list is the value: {recipe1: [ingr1, ingr2, ....], recipe2:[ingr1, ....]}
    """
    #turns out there are only ever 71 landing pages
    allowed_pagenumbers = set(range(1,72))
    
    if not set(page_range).issubset(allowed_pagenumbers):
        print "Didn\'t get any recipes. Can only look at pages 1 thru 71."
        return
    
    all_recipe_links = []
    
    #concatenate all the recipe links
    for pagenum in page_range:
        landing_page_link =  generate_landingfeed_link(pagenum)
        recipe_links = get_recipe_links(landing_page_link)
        if recipe_links != -1 and recipe_links is not None:
            all_recipe_links.extend(recipe_links)
        else:
            print "Had to terminate scraping because a landing page link was bad.\n"
            return
        sleep(random.uniform(2.0, 4.0)) #add a random amount of deadtime so that the server isn't overloaded
    
    num_recipe_links = len(all_recipe_links)
    recipeName_ingredients = [None]*num_recipe_links #pre allocate size of list
    #add each recipe to the list recipe_ingredients which contains json objects
    #of the form {"recipe name": [list of ingredients]}
    print "There are a total of %i recipe links.\n" %(num_recipe_links)
    for i, rlink in enumerate(all_recipe_links):
        recipe = read_recipe_link(rlink)
        if recipe != -1 or recipe is not None:
            recipeName_ingredients[i] = recipe
            recipe = [] #attempting to get rid of memory leak
        else:
            print "Had to terminate scraping because a recipe link was bad.\n"
            recipe = [] #attempting to get rid of memory leak
            return
        sleep(random.uniform(0.02, .04)) #add a random amount of deadtime so that the server isn't overloaded
        ##print recipe.keys()###for troubleshooting
    gc.collect() #attempting to get rid of memory leak
    return recipeName_ingredients
    #return #### Troubleshooting
        




