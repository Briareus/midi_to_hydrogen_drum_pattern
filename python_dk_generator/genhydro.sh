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

UNIXPATH = os.getcwd()
PATHARRAY = UNIXPATH.split('/')
CWDNUM = len(PATHARRAY)-1
KITNAME = PATHARRAY[CWDNUM]
# print(KITNAME) ## debug statement

# now we have KITNAME as name for the kit
# lets build the head of the file

KITFILE = open("drumkit.xml", 'w')
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

INSTNUM=0
# reload file list
INSTNAME = filter(lambda x: x.endswith('.flac'), os.listdir(UNIXPATH))
INSTNAME.sort()
#print(INSTNAME) #### debug statement
# lets parse the instruments into XML

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
print('xml closing') ## debugging
KITFILE.write('</instrumentList>')
KITFILE.write('</drumkit_info>')

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

GNUTAR = tarfile.open(name=DIRDEST+'.tar.gz', mode="w:gz")
GNUTAR.add(DIRDEST)
GNUTAR.close()
