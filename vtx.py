import logging
import time

logger = logging.getLogger(__name__)
handler = logging.FileHandler('botwell.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


valid_params = {
    'protocol': ['irc', 'sa2'],
    'channels': ['a', 'b', 'e', 'f', 'r', 'i'],
    'powers': ['0', '25', '50', '100', '200', '250', '300', '400', '600', '800', '1000'],
}


def filter_params(protocol, channels, powers):
    protocol_filtered = [x for x in protocol.split(',') if x in valid_params['protocol']][0]
    channels_filtered = [x for x in channels.split(',') if x in valid_params['channels']]
    powers_filtered = [x for x in powers.split(',') if x in valid_params['powers']]

    return protocol_filtered, channels_filtered, powers_filtered


def generate_vtx_table(protocol, channels, powers, author):
    bands_list = []
    power_list = []

    channel_sets = {
        'a': {"name": "BOSCAM_A", "letter": "A", "is_factory_band": False,
              "frequencies": [5865, 5845, 5825, 5805, 5785, 5765, 5745, 5725]},
        'b': {"name": "BOSCAM_B", "letter": "B", "is_factory_band": False,
              "frequencies": [5733, 5752, 5771, 5790, 5809, 5828, 5847, 5866]},
        'e': {"name": "BOSCAM_E", "letter": "E", "is_factory_band": False,
              "frequencies": [5705, 5685, 5665, 0, 5885, 5905, 0, 0]},
        'f': {"name": "FATSHARK", "letter": "F", "is_factory_band": False,
              "frequencies": [5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880]},
        'r': {"name": "RACEBAND", "letter": "R", "is_factory_band": False,
              "frequencies": [5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917]},
        'i': {"name": "IMD6", "letter": "I", "is_factory_band": False,
              "frequencies": [5732, 5765, 5828, 5840, 5866, 5740, 0, 0]},
    }

    for channel in channels:
        bands_list.append(channel_sets[channel])

    for i, power in enumerate(powers):
        if protocol == 'irc':
            value = int(power)
        elif protocol == 'sa2':
            value = i

        power_list.append({'value': value, 'label': power})

    vtx_table = {
        "description": "Auto-generated VTX Table by botwell",
        "version": "0.1",
        "vtx_table": {
            "bands_list": bands_list,
            "powerlevels_list": power_list
        }
    }

    filename = '/tmp/%s_%s.json' % (author, time.time())

    with open(filename, 'w') as file:
        file.write(str(vtx_table))

    return filename
