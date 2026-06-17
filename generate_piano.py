import argparse
import re
import sys

NOTE_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}

NOTE_RE = re.compile(r"^([A-G](?:#)?)(\d+)$")


def parse_direction(direction):
    direction = direction.upper()

    if direction == "X" or direction == "+X":
        return (1, 0, 0)
    if direction == "-X":
        return (-1, 0, 0)

    if direction == "Y" or direction == "+Y":
        return (0, 1, 0)
    if direction == "-Y":
        return (0, -1, 0)

    if direction == "Z" or direction == "+Z":
        return (0, 0, 1)
    if direction == "-Z":
        return (0, 0, -1)

    raise ValueError(f"Invalid direction: {direction}")


def note_to_minecraft_pitch(note):
    """
    Minecraft note 0 = F#3
    Minecraft note 24 = F#5
    """

    m = NOTE_RE.fullmatch(note)
    if not m:
        raise ValueError

    note_name = m.group(1)
    octave = int(m.group(2))

    midi = (octave + 1) * 12 + NOTE_TO_SEMITONE[note_name]
    mc_pitch = midi - 54

    if not (0 <= mc_pitch <= 24):
        raise ValueError(
            f"Note {note} is outside Minecraft note block range "
            f"(F#3 to F#5)"
        )

    return mc_pitch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--init_coords",
        nargs=3,
        type=int,
        required=True,
        metavar=("X", "Y", "Z"),
    )
    parser.add_argument(
        "--dir",
        required=True,
    )

    args = parser.parse_args()

    x, y, z = args.init_coords
    dx, dy, dz = parse_direction(args.dir)

    current_under_block = None

    for raw_line in sys.stdin:
        line = raw_line.split("$", 1)[0].strip()

        if line:
            parts = line.split()

            if len(parts) in (1, 2):
                note = parts[0]

                try:
                    pitch = note_to_minecraft_pitch(note)

                    if len(parts) == 2:
                        block_spec = parts[1]

                        if block_spec.lower() == "none":
                            current_under_block = None
                        else:
                            current_under_block = block_spec

                    if current_under_block is not None:
                        print(
                            f"setblock {x} {y-1} {z} {current_under_block}"
                        )

                    print(
                        f"setblock {x} {y} {z} "
                        f"minecraft:note_block[note={pitch}]"
                    )

                except ValueError:
                    pass

        x += dx
        y += dy
        z += dz


if __name__ == "__main__":
    main()