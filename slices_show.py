#
# Show slice table's logout.
#

import matplotlib.pyplot as plt

SLICES_DATA_FILE = "slices.txt"

slices_data_table = {}


def load_slices_data(filename):

    slices_data_table.clear()

    try:
        with open(filename, "r") as fs:
            for line in fs:
                if not line.isspace():
                    item = line.expandtabs().strip().split()
                    k = item[0]
                    v = item[1]
                    slices_data_table[k] = int(v)
    except FileNotFoundError as e:
        raise e


if __name__ == "__main__":

    load_slices_data(SLICES_DATA_FILE)
    # print(slices_data_table.values())

    squares = slices_data_table.values()
    plt.plot(squares)
    plt.show()
