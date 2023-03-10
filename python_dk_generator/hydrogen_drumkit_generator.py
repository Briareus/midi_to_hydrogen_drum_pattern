import sys
import os
import shutil
import tarfile
import xml.etree.ElementTree as ET
import pprint
import glob
import ntpath
import re
import json
import ffmpeg
import subprocess

# configuration
pp = pprint.PrettyPrinter(indent=4)

# main folder
top_dir = 'dk_files/'
# input dir

flac_dir = 'eclectic'
output_dir = flac_dir + '_dk'

AUTO_ADJUST_PITCH = True
AUTO_ADJUST_PITCH_FILES = True
AUTO_ASSIGN_MIDI_NOTES = True

#default pitch adj values
DEFAULT_PITCH_ADJ_VALUES = {"low": -4, "mid": 0, "high": 4}


# functions
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def adjust_pitch(inst, pitch_adj_values = None, pitch_type = None):
    pitch_adj = pitch_adj_values
    if not pitch_adj_values:    
        pitch_adj = DEFAULT_PITCH_ADJ_VALUES
    return pitch_adj.get(pitch_type, 0)

def truncate_audio_file(input_file, output_file, t_length = 1):
    process = (
        ffmpeg
        .input(input_file, t=t_length)
        .output(output_file)
        .overwrite_output()
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    out, err = process.communicate()
    # print(f'output: {out}')
    # print(f'err: {err}')

def create_tar(path, tar_name):
    with tarfile.open(tar_name, "w:gz") as tar_handle:
        for root, dirs, files in os.walk(path):
            for file in files:
                tar_handle.add(os.path.join(root, file))

print('Starting test conversion...')

# get pwd from args

# create output dir if it does not exist
output_path = top_dir + output_dir
if not os.path.exists(output_path):
    os.mkdir(output_path)


dk_file = 'drumkit.xml'
dk_config_file_path = top_dir + flac_dir + '/dk_config.json'
print(dk_file)

types = ('/*.flac', '/*.wav') # the tuple of file types
files_grabbed = []
for files in types:
    file_path = top_dir + flac_dir + files
    files_grabbed.extend(glob.glob(file_path))
files_grabbed.sort()
flac_file_list = list(map(path_leaf, files_grabbed))
pp.pprint(flac_file_list)


# check for config file

if os.path.exists(dk_config_file_path):
    print(f'dk_config file path: {dk_config_file_path}')
    with open(dk_config_file_path) as config_file:
        dk_config_dict = json.load(config_file)

pp.pprint(dk_config_dict)


# set dict values from inputs

if dk_config_dict:
    AUTO_ADJUST_PITCH_FILES = dk_config_dict.get('auto_adjust_pitch', False)
    AUTO_ASSIGN_MIDI_NOTES = dk_config_dict.get('auto_assign_midi_notes', False)
    

if dk_config_dict:
    if dk_config_dict.get('truncate_sound_files', 0) > 0:
        trun_len = dk_config_dict.get('truncate_sound_files', 0)
        trunc_list = []
        for audio_file in flac_file_list:
            input_file = top_dir + flac_dir + '/' + audio_file
            trunc_list.append('t_' + audio_file)
            output_file = output_path + '/t_' + audio_file
            truncate_audio_file(input_file, output_file, trun_len)
        flac_file_list = trunc_list
    pp.pprint(flac_file_list)    


dk_dict = {}
# AUTO_ADJUST_PITCH_FILES = False
if AUTO_ADJUST_PITCH_FILES:
    ffl_cutoff = int(len(flac_file_list)/3)
    print(f'length of ffl: {ffl_cutoff}')
    for i, instrument in enumerate(flac_file_list):
        if i <= ffl_cutoff:
            dk_dict[instrument] = {'pitch':'low'}
        if i > ffl_cutoff and i < (ffl_cutoff * 2):
            dk_dict[instrument] = {'pitch':'mid'}
        if i >= (ffl_cutoff * 2):
            dk_dict[instrument] = {'pitch':'high'}
else:
    for inst in flac_file_list:
        dk_dict[inst] = {'pitch':'mid'}

if AUTO_ASSIGN_MIDI_NOTES:
    for i, instrument in enumerate(flac_file_list):
        midi_note = 24 + i
        params = dk_dict.get(instrument)
        params['midi'] = midi_note
        # dk_dict[instrument] = {'midi':midi_note}


if dk_config_dict:
    inst_counter = 1
    for inst, params in dk_dict.items():
        inst_name_prefix = dk_config_dict.get('inst_name_prefix', "Instrument")
        params['inst_name'] = inst_name_prefix + ' ' + str(inst_counter) + " " + params.get('pitch', 'Original')
        inst_counter += 1

pp.pprint(dk_dict)

# xml generation

# This is the parent (root) tag
# onto which other tags would be
# created
dk_root = ET.Element('drumkit_info')
kit_name = ET.SubElement(dk_root, 'name')
if dk_config_dict:
    kit_name.text = dk_config_dict.get('kit_name',flac_dir + '_drumkit')
kit_author = ET.SubElement(dk_root, 'author')
kit_author.text = 'Clayton Corrello'
kit_info = ET.SubElement(dk_root, 'info')
if dk_config_dict:
    kit_info.text = dk_config_dict.get('kit_desc','Autogenerated drumkit')
kit_license = ET.SubElement(dk_root, 'license')
kit_license.text = 'GPLv3'
inst_list = ET.SubElement(dk_root, 'instrumentList')

inst_counter = 0
for instrument,params in dk_dict.items():
    inst = ET.SubElement(inst_list, 'instrument')
    inst_id = ET.SubElement(inst, 'id')
    inst_id.text = str(inst_counter)
    inst_name = ET.SubElement(inst, 'name')
    inst_name.text = params.get('inst_name', os.path.splitext(instrument)[0])    
    inst_vol = ET.SubElement(inst, 'volume')
    inst_vol.text = '1'
    inst_muted = ET.SubElement(inst, 'isMuted')
    inst_muted.text = 'false'
    inst_pan_left = ET.SubElement(inst, 'pan_L')
    inst_pan_left.text = '1'
    inst_pan_right = ET.SubElement(inst, 'pan_R')
    inst_pan_right.text = '1'
    inst_rand_pitch_fact = ET.SubElement(inst, 'randomPitchFactor')
    inst_rand_pitch_fact.text = '0'
    inst_filter_active = ET.SubElement(inst, 'filterActive')
    inst_filter_active.text = 'false'
    inst_filter_cutoff = ET.SubElement(inst, 'filterCutoff')
    inst_filter_cutoff.text = '1'
    inst_filter_resonance = ET.SubElement(inst, 'filterResonance')
    inst_filter_resonance.text = '0'
    inst_attack = ET.SubElement(inst, 'Attack')
    inst_attack.text = '0'
    inst_decay = ET.SubElement(inst, 'Decay')
    inst_decay.text = '0'
    inst_sustain = ET.SubElement(inst, 'Sustain')
    inst_sustain.text = '1'
    inst_release = ET.SubElement(inst, 'Release')
    inst_release.text = '1000'
    inst_exclude = ET.SubElement(inst, 'exclude')
    inst_midi_out = ET.SubElement(inst, 'midiOutNote')
    midi_out = params.get('midi',60)
    inst_midi_out.text = str(midi_out)

    #layer
    layer = ET.SubElement(inst, 'layer')
    layer_filename = ET.SubElement(layer, 'filename')
    layer_filename.text = instrument

    layer_min = ET.SubElement(layer, 'min')
    layer_min.text = '0'
    layer_max = ET.SubElement(layer, 'max')
    layer_max.text = '1'
    layer_gain = ET.SubElement(layer, 'gain')
    layer_gain.text = '1'
    layer_pitch = ET.SubElement(layer, 'pitch')
    pitch_adj = DEFAULT_PITCH_ADJ_VALUES
    if dk_config_dict:
        pitch_adj = dk_config_dict.get('pitch_adjustment_values',DEFAULT_PITCH_ADJ_VALUES)
    adj_pitch = adjust_pitch(instrument, pitch_adj, params.get('pitch', 'mid'))
    layer_pitch.text = str(adj_pitch)
    inst_counter +=1


# Converting the xml data to byte object,
# for allowing flushing data to file
# stream
dk_xml = ET.tostring(dk_root)



output_xml_file = output_path + '/' + dk_file
print(f'Output dir: {output_xml_file}')
with open(output_xml_file, "wb") as f:
    f.write(dk_xml)

# dk_tar_file = tarfile.open(name=top_dir + flac_dir +'.h2drumkit' , mode="w:gz")
# dk_tar_file.add(output_path)
# dk_tar_file.close()

os.chdir(top_dir)
cwd = os.getcwd()
print(cwd)
tarname = flac_dir +'.h2drumkit'
create_tar(output_dir, tarname)

os.chdir('../')
cwd = os.getcwd()
print(cwd)

print(top_dir + tarname)
os.rename(top_dir + tarname, cwd + '/' + tarname)

print(f'Drumkit generated: {tarname}')