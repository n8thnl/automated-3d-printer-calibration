import os
from solid import *
from PIL import Image

# [3, 17, 0.8]
# "../test-rectangle-short.stl"]

def etch_with_text(infile, outfile, text_arr, translations):
    a = import_stl(infile)
    
    for i in range(len(text_arr)):
        a -= translate(translations[i])(
            linear_extrude(height=0.2)(
                text('{0:04}'.format(str(text_arr[i])),
                    size=2.5,
                    font="helvetica",
                    halign="center",
                    valign="center"
                )
            )
        )

    # generate random filename
    intermediate_file = "intermediate.scad"                    

    scad_render_to_file(a, intermediate_file)

    os.system("openscad {} -o {}".format(intermediate_file, outfile))
    # os.system("openscad --preview --imgsize=512,512 {} -o {}".format(intermediate_file, outfile.replace('.stl', '.png')))

    return outfile


# def export_scad(a, outfile):
#     a = etchWithText(")

#     outfile = "export.scad"
#     stlfile = "export.stl"
#     outimage = "export.png"

#     scad_render_to_file(a, outfile)

#     os.system("openscad {} -o {}".format(outfile, stlfile))

#     os.system("openscad --preview --imgsize=512,512 {} -o {}".format(outfile, outimage))
