#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import geocoder
import time
import matplotlib
matplotlib.use("Agg")
#from matplotlib import rcParams
#rcParams.update({'figure.autolayout': True})
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

#Team to analyze, set ALL to true if you want to analyze all teams
TEAM = "Montréal Canadiens"
ALL = True

#These lists will hold the locations of players drafted by the team in the
#different rounds
lons = []
lats = []
urlbase = "https://statsapi.web.nhl.com/api/v1/draft/"

#This is a modified function from:
#http://qingkaikong.blogspot.se/2016/02/plot-earthquake-heatmap-on-basemap-and.html
def plot(year):
   m = Basemap(projection='merc',llcrnrlat=20,urcrnrlat=75,\
               llcrnrlon=-180,urcrnrlon=75, resolution = 'l')
   m.drawcoastlines()
   m.drawcountries()

   # compute appropriate bins to aggregate data
   # nx is number of bins in x-axis, i.e. longitude
   # ny is number of bins in y-axis, i.e. latitude
   nx = 54 # 10 degree for longitude bin
   ny = 27 # 10 degree for latitude bin

   # form the bins
   lon_bins = np.linspace(-180, 180, nx)
   lat_bins = np.linspace(-90, 90, ny)

   # aggregate the number of earthquakes in each bin, we will only use the density
   density, lat_edges, lon_edges = np.histogram2d(lats, lons, [lat_bins, lon_bins])

   # get the mesh for the lat and lon
   lon_bins_2d, lat_bins_2d = np.meshgrid(lon_bins, lat_bins)

   # convert the bin mesh to map coordinates:
   xs, ys = m(lon_bins_2d, lat_bins_2d) # will be plotted using pcolormesh

   # define custom colormap, white -> red, #E6072A = RGB(0.9,0.03,0.16)
   cdict = {'red':  ( (0.0,  1.0,  1.0),
                      (1.0,  0.9,  1.0) ),
            'green':( (0.0,  1.0,  1.0),
                      (1.0,  0.03, 0.0) ),
            'blue': ( (0.0,  1.0,  1.0),
                      (1.0,  0.16, 0.0) ) }
   custom_map = LinearSegmentedColormap('custom_map', cdict)
   plt.register_cmap(cmap=custom_map)

   # Here adding one row and column at the end of the matrix, so that 
   # density has same dimension as xs, ys, otherwise, using shading='gouraud'
   # will raise error
   density = np.hstack((density,np.zeros((density.shape[0],1))))
   density = np.vstack((density,np.zeros((density.shape[1]))))

   # Plot heatmap with the custom color map
   plt.pcolormesh(xs, ys, density, cmap="custom_map", shading='gouraud')
   plt.clim(0,100)
   # Add color bar and 
   cbar = plt.colorbar(orientation='horizontal', shrink=0.625, aspect=20, fraction=0.2,pad=0.02)
   cbar.set_label('Number of players',size=12)

   # Plot blue scatter plot of epicenters above the heatmap:    
   x,y = m(lons, lats)
   m.plot(x, y, 'o', markersize=5,zorder=6, markerfacecolor='#424FA4',markeredgecolor="none", alpha=0.1)

   plt.title(str(year),loc='left',fontsize=18)

   # make image bigger:
   plt.gcf().set_size_inches(12,6)
   plt.savefig("images/test"+str(year)+".png")
   plt.clf()

#cmp.set_label('Player birth location',size=18)


#Do a loop from the draft in 1995 to 2017
#I use 1995 because the NHL doesn't have information on prospects in their
#API from before then.
for year in range(1995,2018):
   #Get the url to make requests from
   url = urlbase + str(year)
   response = requests.get(url)
   #Need try-except block because 1986-1994 are not available for some reason
   try:
      #Loop through each round
      rounds = response.json()["drafts"][0]["rounds"]
      for round in range(0,len(rounds)):
         try:
            #Loop through each pick
            picks = rounds[round]["picks"]
            for pick in range(0,len(picks)):
               try:
                  #Only get the picks from the team
                  if picks[pick]["team"]["name"].encode('utf8') == TEAM or ALL:
                     #Get the url with the information on the prospect
                     id = str(picks[pick]["prospect"]["id"])
                     url2 = urlbase + "prospects/" + id
                     response2 = requests.get(url2)
		     #Get their birth location
                     birthCountry = response2.json()["prospects"][0]["birthCountry"]
                     try:
                        birthCity = response2.json()["prospects"][0]["birthCity"]
                        birthStateProvince = response2.json()["prospects"][0]["birthStateProvince"]
                        loc = (birthCity + "," + birthStateProvince + "," + birthCountry)
			g = geocoder.google(loc).latlng
			if g == None:
                 	   raise Exception()
                        lats.append(g[0])
                        lons.append(g[1])
                     except:
                        try:
                           birthCity = response2.json()["prospects"][0]["birthCity"]
			   loc = (birthCity + "," + birthCountry)
			   g = geocoder.google(loc).latlng
			   if g == None:
			      raise Exception()
                           lats.append(g[0])
                           lons.append(g[1])
                        except:
			   loc = birthCountry
                           g = geocoder.google(loc).latlng
			   if g == None:
			      raise Exception()
                           lats.append(g[0])
                           lons.append(g[1])
               except:
                  continue
         except:
            continue
   except KeyError:
      continue
   plot(year)

