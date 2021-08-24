import regex as re


import os

import numpy as np

class InvalidNoteError(Exception):
    def __init__(self, not_note):
        self.not_note = not_note
        self.message = self.not_note + " is not a valid note."

    def __str__(self):
        return self.message

class IllegalArgumentException(Exception):
    def __init__(self, message):
        self.message = message
      
    def __str__(self):
        return self.message

class IllegalScaleException(Exception):
  def __init__(self, message):
      self.message = message
  
  def __str__(self):
      return self.message

def get_major(first_note, note_numbers, accidentals):
    next = {
        'c': 'd',
        'd': 'e',
        'e': 'f',
        'f': 'g',
        'g': 'a',
        'a': 'b',
        'b': 'c'
    }
    gaps = [2, 2, 1, 2, 2, 2]
    first_num = note_numbers[first_note]
    scale_nums = [first_num]
    for i in gaps:
        scale_nums.append(scale_nums[-1] + i)

    scale = [first_note]
    letter = first_note[:first_note.index(" ")]
    for i in scale_nums[1:]:
        next_letter = next[letter]
        possibilities = []
        for accidental in accidentals:
            possibilities.append(next_letter + " " + accidental)
        # print(possibilities)
        for j in possibilities:
            if note_numbers[j] % 12 == i % 12:
                scale.append(j)
                break
        letter = next_letter
        # print("i", i, "note", scale[-1])

    return scale, scale_nums

def MIDI_to_frequency(midi_code):
  return 440 * 2**((midi_code - 69)/12)

def play_melody(midi_melody, framerate=11250, durations=None, amplitudes=None):
  if durations is None:
    durations=np.ones_like(midi_melody).astype(float)
  if amplitudes is None:
    amplitudes=np.ones_like(midi_melody).astype(float)
  print("Durations", durations, "Amplitudes", amplitudes)
  freqs = []
  waves = []
  for note in midi_melody:
    freqs.append(MIDI_to_frequency(note))
  frequency = 0
  while frequency < len(freqs):
    waves.append(SinSignal(freq=frequency, amp=amplitudes[frequency], offset=0).make_wave(duration=durations[frequency], framerate = framerate))
    frequency += 1

  arrays = []
  for i in waves:
    arrays.append(i.ys)

  print("arrays[0] type", type(arrays[0]), "shape", arrays[0].shape)
  combined = np.concatenate(arrays, axis = -1)
  print("combined type", type(combined), "shape", combined.shape)
  print("Frequencies", freqs)
  return combined

def validate(yes_or_no):
  lower = yes_or_no.lower()
  if re.match("^([yn]|yes|no)$", lower):
    return lower
  else:
    raise IllegalArgumentException("Please enter yes or no")


