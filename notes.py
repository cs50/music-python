import sys
from helpers import frequency
from wav import Song

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def main():
    if len(sys.argv) > 2:
        print("Usage: python notes.py OCTAVE")
        sys.exit(1)

    octave = int(sys.argv[1]) if len(sys.argv) == 2 else 4
    if octave < 0 or octave > 7:
        print("Invalid octave.")
        sys.exit(1)

    s = Song("notes.wav")

    for note in NOTES:
        note += str(octave)
        f = frequency(note)
        print(f"{note}: {f}")
        s.add_note(f, 1)

    s.write()

if __name__ == "__main__":
    main()
