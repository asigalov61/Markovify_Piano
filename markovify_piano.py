# -*- coding: utf-8 -*-
"""Markovify_Piano.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/asigalov61/Markovify-Piano/blob/main/Markovify_Piano.ipynb

# Markovify Piano (ver 3.0)

***

## Based upon absolutely amazing markovify package of @jsvine: https://github.com/jsvine/markovify

## Powered by tegridy-tools TMIDI 2.0 Optimus Processors

***

### Project Los Angeles
### Tegridy Code 2021

***

# Setup environment
"""

#@title Install dependencies
!git clone https://github.com/asigalov61/tegridy-tools
!pip install unidecode
!pip install tqdm
!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio

# packages below are for plotting pianoroll only
# they are not needed for anything else
!pip install pretty_midi
!pip install librosa
!pip install matplotlib

#@title Load needed modules
print('Loading needed modules. Please wait...')

import sys
import os
import json
import secrets

os.chdir('/content/tegridy-tools/tegridy-tools/')
import TMIDI
import markovify
os.chdir('/content/')

from pprint import pprint

import tqdm.auto

from midi2audio import FluidSynth
from IPython.display import display, Javascript, HTML, Audio

# only for plotting pianoroll
import pretty_midi
import librosa.display
import matplotlib.pyplot as plt

from google.colab import output, drive

print('Creating Dataset dir...')
if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

os.chdir('/content/')
print('Loading complete. Enjoy! :)')

"""# Download/upload desired MIDI dataset

## NOTE: Dataset must be sufficiently large and homogenous for Markov chain to train/perform properly.

# Pre-processed Dataset and Model
"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download and process World Piano Melodies Model (Recommended)

#@markdown NOTE: You can jump straight to music generation after running this code/cell. The model will be loaded and prepped for use.

#@markdown NOTE: This is a model without the velocity and MIDI channels, so make sure to turn-off the "encoding_has_velocities" and "encoding_has_MIDI_channels" options and turn on the "simulate_velocity option"
# %cd /content/

!wget --no-check-certificate -O Markovify-Piano-Melodies-Music-Model.zip "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118483&authkey=ABcsBJclHUenKxg"
!unzip -j Markovify-Piano-Melodies-Music-Model.zip

# %cd /content/

model_json = TMIDI.Tegridy_Any_Pickle_File_Loader('/content/Markovify-Piano-Music-Model-4')
markov_text_model = markovify.Text.from_json(model_json)

# Commented out IPython magic to ensure Python compatibility.
#@title Download World Melodies pre-processed dataset

#@markdown This dataset is great for melody generation or quick testing

#@markdown Works best stand-alone/as-is for the optimal results

#@markdown NOTE: This is a dataset without the velocity and MIDI channels, so make sure to turn-off the "encoding_has_velocities" and "encoding_has_MIDI_channels" options and turn on the "simulate_velocity option"

# %cd /content/

!wget 'https://github.com/asigalov61/Markovify-Piano/raw/main/Models-Datasets/Markovify-Piano-Music-TXT-Dataset.zip.001'
!wget 'https://github.com/asigalov61/Markovify-Piano/raw/main/Models-Datasets/Markovify-Piano-Music-TXT-Dataset.zip.002'

!cat Markovify-Piano-Music-TXT-Dataset.zip* > Markovify-Piano-Music-TXT-Dataset.zip
!unzip -j Markovify-Piano-Music-TXT-Dataset.zip

# %cd /content/

"""## MIDI Datasets"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download Special Tegridy Piano MIDI dataset

#@markdown Works best stand-alone/as-is for the optimal results
# %cd /content/Dataset/

!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Tegridy-Piano-CC-BY-NC-SA.zip'
!unzip -j '/content/Dataset/Tegridy-Piano-CC-BY-NC-SA.zip'
!rm '/content/Dataset/Tegridy-Piano-CC-BY-NC-SA.zip'

# %cd /content/

# Commented out IPython magic to ensure Python compatibility.
#@title Download Full Multi-Instrumental Tegridy MIDI dataset

#@markdown Works best stand-alone/as-is for the optimal results
# %cd /content/Dataset/