def guess_the_mode():
    notes = []
    note = 'a'
    while ord(note) <= ord('g'):
        notes.append(note + " natural")
        notes.append(note + " flat")
        notes.append(note + " sharp")
        notes.append(note + " double flat")
        notes.append(note + " double sharp")
        note = chr(ord(note) + 1)
    
    note_numbers = {
        'c natural': 60,
        'd natural': 62,
        'e natural': 64,
        'f natural': 65,
        'g natural': 67,
        'a natural': 69,
        'b natural': 71
    }
    accidentals = {
        'sharp': 1,
        'flat': -1,
        'double sharp': 2,
        'double flat': -2,
        'natural': 0
    }
    for note in notes:
        if note in note_numbers:
            continue
        letter = note[:note.index(" ")]
        chromatic = note[note.index(" ") + 1:]
        note_numbers[note] = (note_numbers[letter + " natural"] +
                              accidentals[chromatic])
    
    # print("Length should be 35, it is ", len(note_numbers))
    
    first_note = input(
        "What is the first note of the scale? Enter the note and the chromatic sign\nif applicable, e.g. B flat or E sharp (not case-sensitive). The supported\naccidentals are natural, sharp, flat,\ndouble sharp, and double flat\n"
    ).lower()
    
    if re.match("^[a-g]$", first_note):
      first_note += " natural"
    
    if not re.match(
            "[A-Ga-g] ((([Dd][Oo][Uu][Bb][Ll][Ee] )?[Ss][Hh][Aa][Rr][Pp])|(([Dd][Oo][Uu][Bb][Ll][Ee] )?[Ff][Ll][Aa][Tt])|([Nn][Aa][Tt][Uu][Rr][Aa][Ll]))",
            first_note):
        raise InvalidNoteError(first_note)\
    
    notes, midi_codes = get_major(first_note, note_numbers, accidentals)
    print("--------------------")
    for i in notes:
        print(i)
    
    sharps = 0
    flats = 0
    
    change_or_continue = validate(input("Do you need to change any notes (not case sensitive)? (y/n)\n"))
    original_notes = notes.copy()
    while change_or_continue == "y":
      note = input("What is the new note? Use the same naming format as before, but remember the letter name needs to stay the same, e.g. moving e flat down by a semitone produces e doubleflat, not d natural.\n").lower()
      print("-------------")
      if re.match("^[a-g]$", note):
        note += " natural"
      if not re.match("[a-g] (((double )?sharp)|((double )?flat)|(natural))", note):
        raise InvalidNoteError(note)
      letter = note[:note.index(" ")]
      accidental = note[note.index(" ") + 1:]
      i = 0
      found_it = False
      while i < len(notes):
        if re.match("^" + letter, notes[i]):
          found_it = True
          if accidentals[original_notes[i][original_notes[i].index(" ") + 1:]] - accidentals[accidental] == 1:
            flats += 1
            midi_codes[i] -= 1
          elif accidentals[original_notes[i][original_notes[i].index(" ") + 1:]] - accidentals[accidental] == -1:
            sharps += 1
            midi_codes[i] += 1
          elif accidentals[original_notes[i][original_notes[i].index(" ") + 1:]] - accidentals[accidental] == 0:
            print("You probably meant to enter something else, as you didn't change anything.")
            pass
          else:
            raise IllegalArgumentException("It is not possible for to have the note " + note + " in a scale starting on " + notes[0])
          notes[i] = note
        i += 1
      if not found_it:
        raise IllegalArgumentException(note + " is not a note in the scale. Remember the letter name needs to stay the same, e.g. moving e flat down by a semitone produces e doubleflat, not d natural.")
      for i in notes:
        print(i)
      change_or_continue = validate(input("Do you still need to change any notes? (y/n)\n"))
    
    
    # Number of semitones between the notes
    modes = {"221222":"Ionian", "212221":"Dorian", "122212":"Phyrgian", "222122":"Lydian", "221221":"Mixolydian", "212212":"Aeolian", "122122":"Locrian"}
    
    gaps = ""
    i = 1
    while i < len(notes):
      gaps += str(midi_codes[i] - midi_codes[i-1])
      i += 1
    
    # print(gaps)
    mode = modes.get(gaps, "Wrong")
    print("----------------")
    print("----------------")
    if mode!="Wrong":
      print("Your scale is in the " + mode + " mode.")
      if sharps == 1:
        print("Your scale has one sharp in " + first_note + ", which is equivalent to having six flats\nin another key (it's the key a semitone up, e.g. having one sharp in f is\nlike having six flats in f sharp). The formula is # of flats\ndivided by 2 + 1, which tells you the number of the mode.")
        print("6/2 + 1 = 4.")
        num_mode = 4
      else:
        print("Your scale has " + str(flats) + " flats.\nThe formula is # of flats divided by 2 + 1, which\ntells you the number of the mode. Remember to add 7 to the number of flats\nif it's odd (this works because the scale is based on 7 notes).")
        if flats % 2 == 1:
          flats += 7
          print(str(flats -7) + " + 7 = " + str(flats))
        num_mode = 0.5 * flats + 1
        print(str(flats) + " / 2 + 1 = " + str(int(num_mode)))
      num_mode = int(num_mode)
      for i in range(num_mode):
        print(i + 1, list(modes.values())[i] if i != num_mode - 1 else list(modes.values())[i].upper())

      print("If you don't understand why this works, read the README in this directory/folder.")

    else:
      raise IllegalScaleException("No mode exists with the gaps:\n" + gaps)
    
    # see_all = validate(input("Would you like to see a list of all modes? y/n\n").lower())
    # if see_all:
    #   for i in modes:
    #     print(i, list(mode.values())[i])
    
    
    
    
if __name__=="__main__":
	guess_the_mode()
