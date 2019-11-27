import configparser
import os
from random import uniform, choice
from json import dumps
from math import sqrt
from csv import writer, QUOTE_MINIMAL
from argparse import ArgumentParser
import logging

rounds = 10
sheep_number = 3
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
        logging.debug(
            "Call sheep.move() method. Sheep number: " + str(self.number))
        direction_x = choice(['W', 'E'])
        direction_y = choice(['N', 'S'])
        logging.info(
            'Sheep nr ' + str(self.number) + ' position before move: ' + str(
                self.position['x']) + ' ,' + str(self.position['y']))
        if direction_x == 'E':
            self.position['x'] += sheep_move_dist
        else:
            self.position['x'] -= sheep_move_dist

        if direction_y == 'N':
            self.position['y'] += sheep_move_dist
        else:
            self.position['y'] -= sheep_move_dist
        logging.info(
            'Sheep nr ' + str(self.number) + ' position after move: ' + str(
                self.position['x']) + ' ,' + str(self.position['y']))


class Wolf():

    def __init__(self):
        self.position = {
            'x': 0.0,
            'y': 0.0
        }

    def move(self, sheep_list):
        logging.debug("Call wolf.move() method.")
        logging.info('Wolf position before move: ' + str(
            self.position['x']) + ' ,' + str(self.position['y']))
        old_distance = 20
        sheep_nr = 0

        for sheep in sheep_list:
            if sheep != None:
                x_s = sheep.position['x']
                y_s = sheep.position['y']
                x_w = self.position['x']
                y_w = self.position['y']
                distance = sqrt((x_s - x_w) ** 2 + (y_s - y_w) ** 2)

                if distance < old_distance:
                    old_distance = distance
                    sheep_nr = sheep_list.index(sheep)

        if old_distance < wolf_move_dist:
            eaten_sheep = sheep_list[sheep_nr]
            sheep_list[sheep_nr] = None
            print(
                '\033[92m' + f'Sheep nr {eaten_sheep.number} was eaten' + '\033[0m')
            return sheep_list
        else:
            x_s = sheep_list[sheep_nr].position['x']
            y_s = sheep_list[sheep_nr].position['y']
            x_w = self.position['x']
            y_w = self.position['y']

            self.position['x'] = x_w + (
                    wolf_move_dist * (x_s - x_w)) / old_distance
            self.position['y'] = y_w + (
                    wolf_move_dist * (y_s - y_w)) / old_distance
        logging.info('Wolf position after move: ' + str(
            self.position['x']) + ' ,' + str(self.position['y']))


config = configparser.ConfigParser()
parser = ArgumentParser(description='wolf sheep simulation')
parser.add_argument('-c', '--config', metavar='FILE', dest='file',
                    help='configuration file', required=False)
parser.add_argument('-d', '--dir', metavar='DIR', dest='directory',
                    help='directory for log files', required=False)
parser.add_argument('-l', '--log', metavar='LEVEL', dest='log_level',
                    help='DEBUG, INFO, WARNING, ERROR, CRITICAL',
                    required=False)
parser.add_argument('-r', '--rounds', metavar='NUM', dest='rounds_number',
                    help='rounds number', type=int, required=False)
parser.add_argument('-s', '--sheep', metavar='NUM', dest='sheep_number',
                    help='sheep number', type=int, required=False)
parser.add_argument('-w', '--wait', help='wait after round end',
                    action='store_true', required=False)
args = parser.parse_args()

if args.log_level is not None:
    level = logging.DEBUG
    if args.log_level == 'DEBUG':
        level = logging.DEBUG
    if args.log_level == 'INFO':
        level = logging.INFO
    if args.log_level == 'WARNING':
        level = logging.WARNING
    if args.log_level == 'ERROR':
        level = logging.ERROR
    if args.log_level == 'CRITICAL':
        level = logging.CRITICAL
    logging.basicConfig(filename='chase.log', filemode='w', level=level)

if args.file:
    config.read(args.file)

    init_pos_limit = float(config['Terrain']['InitPosLimit'])
    if init_pos_limit < 0:
        logging.error("Value of init_pos_limit was set to less than 0!")
        raise ValueError('init_pos_limit cannot be less than 0')

    sheep_move_dist = float(config['Movement']['SheepMoveDist'])
    if sheep_move_dist < 0:
        logging.error("Value of sheep_move_dist was set to less than 0!")
        raise ValueError('sheep_move_dist cannot be less than 0')

    wolf_move_dist = float(config['Movement']['WolfMoveDist'])
    if wolf_move_dist < 0:
        logging.error("Value of wolf_move_dist was set to less than 0!")
        raise ValueError('wolf_move_dist cannot be less than 0')

if args.directory:
    if not os.path.isdir(f'./{args.directory}'):
        os.mkdir(args.directory)

    file_json = open(f'./{args.directory}/pos.json', 'w+')
    file_csv = open(f'./{args.directory}/alive.csv', 'w+')
    logging.info("Set pos.json and alive.csv location in given directory.")
else:
    file_json = open('pos.json', 'w+')
    file_csv = open('alive.csv', 'w+')
    logging.info('Set pos.json and alive.csv location in local directory.')

if args.rounds_number:
    if args.rounds_number < 0:
        logging.error("Value of rounds_number was set to less than 0!")
        raise ValueError('rounds_number cannot be less than 0')
    logging.info(
        "Value of rounds_number set to: " + str(args.rounds_number) + ".")
    rounds = args.rounds_number

if args.sheep_number:
    if args.sheep_number < 0:
        logging.error("Value of sheep_number was set to less than 0!")
        raise ValueError('sheep_number cannot be less than 0')
    sheep_number = args.sheep_number
    logging.info(
        "Value of sheep_number set to: " + str(args.sheep_number) + ".")

sheeps = []
wolf = Wolf()

for i in range(sheep_number):
    sheeps.append(Sheep(i))

csv_writer = writer(file_csv, delimiter=',', quotechar='|',
                    quoting=QUOTE_MINIMAL)
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
    print(f'Number of sheeps alive: {len([i for i in sheeps if i])}')
    print('------------------------------')

    if sheeps_after != None:
        sheeps = sheeps_after

    for sheep in sheeps:
        if sheep != None:
            sheep_json.append(sheep.position)
        else:
            sheep_json.append(None)

    csv_writer.writerow([i, len([i for i in sheeps if i])])
    round_json = dumps(
        {'round_no': i, 'sheep_pos': sheep_json, 'wolf_pos': wolf.position}, indent = 1)

    if i == rounds - 1 or len([i for i in sheeps if i]) == 0:
        logging.info("Write rounds to json file.")
        file_json.write(round_json)
    else:
        logging.info("Write rounds to json file.")
        file_json.write(round_json + ',\n')

    if args.wait:
        input('')

    if len([i for i in sheeps if i]) == 0:
        break

file_json.write(']')
file_json.close()
file_csv.close()
