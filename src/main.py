import random
import music21

#A function that generates a chord given the pitches of a scale and the position (rank) of a note in the scale
def generate_chord(scale_pitches, rank):
    chord = music21.chord.Chord([scale_pitches[rank], scale_pitches[(rank+2) % len(scale_pitches)], scale_pitches[(rank+4) % len(scale_pitches)]])
    chord.duration.quarterLength = 2
    return chord


#Load a MIDI file as an input for training the 2nd order Markov chain
input_file = 'midi/godfather.mid'
input = music21.converter.parse(input_file)


#Extract the pitches from the Piano melody part as the musical states
pitches = [n.pitch for n in input.parts[1].flatten().notes if isinstance(n, music21.note.Note)]

#Choose the key of the output scale
key = "C3"

#Define the scale and the mode of the output (C minor scale in our case)
c_minor_scale = music21.scale.MinorScale(key)

#Get the pitches of the C minor scale
c_minor_pitches = c_minor_scale.getPitches()

#Build the transition matrix
transition_matrix = {}

#Iterate through the pitches to build the transition matrix
for i in range(len(pitches) - 2):
    current_pitch = pitches[i]
    next_pitch = pitches[i + 1]
    next_next_pitch = pitches[i + 2]
    if (current_pitch, next_pitch) not in transition_matrix:
        transition_matrix[(current_pitch, next_pitch)] = {}

    if next_next_pitch not in transition_matrix[(current_pitch, next_pitch)]:
        transition_matrix[(current_pitch, next_pitch)][next_next_pitch] = 0

    transition_matrix[(current_pitch, next_pitch)][next_next_pitch] += 1


#Calculate the probabilities of the Markov Chain transistions
for current_pitches in transition_matrix:
    total = sum(transition_matrix[current_pitches].values())
    for next_pitch in transition_matrix[current_pitches]:
        transition_matrix[current_pitches][next_pitch] /= total

#Set the 2 starting pitches for generating the music
starting_pitches = (random.choice(list(transition_matrix.keys())))

#Generate a sequence of pitches using the second-order Markov chain
#The sequence should be enough to populate num_measures
generated_pitches = list(starting_pitches)
num_measures = 20

for i in range(2*(num_measures*4)):
    current_pitches = tuple(generated_pitches[-2:])
    next_pitches = list(transition_matrix[current_pitches].keys())
    probabilities = list(transition_matrix[current_pitches].values())
    #Randomly choose the next pitch based on the transition probabilities
    next_pitch = random.choices(next_pitches, probabilities)[0]
    generated_pitches.append(next_pitch)

#Pitch durations patterns
pitch_patterns = [
    [1, 1, 1, 1],
    [0.5, 1, 0.5, 0.5, 0.5, 1],
    [0.5, 0.5, 1, 1, 0.5, 0.5],
    [1, 1, 0.5, 0.5, 1]
    #We can add more in the future
]

###Create the melody
melody = music21.stream.Part()
current_measure = 1
pitch = 0
while(current_measure <= 20):
    pattern = random.choice(pitch_patterns)
    for dur in pattern:
        note_obj = music21.note.Note()
        note_obj.pitch = generated_pitches[pitch]
        note_obj.duration.quarterLength = dur
        melody.append(note_obj)
        pitch += 1
    current_measure += 1

melody.insert(0, music21.instrument.Flute())


###Create the accompainment chords
#I chose the i iv i v succession
accompany_chords = music21.stream.Part()
for i in range(num_measures):
    if i%2 == 0:
        accompany_chords.append(generate_chord(c_minor_pitches, 0))
        accompany_chords.append(generate_chord(c_minor_pitches, 3))
    else:
        accompany_chords.append(generate_chord(c_minor_pitches, 0))
        accompany_chords.append(generate_chord(c_minor_pitches, 4))

accompany_chords.insert(0, music21.instrument.Piano())


###Create the drums part
drums_part = music21.stream.Part()

for i in range(num_measures):
    drums_part.append(music21.chord.Chord([music21.note.Note('G2', type='eighth'), music21.note.Note('G3', type='eighth')]))
    drums_part.append(music21.note.Note('G3', type='eighth'))
    drums_part.append(music21.chord.Chord([music21.note.Note('D3', type='eighth'), music21.note.Note('G3', type='eighth')]))
    drums_part.append(music21.note.Note('G3', type='eighth'))
    drums_part.append(music21.chord.Chord([music21.note.Note('G2', type='eighth'), music21.note.Note('G3', type='eighth')]))
    drums_part.append(music21.chord.Chord([music21.note.Note('G2', type='eighth'), music21.note.Note('G3', type='eighth')]))
    drums_part.append(music21.chord.Chord([music21.note.Note('D3', type='eighth'), music21.note.Note('G3', type='eighth')]))
    drums_part.append(music21.note.Note('G3', type='eighth'))
    
drums_part.insert(0, music21.instrument.BassDrum())


###Create the score
score = music21.stream.Score()
score.append(melody)
score.append(accompany_chords)
score.append(drums_part)

tempo = music21.tempo.MetronomeMark(number=80)
score.insert(0, tempo)

#Save the generated music as a MIDI file
output_file = 'midi/output3.mid'
score.write('midi', fp=output_file)

#Confirm the successful generation of the output file
print("MIDI file generated:", output_file)