!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Tegridy-MIDI-Dataset-CC-BY-NC-SA.zip'
!unzip -j '/content/Dataset/Tegridy-MIDI-Dataset-CC-BY-NC-SA.zip'
!rm '/content/Dataset/Tegridy-MIDI-Dataset-CC-BY-NC-SA.zip'

# %cd /content/

"""# Process the MIDI dataset

## NOTE: If you are not sure what settings to select, please use original defaults
"""

#@title Process MIDIs to special MIDI dataset with Tegridy MIDI Processor
#@markdown NOTES:

#@markdown 1) Dataset MIDI file names are used as song names. Feel free to change it to anything you like.

#@markdown 2) Best results are achieved with the single-track, single-channel, single-instrument MIDI 0 files with plain English names (avoid special or sys/foreign chars)

#@markdown 3) MIDI Channel = -1 means all MIDI channels. MIDI Channel = 16 means all channels will be processed. Otherwise, only single indicated MIDI channel will be processed.

file_name_to_output_dataset_to = "/content/Markovify-Piano-Music-TXT-Dataset" #@param {type:"string"}
desired_MIDI_channel_to_process = 16 #@param {type:"slider", min:-1, max:16, step:1}
encode_MIDI_channels = True #@param {type:"boolean"}
encode_velocities = False #@param {type:"boolean"}
chordify_input_MIDIs = False #@param {type:"boolean"}
melody_conditioned_encoding = False #@param {type:"boolean"}
melody_pitch_baseline = 60 #@param {type:"slider", min:1, max:127, step:1}
time_denominator = 1 #@param {type:"slider", min:1, max:20, step:1}
chars_encoding_offset = 30000 #@param {type:"number"}

print('TMIDI Processor')
print('Starting up...')

###########

average_note_pitch = 0
min_note = 127
max_note = 0

files_count = 0

ev = 0

chords_list_f = []
melody_list_f = []

chords_list = []
chords_count = 0

melody_chords = []
melody_count = 0

TXT_String = 'DATASET=Optimus-Virtuoso-Music-Dataset' + chr(10)

TXT = ''
melody = []
chords = []
bf = 0
###########

print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset/"
os.chdir(dataset_addr)
filez = os.listdir(dataset_addr)

print('Processing MIDI files. Please wait...')
for f in tqdm.auto.tqdm(filez):
  try:
    fn = os.path.basename(f)
    fn1 = fn.split('.')[0]
    #notes = song_notes_list[song_notes_list.index(fn1)+1]


    files_count += 1
    TXT, melody, chords = TMIDI.Optimus_MIDI_TXT_Processor(f, 
                                                           line_by_line_output=False, 
                                                           chordify_TXT=chordify_input_MIDIs, 
                                                           output_MIDI_channels=encode_MIDI_channels, 
                                                           char_offset=chars_encoding_offset, 
                                                           dataset_MIDI_events_time_denominator=time_denominator, 
                                                           output_velocity=encode_velocities, 
                                                           MIDI_channel=desired_MIDI_channel_to_process,
                                                           MIDI_patch=range(0,127), 
                                                           melody_conditioned_encoding=melody_conditioned_encoding,
                                                           melody_pitch_baseline=melody_pitch_baseline)
    melody_list_f += melody
    chords_list_f += chords
    
    #TXT_String += 'INTRO=' + notes + '\n'
    TXT_String += TXT
  
  except KeyboardInterrupt:
    print('Exiting...Saving progress...')
    break

  except:
    bf += 1
    print('Bad MIDI:', f)
    print('Count:', bf)
    
    continue

print('Task complete :)')
print('==================================================')
print('Number of processed dataset MIDI files:', files_count)
print('Number of MIDI chords recorded:', len(chords_list_f))
print('First chord event:', chords_list_f[0], 'Last chord event:', chords_list_f[-1]) 
print('Number of recorded melody events:', len(melody_list_f))
print('First melody event:', melody_list_f[0], 'Last Melody event:', melody_list_f[-1])
print('Total number of MIDI events recorded:', len(chords_list_f) + len(melody_list_f))

