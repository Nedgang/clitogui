"""Example showing how to use clitogui as a fully standalone program.

Needs Pillow:  pip install Pillow

"""
import clitogui
import argparse
from PIL import Image


COLORS = {
    'red': (255, 0, 0, 255),
    'green': (0, 255, 0, 255),
    'blue': (0, 0, 255, 255),
}


def run_pipeline(args) -> Image:
    for _ in range(args.nb_to_return):
        yield Image.new(mode='RGBA', color=COLORS[args.color], size=(int(args.width), int(args.height)))


@clitogui.interactive(run_pipeline, tabulate=True)
def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('color', choices=tuple(COLORS), type=str,
                        help='Main background color of the image')
    parser.add_argument('--width', '-w', type=int, default=300,
                        help='image width')
    parser.add_argument('--height', '-t', type=int, default=300,
                        help='image height')
    parser.add_argument('--outfile', '-o', type=str, default='out.png',
                        help='where to save the final image')
    parser.add_argument('--nb-to-return', '-n', type=int, default=1,
                        help='Number of time the image should be created')
    return parser


if __name__ == "__main__":
    args = cli().parse_args()
    final_images = args._output
    if final_images:
        final_images[0].save(args.outfile)  # saving of the first image
    print('finished! ({} images returned)'.format(len(final_images)))
