# Ivy Zhou, 3/12/2016
#! python3

import requests, sys, bs4, webbrowser, string
from collections import defaultdict
import regex as re

# TODO: save this outside in a database
topSongs = []

# create a song class to get information about a song
class Song(object):
    def __init__(self, title, artist):
        self._title = title
        self._artist = artist
        self._lyrics = ""

    def __repr__(self):
        return self._title + " - " + self._artist + "\n" + self._lyrics;

    def __str__(self):
        return self._title + " - " + self._artist + "\n" + self._lyrics;

    #@lyrics.setter
    def setLyrics(self, lyrics):
        self._lyrics = lyrics; # store the lyrics of the song

    # some getters
    @property
    def song(self):
        return self._title
    @property
    def artist(self):
        return self._artist

    @property
    def lyrics(self):
        return self._lyrics

# finds the lyrics for each of the songs
def getLyrics(songs = []):
    print('Getting the lyrics...')
    API_key = ""; # put your own API key here
    searchQuery = "http://api.musixmatch.com/ws/1.1/track.search?f_has_lyrics=1f&format=xml&apikey={}".format(API_key);
            #"http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?" # this one kind of just sucks
            #"http://search.azlyrics.com/search.php?q="; # i got banned from azlyrics

    for song in songs:
        res = requests.get(searchQuery + "&q_track=" + song._title + "&q_artist=" + song._artist)
        #webbrowser.open(searchQuery + "&q_track=" + song._title + "&q_artist=" + song._artist)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")

        if (len(soup.findAll("track_id")) == 0):
            continue
        trackID = soup.findAll("track_id")[0].text

        # query for lyrics - due to restrictions from api, we only get 30% of lyrics this way :(
        # but on the other hand, I'm banned from azlyrics right now
        lyricsQuery = "http://api.musixmatch.com/ws/1.1/track.lyrics.get?format=xml&apikey={}&track_id=".format(API_key);
        res = requests.get(lyricsQuery + trackID)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")

        # I have to santize the 30% of lyrics I got from them
        lyrics = soup.findAll("lyrics_body")[0].text;
        cpPos = lyrics.find("*******")
        lyrics = lyrics[:cpPos - 1]

        song.setLyrics(lyrics)

        print(trackID)
        print(song)

# updates list of top songs from the current billboard
def updateTopSongs():
    # request the Top Bill Boards page
    print('Getting the latest funky fresh beats...')
    res = requests.get("http://www.billboard.com/charts/hot-100")
    res.raise_for_status()

    # parse the page for the top songs
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    titles = soup.findAll(attrs={'class' : 'chart-row__song'})
    artists = soup.findAll(attrs={'class' : 'chart-row__artist'})

    # save all the songs away
    for i in range(len(titles)):
        # cut out the featuring artist for my API call
        nextArtist = artists[i].text.strip();
        artistPos = len(nextArtist)
        if nextArtist.find("Featuring") != -1:
            artistPos = nextArtist.find("Featuring") - 1;
        nextSong = Song(titles[i].text, nextArtist[:artistPos])
        topSongs.append(nextSong)

    print(topSongs)

    # find the lyrics for each song
    getLyrics(topSongs)

# absolutely no idea what this does
def remove_punctuation(text):
    return re.sub(r'\p{P}', "", text)

def analyze():
    # sanitize the input for punctuation
    frequencies = defaultdict(int) # could also use a Counter here
    for song in topSongs:
        s = song._lyrics;
        # santize the lyrics i.e. remove punctuation and lowercase, then store in an array
        s = remove_punctuation(s).lower().split();
        #s = s.translate(str.maketrans("",""), string.punctuation).lower().split()
        for word in s:
            frequencies[word] += 1
    print (frequencies)


# dummy main, especially stupid bc/ of the while True
while True:
    command = input("What's next, pops?: ")
    if (len(command) == 0): #break by sending me an empty input line
        break
    elif command == "update":
        updateTopSongs()
        command = input("All done, boss! Do you want to see my work? (Y/N): ");
        if (command == "Y"):
            print(topSongs)
    elif command == "analyze":
        analyze();
