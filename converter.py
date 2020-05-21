import ffmpeg
import os.path
import sys
import time

from argparse import ArgumentParser
from gooey import Gooey, GooeyParser


@Gooey(
    program_name="Video Converter",
    program_description="Convert between different video formats",
    default_size=(600, 720),
    navigation="TABBED",
    progress_regex=r"^Progress (\d+)$",
)
def main():
    parser = GooeyParser()
    subs = parser.add_subparsers(help="commands", dest="command")
    converter = subs.add_parser(
        "file_convert", prog="File convert",
    ).add_argument_group("")
    converter.add_argument(
        "input_file",
        metavar="Input file",
        help="File to be converted",
        widget="FileChooser",
        gooey_options=dict(
            wildcard="Video files (*.mp4, *.mkv)|*.mp4;*.mkv", full_width=True,
        ),
    )
    converter.add_argument(
        "output_file",
        metavar="Output file",
        help="Path for the converted file",
        widget="FileSaver",
        gooey_options=dict(
            wildcard="MPEG-4 (.mp4)|*.mp4|Matroska (.mkv)|*.mkv", full_width=True,
        ),
    )

    batch_converter = subs.add_parser(
        "batch_convert", prog="Batch convert", help="Convert multiple files"
    )
    batch_group = batch_converter.add_argument_group("")
    batch_group.add_argument(
        "input_files",
        metavar="Input files",
        help="List of files to convert",
        widget="MultiFileChooser",
        gooey_options=dict(
            wildcard="Video files (*.mp4, *.mkv)|*.mp4;*.mkv", full_width=True,
        ),
    )
    batch_group.add_argument(
        "output_directory",
        metavar="Output directory",
        help="Directory for file output",
        widget="DirChooser",
        gooey_options=dict(full_width=True,),
    )
    batch_conversion_settings = batch_converter.add_argument_group(
        "Conversion settings"
    )
    filename_group = batch_conversion_settings.add_mutually_exclusive_group(
        required=True,
        gooey_options=dict(title="Choose the file naming scheme", full_width=True,),
    )
    filename_group.add_argument(
        "--original_filename", metavar="Keep original filename", action="store_true"
    )
    filename_group.add_argument(
        "--file_prefix",
        metavar="Create a sequence",
        help="Choose file prefix",
        widget="TextField",
        default="video",
    )
    file_extension_group = batch_conversion_settings.add_argument(
        "--file_extension",
        metavar="File extension",
        required=True,
        widget="Dropdown",
        choices=[".mp4", ".mkv"],
        default=".mp4",
    )

    args = parser.parse_args()
    run(args)


def run(args):
    if args.command == "file_convert":
        convert(args.input_file, args.output_file)
    elif args.command == "batch_convert":
        if args.original_filename:
            file_prefix = None
        else:
            file_prefix = args.file_prefix

        convert_multiple(
            args.input_files, args.output_directory, args.file_extension, file_prefix,
        )


def convert_multiple(infiles, outdir, file_extension, file_prefix):
    input_files = infiles.split(";")

    for index, infile in enumerate(input_files):
        if file_prefix:
            output_filename = f"{file_prefix}{index}{file_extension}"
        else:
            input_filename = os.path.basename(infile)
            output_filename = os.path.splitext(input_filename)[0] + file_extension
        outfile = os.path.join(outdir, output_filename)
        convert(infile, outfile)
        print_progress(index, len(input_files))


def convert(infile, outfile):
    (
        ffmpeg.input(infile)
        .output(outfile, vcodec="copy", acodec="copy")
        .run(overwrite_output=True)
    )


def print_progress(index, total):
    print(f"Progress {int((index + 1) / total * 100)}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
