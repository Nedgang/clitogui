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
    image = Image.new(mode='RGBA', color=COLORS[args.color], size=(int(args.width), int(args.height)))
    return image  # a pillow image


@clitogui.interactive(run_pipeline, tabulate=False)
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
    final_image = args._output
    if final_image is not None:  # an image has been generated
        if hasattr(final_image, 'save'):  # TODEL
            final_image.save(args.outfile)  # saving of the final image, and the args leading to it
    print('finished!')
