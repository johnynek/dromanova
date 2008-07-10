#!/usr/bin/env python

import sys, base64, re, urllib2, os, os.path, urllib, string, codecs
from cStringIO import *
import xml.parsers.expat

#################################################
#Configure the script here:

# use:
# %a -> artist
# %l -> album
# %t -> title
# %n -> track number

#Where do we download the stuff?
base = os.environ['HOME']
#path is an array to be portable.  It is relative to base, this joined together into a path
#there should not be an path separator characters in any of the elements of path (e.g. "/" on unix).
#if there are, they will be replaced with "_".  This is because we don't know if track metadata
#will contain such characters.
path = ["media", "audio", "mp3", "%a", "%l"]
#This filenaming standard is good since lexigraphically it will usually do "the right thing"
filename = "%a-%n-%t.mp3"
#replace the following characters with underscores
underscore_chars = " *+!`'?[]()"

################################################

#####
# This program is part of Dromanova, a python download manager for emusic.
# (c) P. Oscar Boykin <boykin@pobox.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# http://www.gnu.org/copyleft/gpl.html
# 
# The decryption algorithm was taken from the GPL-licensed program Emusic/J
# http://www.kallisti.net.nz/EMusicJ/HomePage
#####

############################

def create_xml(data):
  """Reads the EMP file and returns the decoded XML"""
  line = data.readline()
  
  #Teh hardcore EMUSIC Hax0rs came up with their own super-duper
  #crypto.  How can we ever get around it?
  key = [
  			0x6b, 0xd8, 0x44, 0x87, 0x52, 0x94, 0xfd, 0x6e,
  			0x2c, 0x18, 0xe4, 0xc8, 0xde, 0x0b, 0xfa, 0x6d,
  			0xb5, 0x06, 0x7b, 0xce, 0x77, 0xf4, 0x67, 0x3f,
  			0x93, 0x09, 0x1c, 0x20, 0xf5, 0xbe, 0x27, 0xb1,
  			0x02, 0xc9, 0x8f, 0x37, 0x68, 0x5e, 0xc1, 0x91,
  			0xb4, 0x57, 0x8d, 0x90, 0x55, 0x8e, 0x45, 0x19,
  			0xdb, 0x9c, 0xec, 0xa3, 0x9d, 0x32, 0xf7, 0x81,
  			0xc5, 0x61, 0x8b, 0xab, 0x30, 0xa0, 0xbc, 0x31,
  			0xdf, 0xf3, 0x4b, 0xa9, 0x2f, 0x3a, 0x4a, 0xbf,
  			0x08, 0x66, 0xa7, 0xe2, 0x62, 0x3d, 0x36, 0xb2,
  			0x4f, 0x73, 0x6c, 0x9a, 0x56, 0xcf, 0x33, 0xe5,
  			0x43, 0x10, 0x17, 0xc2, 0x3e, 0x1e, 0x2b, 0x70,
  			0x04, 0x7e, 0xc0, 0x9e, 0xc6, 0x4c, 0x92, 0x5c,
  			0x0f, 0x23, 0x35, 0xd2, 0x7a, 0x3b, 0xaf, 0x80,
  			0xd6, 0x9f, 0x0e, 0x78, 0x63, 0x76, 0x95, 0x58,
  			0x1d, 0x83, 0x22, 0x4d, 0x96, 0xda, 0xc4, 0xae,
  			0xca, 0xcb, 0xed, 0xd9, 0x86, 0x98, 0xea, 0xef,
  			0xc3, 0xd0, 0x00, 0xba, 0x71, 0x46, 0xa8, 0x42,
  			0x72, 0x2a, 0xd1, 0x49, 0xe8, 0xd3, 0xc7, 0xd5,
  			0x50, 0xcc, 0x47, 0x21, 0xd7, 0x60, 0x38, 0x3c,
  			0xe7, 0xd4, 0x89, 0xb6, 0x8a, 0x0c, 0xb8, 0xac,
  			0x0d, 0x82, 0x29, 0x05, 0xe6, 0x5f, 0xfc, 0x5a,
  			0x12, 0x74, 0x5d, 0x8c, 0x14, 0x03, 0x2d, 0x59,
  			0x6f, 0xdc, 0x28, 0x7c, 0x15, 0xad, 0xa2, 0x26,
  			0x11, 0x9b, 0x99, 0x24, 0xfb, 0xf8, 0xa4, 0x07,
  			0x7d, 0x64, 0x75, 0x1b, 0xcd, 0xa5, 0x25, 0xfe,
  			0xb7, 0xb9, 0xff, 0x5b, 0xb0, 0xe0, 0x13, 0x51,
  			0x65, 0x4e, 0xbb, 0xf1, 0xeb, 0x48, 0x39, 0x53,
  			0xf0, 0xe9, 0x85, 0xf2, 0x69, 0x0a, 0xaa, 0x34,
  			0x84, 0x40, 0x41, 0x54, 0xdd, 0xf6, 0x1f, 0xbd,
  			0xa1, 0xe1, 0x1a, 0xe3, 0x01, 0x97, 0x88, 0xa6,
  			0xf9, 0x2e, 0x16, 0xb3, 0x6a, 0xee, 0x79, 0x7f       
  	];
  
  ciphertext = base64.b64decode( line.replace('-',"="), ['.', '_'] );
  decoded = StringIO()
  carry = 0
  #stolen from Emusic/J:
  for i in xrange(1,len(ciphertext)):
    k1 = key[ i & 0xFF ]
    carry = (carry + k1) & 0xFF
    k2 = key[ carry ]
    #Exchange the bytes:
    key[ i & 0xFF ] = k2
    key[carry] = k1
    #Wow, this is heavy duty crypto
    decoded.write( chr( ord( ciphertext[i - 1] ) ^ key[ (k1 + k2) & 0xFF ] ) )
  return decoded.getvalue()
