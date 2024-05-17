import numpy as np
import configparser
import os
import model_lib.add_text as add_text
import model_lib.join_stl as join_stl
from solid import *

# Parameters
extrusion_width_range = [0.4, 0.8]
speed_range = [5, 25]
flow_rate_range = [95, 105]
temperature_range = [240, 280]

ETCH_TEXT = False

def generate_parameter_set():
    extrusion_width = round(np.random.uniform(extrusion_width_range[0], extrusion_width_range[1]), 2)
    speed = round(np.random.uniform(speed_range[0], speed_range[1]), 2)
    flow_rate = round(np.random.uniform(flow_rate_range[0], flow_rate_range[1]), 2)
    temperature = round(np.random.uniform(temperature_range[0], temperature_range[1]), 2)

    return extrusion_width, speed, flow_rate, temperature

def generate_config(config, parameter_set, filename):
    extrusion_width, speed, flow_rate, temperature = parameter_set

    config['DEFAULT']['extrusion_width'] = str(extrusion_width)
    config['DEFAULT']['before_layer_gcode'] += 'M221 S{}'.format(flow_rate)
    config['DEFAULT']['first_layer_temperature'] = str(temperature)
    config['DEFAULT']['temperature'] = str(temperature)

    # All Speeds
    config['DEFAULT']['perimeter_speed'] = str(speed)
    config['DEFAULT']['infill_speed'] = str(speed)
    config['DEFAULT']['external_perimeter_speed'] = str(speed)
    config['DEFAULT']['first_layer_speed'] = str(speed)
    config['DEFAULT']['min_print_speed'] = str(speed)
    config['DEFAULT']['solid_infill_speed'] = str(speed)
    config['DEFAULT']['top_solid_infill_speed'] = str(speed)

    with open(filename, 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':

    # generate parameter sets
    num_parameter_sets = 2
    parameter_sets = []
    for i in range(num_parameter_sets):
        parameter_sets.append(generate_parameter_set())

    # remove all existing configs
    for file in os.listdir('./configs'):
        os.remove('./configs/' + file)

    for i, parameter_set in enumerate(parameter_sets):
        # read base config json from file
        base_config = configparser.ConfigParser(inline_comment_prefixes="#")
        base_config.read('base-config.ini')
        filename = './configs/config-{}.ini'.format(i)
        generate_config(base_config, parameter_set, filename)

        # remove the first line from the config file
        with open(filename, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(filename, 'w') as fout:
            fout.writelines(data[1:])

    # remove all existing models
    for file in os.listdir('./models'):
        os.remove('./models/' + file)

    # etch stls with parameters
    corner_translations = [
        [6, 22, 0.8],        # top left
        [19, 22, 0.8],       # top right
        [6, 3, 0.8],         # bottom left
        [19, 3, 0.8]         # bottom right
    ]

    def param_to_str(parameter):
        if parameter < 10:
            return '{0:.3f}'.format(parameter)
        elif parameter < 100:
            return '{0:.2f}'.format(parameter)
        elif parameter < 1000:
            return '{0:.1f}'.format(parameter)

    models_etched = []
    for i, parameter_set in enumerate(parameter_sets):
        filename = './models/model-{}.stl'.format(i)

        if ETCH_TEXT:
            add_text.etch_with_text('test-rectangle-short.stl', filename, [param_to_str(el) for el in parameter_set], corner_translations)
        else:
            # copy the base file to the filename
            os.system('cp test-rectangle-short.stl {}'.format(filename))
        
        prusaslicer_args = [
            'prusaslicer',
            '--export-gcode',
            '--center {},30'.format(125+i*50),
            '--load ./configs/config-{}.ini'.format(i),
            '-o ./gcode/gcode-{}.gcode'.format(i),
            './models/model-{}.stl'.format(i)
        ]
        # slice model
        os.system(' '.join(prusaslicer_args))

    # remove all existing layer files
    for file in os.listdir('./layers'):
        os.remove('./layers/' + file)

    # join sliced models
    join_stl.stl_chain('./gcode/', 10)