# Writing dataset to TXT file
with open(file_name_to_output_dataset_to + '.txt', 'wb') as f:
  f.write(TXT_String.encode('utf-8', 'replace'))
  f.close

# Dataset
MusicDataset = [chords_list_f, melody_list_f]

# Writing dataset to pickle file
TMIDI.Tegridy_Pickle_File_Writer(MusicDataset, file_name_to_output_dataset_to)

"""# Load processed TXT MIDI dataset into memory"""

#@title Load/Reload processed TXT dataset
full_path_to_TXT_dataset = "/content/Markovify-Piano-Music-TXT-Dataset.txt" #@param {type:"string"}

print('Loading TXT MIDI dataset. Please wait...')
with open(full_path_to_TXT_dataset) as f:
    text = f.read()
print('Dataset loaded! Enjoy :)')

"""# Train TXT Markov chain/model"""

#@title Train Markov-chain/model
markov_chain_state_size = 5 #@param {type:"slider", min:1, max:30, step:1}

print('Training Markov chain/model. Please wait...')
markov_text_model = markovify.NewlineText(text, well_formed=False, state_size=markov_chain_state_size)

print('Compiling model...')
markov_text_model.compile(inplace=True)

print('Model is ready! Enjoy :)')

#@title Save the model
full_path_to_json_save_file = "/content/Markovify-Piano-Music-Model.json" #@param {type:"string"}
legacy_model = False #@param {type:"boolean"}

print('Converting model to json...')
model_json = markov_text_model.to_json()

if legacy_model == False:
  TMIDI.Tegridy_Pickle_File_Writer(model_json, full_path_to_json_save_file)

else:
  print('Saving model as json file...')
  with open(full_path_to_json_save_file, 'w') as f:
      json.dump(model_json, f)

print('Task complete! Enjoy! :)')

#@title Load/Re-load saved model
full_path_to_json_save_file = "/content/Markovify-Piano-Music-Model.json" #@param {type:"string"}
legacy_model = False #@param {type:"boolean"}

if legacy_model == False:
  model_json = TMIDI.Tegridy_Any_Pickle_File_Loader(full_path_to_json_save_file)

else:

  print('Loading model from json file...')
  f = open(full_path_to_json_save_file)
  model_json = json.load(f)

print('Restoring the model...')
markov_text_model = markovify.Text.from_json(model_json)

print('Model loaded and restored! Enjoy! :)')

"""# Generate music composition"""

#@title Generate Music

#@markdown HINT: Each note = 3-5 characters depending on the MIDI processing settings above

#@markdown NOTE: If nothing is being generated after 5 attempts, try again with different model state # and generation settings

#@markdown NOTE: For practical purposes only the longest attempt is returned.

minimum_number_of_characters_to_generate = 150 #@param {type:"slider", min:50, max:1500, step:100}
minimum_notes_to_generate = 500 #@param {type:"slider", min:10, max:5000, step:10}
number_of_cycles_to_try_to_generate_desired_result = 5000 #@param {type:"slider", min:10, max:10000, step:10}
overlap_ratio = 0.6 #@param {type:"slider", min:0.1, max:0.95, step:0.05}
max_overlap_notes_total = 100 #@param {type:"slider", min:1, max:200, step:1}
let_run_wild = False #@param {type:"boolean"}
full_path_to_input_MIDI_file = "" #@param {type:"string"}
enable_plagiarizm_check = True #@param {type:"boolean"}
print_generated_song = False #@param {type:"boolean"}

Output_TXT_String = ''

attempt = 0

print('Generating music composition. Please wait...')

