#!/usr/bin/env python
# hydrogen drumkit generator
'''
This program generates hydrogen drumkits from a directory
full of .flac files. Currently it's quite specific to that
although in the future i will try to breakout the file format
'''

#### LICENSE is GPLV3
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import sys,os,shutil,tarfile

# get pwd so we have default name for kit

ARGLIST = sys.argv

if len(ARGLIST) == 1:
    print(" \'.-__     __-.\'")
    print("     \\X M X/       You provided no path!")
    print("      | m |        Proper syntax:")       
    print("       ] [         genhydro ~/path/to/folder/containing/samples")
    print("       \'v\'")
    exit()
else:
    UNIXPATH = ARGLIST[1]

## sanitize trailing slashes
if UNIXPATH.endswith("/"):
    UNIXPATH = UNIXPATH[:-1]
else:
    pass

PATHARRAY = UNIXPATH.split('/')
# CWDNUM = len(PATHARRAY)-2
# KITNAME = PATHARRAY[CWDNUM]  ## this breaks
## print('drumkit name '+KITNAME)  ## debugger
#
#     this gets us to the new working directory
#  and gets us the proper KITNAME regardless of
######        where we are executing the script

os.chdir(UNIXPATH)
CWDNUM = len(PATHARRAY)-1
KITNAME = PATHARRAY[CWDNUM]
# print('new kitname after chdir '+KITNAME) 
# print(UNIXPATH) ##debug

# now we have KITNAME as name for the kit
# lets build the head of the file

XMLFILE = os.path.join(UNIXPATH, "drumkit.xml")
KITFILE = open(XMLFILE, 'w')

KITFILE.write('<drumkit_info>')
KITFILE.write('<name>'+KITNAME+'Kit</name>')
KITFILE.write('''
<author>Klaatu</author>
<info>This drum kit was created with genhydro.py and drummer.sh on behalf of the Second Great Linux Multimedia Sprint. Find out more info at http://slackermedia.info/sprint. It is licensed under the GPLv3 meaning you are free to use it, share it, and modify it, even for commercial purposes, although any changes you make to the kit itself must be made available to everyone for free (not so much to ask considering we did the work to get the kit this far already).</info>
<license>GPLv3</license>''')
KITFILE.write('<instrumentList>')

# the basic info of the drumkit exists.
# now let's loop through each sound file in pwd
# and add them as instruments

# set instrument number
INSTNUM=0
COUNT=0
INSTNAME = filter(lambda x: x.endswith('.flac'), os.listdir(UNIXPATH))
INSTNAME.sort()
## print(INSTNAME)
# lets grab how many files there are for a loop later on. wink wink.
#
# try to get them in some semblance of General MIDI order 
# this is not precise, but 1 in 10 times it will help
#       thanks to [lsd] in opensourcemusicians for ref
# http://en.wikipedia.org/wiki/General_MIDI#Percussion

GMLIST = ['bass','kick','rim','snare','clap','hi','tom','cymbal','tamb','cowbell','slap','bongo','conga','timbale','agogo','maraca','whistle','clave','trian']

for GMINST in GMLIST:
    for DRUMTYPE in INSTNAME:
        if DRUMTYPE.find(GMINST):
            pass
        else:
#            print(str(INSTNUM)+'_'+DRUMTYPE) ##debug statement
            os.rename(DRUMTYPE, str(INSTNUM)+'_'+DRUMTYPE)
            COUNT=COUNT+1
            INSTNUM=INSTNUM+1
# reset number
INSTNUM=0
# reload file list
INSTNAME = filter(lambda x: x.endswith('.flac'), os.listdir(UNIXPATH))
INSTNAME.sort()
#print(INSTNAME) #### debug statement

# now we have the instruments numbered and in order
# so lets parse them into XML

for DRUMTYPE in INSTNAME:
    #    print(DRUMTYPE)    #### debug statement
    KITFILE.write('<instrument>')
    KITFILE.write('<id>'+str(INSTNUM)+'</id>')
    KITFILE.write('<name>'+os.path.splitext(INSTNAME[INSTNUM])[0]+'</name>')
    KITFILE.write('''
            <volume>1</volume>
            <isMuted>false</isMuted>
            <pan_L>1</pan_L>
            <pan_R>1</pan_R>
            <randomPitchFactor>0</randomPitchFactor>
            <filterActive>false</filterActive>
            <filterCutoff>1</filterCutoff>
            <filterResonance>0</filterResonance>
            <Attack>0</Attack>
            <Decay>0</Decay>
            <Sustain>1</Sustain>
            <Release>1000</Release>
            <exclude />''')
    KITFILE.write('<layer>')
    KITFILE.write('<filename>'+INSTNAME[INSTNUM]+'</filename>')
    KITFILE.write('''
                <min>0</min>
                <max>1</max>
                <gain>1</gain>
                <pitch>0</pitch>
            </layer>
        </instrument>''')
    # increment instrument number
    INSTNUM=INSTNUM+1
 # that should be all the instruments now
# so its time to close the XML tree
KITFILE.write('</instrumentList>')
KITFILE.write('</drumkit_info>')
## apparently you need to flush() the file
## before closing it; thanks to nido for the tip
## and we have to fsync. thanks to goibniu.
KITFILE.flush()
os.fsync(KITFILE.fileno())
KITFILE.close

# i guess we should package it up now
# this is really clunky
# i know there is a better way to move files

os.makedirs(KITNAME+'Kit')
# DIRSRC = "."
DIRDEST = KITNAME+'Kit'

# print(DIRSRC)  ##  debug statements
# print(DIRDEST) ##

for DRUMFILE in os.listdir(UNIXPATH):
	if DRUMFILE.endswith(".flac"):
		SRCFILE = os.path.join(UNIXPATH, DRUMFILE)
		DESTFILE = os.path.join(DIRDEST, DRUMFILE)
		shutil.move(SRCFILE, DESTFILE)

for DRUMFILE in os.listdir(UNIXPATH):
	if DRUMFILE.endswith(".xml"):
		SRCFILE = os.path.join(UNIXPATH, DRUMFILE)
		DESTFILE = os.path.join(DIRDEST, DRUMFILE)
		shutil.move(SRCFILE, DESTFILE)

GNUTAR = tarfile.open(name=DIRDEST+'.h2drumkit'+'.tgz' , mode="w:gz")
GNUTAR.add(DIRDEST)
GNUTAR.close()
