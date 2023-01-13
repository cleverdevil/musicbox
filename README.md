# Musicbox: Raspberry Pi + NFC Digital Jukebox

This is a very simple personal project that I created for my daughter, provided
here as a useful referece for tinkerers that may want to build their own.
Together, my daughter and I created a little "music box" that she can tap with 
NFC tags that she decorates, and it will stream either a single song or a
playlist of songs associated with the tag to her HomePod Mini. She can also tap
a tag to the music box to stop what is currently playing.

There are two main scripts in this repository, a "client" and a "server." The
client runs on the music box itself, and the server can run wherever you like,
provided that it can be reached via the network by both the client and the
HomePod target.

## The Music Box itself 

First, you need a "client" device to be the music box. We used a [Raspberry Pi 
Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) 
because its cheap, powerful, small, and has a large ecosystem. On the Raspberry 
Pi, we installed the latest 64-bit release of Raspberry Pi OS.

For the NFC reader, we went with a [simple USB-powered device from Amazon](
https://www.amazon.com/gp/product/B00GYPIZG6). You can use any USB-powered 
reader with an ACR122 chip. The one we purchased conveniently came with five NFC
cards.

On device, we installed Python 3.9, created a virtualenv, and installed the only
depdendency for the client - the [PyNFC library](
https://github.com/BarnabyShearer/pynfc). Within the client script, there is a
variable `MUSICBOX_SERVER` which must be sets to the URL that refers to the
server side of this project.

Once you're all set, you just run `python musicbox-client.py` and can start
tapping away. The client sends a maximum of one "event" every 10 seconds to
avoid flooding the server. Once tapped, the client just sends a simple HTTP
request to the server with the identifier of the tapped NFC tag. Easy peasy.

## Music Box Server

The server side does the heavy lift. You could easily run this on the Raspberry
Pi itself, if you don't mind having all of the music on device. I already have a
large music library on my home Synology NAS, so I choose to run the server
there.

The `musicbox-server.py` script is a simple [Flask](
https://flask.palletsprojects.com/) web service, and relies upon the [PyATV 
library](https://pyatv.dev/) to stream music to the HomePod. You'll need to
install both into your Python environment, change the `AIRPLAY_ID` in the script
to point to the IP of your target HomePod, and then run the service on the port
of your choosing:

```sh
$ export FLASK_APP=musicbox-server.py
$ flask run -h 0.0.0.0 -p 5150
```

When an event is received, the server will look for either a playlist file or a
MP3 file that maps to the specified tag identifier within a "music"
subdirectory. For example, if you scan a tag with id `abc123`, then the server
will first look for a playlist at `music/abc123.m3u8`, and then an MP3 file at
`music/abc123.mp3`. If it finds either, it will initiate a stream. If it finds
nothing, it simply stops whatever is playing.

That's it! Nothing too fancy. I know this could be made more general purpose,
but it works just fine for my needs, and was fun to build with my kiddo. Feel
free to fork, borrow, or steal any code within for whatever purpose you like!