while (len(Output_TXT_String.split(' ')[1:])-2) < minimum_notes_to_generate:
  
  if not let_run_wild:
    if full_path_to_input_MIDI_file == '':
      out = markov_text_model.make_sentence(min_chars=minimum_number_of_characters_to_generate, 
                              tries=number_of_cycles_to_try_to_generate_desired_result,
                              max_overlap_ratio=overlap_ratio, 
                              test_output=enable_plagiarizm_check,
                              max_overlap_total=max_overlap_notes_total)
    else:
      T, C, M = TMIDI.Optimus_MIDI_TXT_Processor(full_path_to_input_MIDI_file, line_by_line_output=False, output_velocity=False)
      TXT = T.split()
      out = markov_text_model.make_sentence_with_start(' '.join(TXT[-2:-1]), strict=False, min_chars=minimum_number_of_characters_to_generate, 
                              tries=number_of_cycles_to_try_to_generate_desired_result,
                              max_overlap_ratio=overlap_ratio, 
                              test_output=enable_plagiarizm_check,
                              max_overlap_total=max_overlap_notes_total)   
  
  else:
    if full_path_to_input_MIDI_file == '':
      out = markov_text_model.make_sentence(test_output=enable_plagiarizm_check)
    else:
      T, C, M = TMIDI.Optimus_MIDI_TXT_Processor(full_path_to_input_MIDI_file, line_by_line_output=False, output_velocity=False)
      TXT = T.split()
      out = markov_text_model.make_sentence_with_start(' '.join(TXT[-2:-1]), strict=False)   
   
  if out == None: out = ''  
  
  if len(''.join(out)) > len(Output_TXT_String):
    Output_TXT_String = ''.join(out)
  print('Attempt #', attempt)
  attempt += 1
  
  if attempt > 5:
    break

if out != '':

  print('Generation complete!')
  print('=' * 70)
  print(Output_TXT_String.split(' ')[0], 'with', len(Output_TXT_String.split(' ')[1:])-2, 'notes.')
  print('=' * 70)

  if print_generated_song:
    pprint(Output_TXT_String)
    print('=' * 70)
else:
  print('Could not generate anything. Try again and/or change the generation settings.')

"""# Convert generated music composition to MIDI file and download/listen to the output :)"""

#@title Convert to MIDI from TXT (w/Tegridy MIDI-TXT Processor)

#@markdown Standard MIDI timings are 400/120(80)

'''For debug:'''

#fname = '/content/Optimus-VIRTUOSO-Composition-generated-on-2021-02-25_00_45_41_715972'
#with open(fname + '.txt', 'r') as f:
#  completion = f.read()
fname = '/content/Markovify-Piano-Music-Composition'
completion = Output_TXT_String

#completion = TXT_String[:1500]


number_of_ticks_per_quarter = 420 #@param {type:"slider", min:10, max:500, step:10}
dataset_time_denominator = 1 #@param {type:"slider", min:1, max:20, step:1}
encoding_has_MIDI_channels = True #@param {type:"boolean"}
encoding_has_velocities = False #@param {type:"boolean"}
simulate_velocity = True #@param {type:"boolean"}
chars_encoding_offset_used_for_dataset = 30000 #@param {type:"number"}

print('Converting TXT to MIDI. Please wait...')
print('Converting TXT to Song...')
output_list, song_name = TMIDI.Tegridy_Optimus_TXT_to_Notes_Converter(completion, 
                                                                has_MIDI_channels=encoding_has_MIDI_channels, 
                                                                simulate_velocity=simulate_velocity,
                                                                char_encoding_offset=chars_encoding_offset_used_for_dataset,
                                                                save_only_first_composition=True,
                                                                dataset_MIDI_events_time_denominator=dataset_time_denominator,
                                                                has_velocities=encoding_has_velocities,
                                                                line_by_line_dataset=False)

print('Converting Song to MIDI...')

output_signature = 'Markovify Piano'

detailed_stats = TMIDI.Tegridy_SONG_to_MIDI_Converter(output_list,
                                                      output_signature = output_signature,  
                                                      output_file_name = fname, 
                                                      track_name=song_name, 
                                                      number_of_ticks_per_quarter=number_of_ticks_per_quarter,
                                                      )

print('Done!')

print('Downloading your composition now...')
from google.colab import files
files.download(fname + '.mid')

print('Detailed MIDI stats:')
detailed_stats

#@title Plot and listen to the last generated composition
#@markdown NOTE: May be very slow with the long compositions
fn = os.path.basename(fname + '.mid')
fn1 = fn.split('.')[0]
print('Playing and plotting composition...')

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', sr=64000, cmap=plt.cm.hot)
plt.title('Composition: ' + fn1)

print('Synthesizing the last output MIDI. Please stand-by... ')
FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)