### End of XmlFactory

def decode_xml( xmlstring ):
  """return a tuple of (server, tracklist)"""
  server = {}
  tracklist = []
  track = [{}] #Hack to make a closure work like we want..
  current_element = [""]
  current_hash = [ None ]
  def start_el(name, attrs):
    ce = name.lower()
    current_element[0] = ce
    if ce == "track":
      current_hash[0] = track[0]
    elif ce == "server":
      current_hash[0] = server
    
  def end_el(name):
    n = name.lower()
    if n == "track":
      #just finished a track
      this_track = track[0]
      #clean up some things:
      trnum = int(this_track.get("tracknum", -1))
      if (trnum >= 0) and (trnum < 10):
        this_track["tracknum"] = "0" + this_track["tracknum"]
      tracklist.append( this_track )
      track[0] = {}
      current_hash[0] = None
    elif n == "server":
      current_hash[0] = None
  
  def char_data(data):
    ce = current_element[0]
    if current_hash[0] != None:
      current_hash[0][ ce ] = current_hash[0].get(ce,"") + data.strip()
  p = xml.parsers.expat.ParserCreate()
  p.StartElementHandler = start_el
  p.EndElementHandler = end_el
  p.CharacterDataHandler = char_data
  p.ParseFile( xmlstring )
  return ( server, tracklist )

def make_url(server, track):
  """Given a server element from the XML and a track element, get it"""
  #first construct the URL:
  if 'trackurl' in track:
    return track['trackurl']
  url = "http://" + server["netname"] + server["location"]
  url = url.replace( "%fid", track["trackid"] )
  url = url.replace( "%f", track["filename"] )
  return url

def copy_file( source, dest, callback = None ):
  tot = 0
  block = f.read(100000)
  tot = len(block)
  while block != "":
    output.write(block)
    block = f.read(100000)
    tot = tot + len(block)
    if callback != None:
      callback(tot);
  return tot

def replace_metadata(orig, track):
  """insert the metadata into the string orig"""
  kv = { '%n' : 'tracknum',
         '%a' : 'artist',
         '%l' : 'album',
         '%t' : 'title'
       }
  for (key, val) in kv.iteritems():
    orig = orig.replace(key, track[ val ]);
  return orig

def make_path_fn(track):
  this_fn = replace_metadata(filename, track)
  tmp_path = [replace_metadata(p, track) for p in path]
  #filename's can't have os.sep in them:
  this_fn = this_fn.replace(os.sep,"_");
  tmp_path = [ p.replace(os.sep, "_") for p in tmp_path ]
  this_path = base
  for e in tmp_path:
    this_path = os.path.join(this_path, e) 
  #Make sure any unicode characters are dealt with:
  this_path = this_path.encode('ascii', 'replace')
  this_fn = this_fn.encode('ascii', 'replace')
  for c in underscore_chars:
    this_fn = this_fn.replace(c,"_");
    this_path = this_path.replace(c,"_");
  #Now use URLencoding on any nonsafe characters:
  safe_special_chars = "_-()[],"
  this_fn = urllib.quote(this_fn, safe_special_chars)
  this_path = urllib.quote(this_path, os.sep + safe_special_chars)
  return (this_path, this_fn)

def print_progress(tot):
  sys.stdout.write(".")
  sys.stdout.flush()


if __name__ == "__main__":
  try:
    (server, tracklist) = decode_xml( file(sys.argv[1]) )
  except xml.parsers.expat.ExpatError:
    decoded = create_xml( file( sys.argv[1] ) )
    #print decoded;
    #sys.exit(1)
    (server, tracklist) = decode_xml( StringIO(decoded) )
  for track in tracklist:
    url = make_url(server, track) 
    (this_path, this_fn) = make_path_fn(track);
    if not os.path.exists(this_path):
      os.makedirs(this_path)
    fullname = os.path.join( this_path, this_fn )
    output = file(fullname, "w")
    f = urllib2.urlopen( url )
    sys.stdout.write("Track: %s -> %s\n" % (track["title"].encode('ascii','replace'),
                                            fullname))
    tot = copy_file(f, output, print_progress)
    sys.stdout.write("\ntotal %i\n" % (tot))
    #got the file
