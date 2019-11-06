import configparser
import os
from random import uniform, choice
from json import dumps
from math import sqrt
from csv import writer, QUOTE_MINIMAL
from argparse import ArgumentParser

rounds = 10
sheep_number = 1
init_pos_limit = 10.0
sheep_move_dist = 0.5
wolf_move_dist = 1.0


class Sheep():

    def __init__(self, number):
        self.number = number
        self.position = {
            'x': uniform(-init_pos_limit, init_pos_limit),
            'y': uniform(-init_pos_limit, init_pos_limit)
        }

    def move(self):
        direction_x = choice(['W', 'E'])
        direction_y = choice(['N', 'S'])

        if direction_x == 'E':
            self.position['x'] += sheep_move_dist
        else:
            self.position['x'] -= sheep_move_dist

        if direction_y == 'N':
            self.position['y'] += sheep_move_dist
        else:
            self.position['y'] -= sheep_move_dist


class Wolf():

    def __init__(self):
        self.position = {
            'x': 0.0,
            'y': 0.0
        }

    def move(self, sheep_list):

        old_distance = 20
        sheep_nr = 0

        for sheep in sheep_list:
            if sheep != None:
                x_s = sheep.position['x']
                y_s = sheep.position['y']
                x_w = self.position['x']
                y_w = self.position['y']
                distance = sqrt((x_s - x_w)**2 + (y_s - y_w)**2)

                if distance < old_distance:
                    old_distance = distance
                    sheep_nr = sheep_list.index(sheep)

        if old_distance < wolf_move_dist:
            eaten_sheep = sheep_list[sheep_nr]
            sheep_list[sheep_nr] = None
            print('\033[92m' + f'Sheep nr {eaten_sheep.number} was eaten' + '\033[0m')
            return sheep_list
        else:
            x_s = sheep_list[sheep_nr].position['x']
            y_s = sheep_list[sheep_nr].position['y']
            x_w = self.position['x']
            y_w = self.position['y']

            self.position['x'] = x_w + (wolf_move_dist * (x_s - x_w))/old_distance
            self.position['y'] = y_w + (wolf_move_dist * (y_s - y_w))/old_distance

config = configparser.ConfigParser()
parser = ArgumentParser(description = 'wolf sheep simulation')
parser.add_argument('-c', '--config', metavar = 'FILE', dest ='file', help = 'configuration file', required = False)
parser.add_argument('-d', '--dir', metavar = 'DIR', dest ='directory', help = 'directory for log files', required = False)
parser.add_argument('-l', '--log', metavar = 'LEVEL', dest ='log_level', help = 'debug, info, warning, error, critical', required = False)
parser.add_argument('-r', '--rounds', metavar = 'NUM', dest ='rounds_number', help = 'rounds number', required = False)
parser.add_argument('-s', '--sheep', metavar = 'NUM', dest ='sheep_number', help = 'sheep number', required = False)
parser.add_argument('-w', '--wait', help = 'wait after round end')
args = parser.parse_args()

if args.file:
    config.read(args.file)
    init_pos_limit = float(config['Terrain']['InitPosLimit'])
    if(init_pos_limit < 0):
        raise ValueError('init_pos_limit cannot be less than 0')
    sheep_move_dist = float(config['Movement']['SheepMoveDist'])
    if(sheep_move_dist < 0):
        raise ValueError('sheep_move_dist cannot be less than 0')
    wolf_move_dist = float(config['Movement']['WolfMoveDist'])
    if(wolf_move_dist < 0):
        raise ValueError('wolf_move_dist cannot be less than 0')

if args.directory:
    os.mkdir(args.directory)



sheeps = []
wolf = Wolf()

for i in range(sheep_number):
    sheeps.append(Sheep(i))

file_json = open('pos.json', 'w+')
file_csv = open('alive.csv', 'w+')
csv_writer = writer(file_csv, delimiter = ',', quotechar = '|', quoting = QUOTE_MINIMAL)
file_json.write('[')

for i in range(rounds):

    sheep_json = []

    for sheep in sheeps:
        if sheep != None:
            sheep.move()

    print(f'Tour number: {i}')
    sheeps_after = wolf.move(sheeps)
    print("Wolf position:  %.3f, %.3f" %
          (wolf.position['x'], wolf.position['y']))
    print(f'Number of sheeps alive: {len([i for i in sheeps if i] )}')
    print('------------------------------')

    if sheeps_after != None:
        sheeps = sheeps_after

    for sheep in sheeps:
        if sheep != None:
            sheep_json.append(sheep.position)
        else:
            sheep_json.append(None)

    csv_writer.writerow([i, len([i for i in sheeps if i])])
    round_json = dumps({'round_no': i, 'sheep_pos': sheep_json, 'wolf_pos': wolf.position})

    if i == rounds - 1 or len([i for i in sheeps if i]) == 0:
        file_json.write(round_json)
    else:
        file_json.write(round_json + ',\n')

    if len([i for i in sheeps if i]) == 0:
        break

file_json.write(']')
file_json.close()
file_csv.close()