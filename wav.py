import math
import struct

class Song:

    # Constants
    WAV_SAMPLES_PER_SECOND = 44100
    BEAT_LEN = WAV_SAMPLES_PER_SECOND / 4
    BITS_PER_SAMPLE = 16
    DECAY_DURATION = BEAT_LEN / 2
    DECAY_FACTOR = -5
    SILENCE_DURATION = 5
    VOLUME = 32000
    STRUCT_FMT = "c c c c i c c c c c c c c i h h i i h h c c c c i"

    def __init__(self, filename):
        """Initialize song with no notes."""
        self.filename = filename
        self.notes = []
        self.duration = 0

    def add_note(self, frequency, duration):
        """Add a note to end of current song."""
        self.notes.append((frequency, duration))
        self.duration += duration

    def add_rest(self, duration):
        """Add a rest to end of current song."""
        self.add_note(0, duration)

    def write(self):

        def wav_header():
            """Generate a binary-encoded RIFF header."""
            header = struct.Struct(Song.STRUCT_FMT)
            values = ["R".encode(), "I".encode(), "F".encode(), "F".encode(), 0,
                      "W".encode(), "A".encode(), "V".encode(), "E".encode(),
                      "f".encode(), "m".encode(), "t".encode(), " ".encode(),
                      16, 1, 1, Song.WAV_SAMPLES_PER_SECOND,
                      int(Song.WAV_SAMPLES_PER_SECOND * (Song.BITS_PER_SAMPLE / 8)),
                      int(Song.BITS_PER_SAMPLE / 8), Song.BITS_PER_SAMPLE,
                      "d".encode(), "a".encode(), "t".encode(), "a".encode(), 0]
            packed = header.pack(*values)
            return packed

        def wav_open(filename):
            """Open a new file and write the RIFF header to it."""
            header = wav_header()
            f = open(filename, "wb")
            f.write(header)
            return f

        def compute_waveform():
            """Calculate frequency for each sample in the song."""
            waveform = [0 for i in range(int(self.duration * Song.BEAT_LEN))]
            current_index = 0

            # Compute waveform values for each note.
            for frequency, duration in self.notes:
                phase = 0.0
                phase_step = (frequency * 2 * math.pi) / Song.WAV_SAMPLES_PER_SECOND

                # Determine length of note and length of decay.
                note_end_index = int(current_index + duration * Song.BEAT_LEN - Song.SILENCE_DURATION)
                decay_start_index = int(note_end_index - Song.DECAY_DURATION)

                # Add samples for playing the note at full volume.
                while (current_index != decay_start_index):
                    waveform[current_index] = round(Song.VOLUME * math.sin(phase))
                    current_index += 1
                    phase += phase_step

                # Decay note's volume after it's been played.
                while (current_index != note_end_index):
                    t = (current_index - decay_start_index) / Song.BEAT_LEN
                    waveform[current_index] = round(Song.VOLUME *
                        pow(math.e, t * Song.DECAY_FACTOR) * math.sin(phase))
                    current_index += 1
                    phase += phase_step

                # Add a brief silence at end of each note.
                current_index += Song.SILENCE_DURATION
            return waveform

        def wav_close(f):
            """Update header and close file."""

            # Update data_length header field
            file_length = f.tell()
            header_size = struct.calcsize(Song.STRUCT_FMT)
            data_length = file_length - header_size
            f.seek(header_size - 4, 0)
            f.write(struct.pack("i", data_length))

            # Update riff_length header field
            riff_length = file_length - 8
            f.seek(4, 0)
            f.write(struct.pack("i", riff_length))

            f.close()

        # Write header and waveform to file
        f = wav_open(self.filename)
        waveform = compute_waveform()
        for sample in waveform:
            f.write(struct.pack("h", sample))
        wav_close(f)

