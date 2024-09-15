import fitz  # PyMuPDF library
import argparse
from pathlib import Path

description = "Replace raster figures in PDF file with their vector versions"

# Customer formatter required to print help message for "--" option.
class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position = 50)
    def format_help(self):
        original_help = super().format_help()
        return original_help.replace(' images ', ' -- images ')

parser = argparse.ArgumentParser(description = description, add_help = False, formatter_class = CustomHelpFormatter)

parser.add_argument('-h', '--help', action = 'help', default = argparse.SUPPRESS, help = "Show this help message and exit.")
parser.add_argument('-d', '--dir', type = str, help = 'Save rasters in this folder for debugging.')

parser.add_argument('-i', '--input', required = True, type = str, help = 'Input PDF file.')
parser.add_argument('-o', '--output', required = True, type = str, help = 'Output PDF file.')
parser.add_argument('images', type = str, nargs = '+', help = 'PDF files with images')

args = parser.parse_args()

def replace_raster_with_vector(input_file, figure_files, output_file, dir_name):
    doc = fitz.open(input_file)
    if dir_name:
        raster_dir = Path(dir_name)
        raster_dir.mkdir(parents = True, exist_ok = True)
    else:
        raster_dir = None
    i = 0
    for page in doc:
        for image in page.get_images(full=True):

            assert len(figure_files) > i, "More figures than figure files"
            fig_file = figure_files[i]
            xref = image[0]
            print(i, fig_file)

            if raster_dir:
                raster = doc.extract_image(xref)
                with open(raster_dir.joinpath(f"{i}.{raster['ext']}"), 'wb') as file:
                    file.write(raster['image'])
           
            # Get the bounding box of the image
            bbox = page.get_image_bbox(image)
            
            # Replace raster image with the corresponding vector image overlay
            docsrc = fitz.open(fig_file)
            page.show_pdf_page(bbox, docsrc, pno=0, overlay=True)
            docsrc.close()
                
            # Remove the original raster image
            page.delete_image(xref)

            i += 1
    assert i == len(figure_files), "More figure files than figures"
    doc.save(output_file)
    doc.close()

replace_raster_with_vector(args.input, args.images, args.output, args.dir)
