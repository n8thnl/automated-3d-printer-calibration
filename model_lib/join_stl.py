import os

def strip_end(gcode_arr):
    for i in range(len(gcode_arr)):
        if '; stop printing object' in gcode_arr[i]:
            return gcode_arr[:i]

# travel to a position
def travel(end_pos):
    return 'G1 X{} Y{} F9000\n'.format(end_pos[0], end_pos[1])


def stl_chain(gcode_folder, num_layers, delimiter=';LAYER_CHANGE\n'):

    # read all filenames under gcode_folder
    gcode_files = os.listdir(gcode_folder)

    # list of all gcodes we read
    gcode_arr = []

    # read all gcodes
    for i in range(len(gcode_files)):
        with open(gcode_folder + 'gcode-{}.gcode'.format(i), 'r') as file:
            total_gcode = file.readlines()

            # split gcode into layers using the delimiter
            layers_split_idx = []
            for j, layer in enumerate(total_gcode):
                if layer == delimiter:
                    layers_split_idx.append(j)

            # strict equal since the start_gcode technically counts as a layer
            if len(layers_split_idx) != num_layers:
                raise Exception('Number of layers does not match expected number of layers')

            # split gcode into layers
            layers = []
            for j in range(len(layers_split_idx) + 1):
                if j == 0 and i == 0:
                    layers.append(total_gcode[:layers_split_idx[j]])
                elif j == 0:
                    # do not include start gcode if we are not in the first file
                    pass
                elif j == len(layers_split_idx):
                    if i != len(gcode_files) - 1:
                        # do not include end gcode if we are not in the last file
                        layers.append(strip_end(total_gcode[layers_split_idx[j-1]:]))
                    else:
                        layers.append(total_gcode[layers_split_idx[j-1]:])
                else:
                    layers.append(total_gcode[layers_split_idx[j-1]:layers_split_idx[j]])

            # save each layer to a file
            for j, layer in enumerate(layers):
                with open('./layers/gcode-{}-layer-{}'.format(i,j if i == 0 else j + 1), 'w') as layer_file:
                    layer_file.writelines(layer)

    combined_gcode = []
    # read layer 0 start gcode and append to list
    with open('./layers/gcode-0-layer-0', 'r') as file:
        combined_gcode += file.readlines()

    # start with layer 1 and go to final layer
    for i in range(1, num_layers + 1):
        
        # for each file, combine the layer
        for j in range(len(gcode_files)):
            with open('./layers/gcode-{}-layer-{}'.format(j,i), 'r') as file:
                combined_gcode += file.readlines()

    # remove combined.gcode if it exists
    if os.path.exists('./combined.gcode'):
        os.remove('./combined.gcode')

    # write the combined gcode to a file
    with open('./combined.gcode', 'w') as file:
        file.writelines(combined_gcode)
    