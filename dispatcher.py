#!/usr/bin/python3

#
# Slices Dispatcher
#
# Version: 1.1
#
# Changelog:
#   v1.0: Strategy1 domo1
#
#   v1.1: Strategy1 stranger
#         Strategy2
#         Strategy3
#         Strategy4
#
#
#
# Author: Rock <orchidrock@126.com>
# Date: 2020.7.12
#

import copy
import optparse
import math

SLICES_DATA_FILE = "slices.txt"
STRATEGY = 2
DEVIATION_RANGE = 3
DOCDORS = 8
DFS_TABLE_TRANS_LIMIT = 30
GROUP_SEGMENT_LIMIT = 2

options = {}

initial_dt = [[[0, 10], 130], [[11, 47], 138], [[48, 65], 126],
              [[66, 77], 122], [[78, 83], 122], [[84, 97], 136],
              [[98, 110], 131], [[111, 152], 150]]

test_dt = [[[0, 10], 130], [[11, 51], 147], [[52, 66], 132],
           [[67, 78], 127], [[79, 85], 131], [[86, 99], 134],
           [[100, 118], 128], [[119, 152], 126]]


def parse_args():
    usage = """usage: %prog [options]
"""
    parser = optparse.OptionParser(usage)

    parser.add_option("--slice-file", type='string', default=SLICES_DATA_FILE)
    parser.add_option("--strategy", type='int', default=STRATEGY)
    parser.add_option("--deviation", type='int', default=DEVIATION_RANGE)
    parser.add_option("--doctors", type='float', default=DOCDORS)
    parser.add_option("--dttl", type='int', default=DFS_TABLE_TRANS_LIMIT)
    parser.add_option("--gsl", type='int', default=GROUP_SEGMENT_LIMIT)
    options, args = parser.parse_args()

    return options


def load_slices_data(filename):

    slices_data_table = {}
    tags = {}

    try:
        with open(filename, "r") as fs:
            for line in fs:
                if not line.isspace():
                    item = line.expandtabs().strip().split()
                    k = item[0]
                    v = item[1]
                    tag_name = None
                    if len(item) > 2:
                        tag_name = item[2]
                    if tag_name:
                        tag = tags.get(tag_name)
                        if tag:
                            tag[0] += int(v)
                            tag[1].append(k)
                        else:
                            tag = [int(v), [k]]
                            tags[tag_name] = tag
                    else:
                        slices_data_table[k] = int(v)

    except FileNotFoundError as e:
        raise e

    for key in tags.keys():
        tag = tags[key]
        slices_data_table[key] = tag[0]

    return slices_data_table, tags


#
# core algorithm
#
def judge_by_greedy(current_s, up_case, down_case, average):
    if down_case is None and up_case is None:
        return 0
    elif down_case is None:
        if current_s == 0 or \
           abs(current_s - average) > abs(current_s + up_case[1] - average):
            return 1
        else:
            return 0
    elif up_case is None:
        if current_s == 0 or \
           abs(current_s - average) > abs(current_s + down_case[1] - average):
            return 2
        else:
            return 0
    else:
        a = abs(current_s - average)
        b = abs(current_s + up_case[1] - average)
        c = abs(current_s + down_case[1] - average)

        m = min(a, b, c)
        if m == c:
            return 2
        elif m == b:
            return 1
        else:
            return 0


def sum_segment(start, end, slices_data_table_sorted):
    s = 0
    for i in range(start, end+1):
        s += slices_data_table_sorted[i][1]

    return s


def get_initial_dispatched_table(slices_sorted_by_key, case_numbers,
                                 average_samples):
    dispatched_table = []
    up_index = 0
    down_index = 0
    doctors = math.ceil(options.doctors)

    for i in range(doctors):
        s = 0
        while True:

            up_case = None

            if down_index >= case_numbers:
                down_case = None
            else:
                down_case = slices_sorted_by_key[down_index]

            judge = judge_by_greedy(s, up_case, down_case, average_samples[i])

            if i == doctors - 1 and down_case is not None:
                down_index += 1
                s += down_case[1]
            elif judge == 2:
                down_index += 1
                s += down_case[1]
            else:
                dispatched_table.append([[up_index, down_index-1], s])
                up_index = down_index
                break

    return dispatched_table


def get_dfs_table(initial_dispatched_table, slices_sorted_by_key):
    dfs_table = []
    doctors = math.ceil(options.doctors)
    dfs_table_trans_limit = options.dttl

    for i in range(doctors):
        item = initial_dispatched_table[i]
        index_range = item[0]
        up_index = index_range[0]
        down_index = index_range[1]

        up_sum = slices_sorted_by_key[up_index][1]
        down_sum = slices_sorted_by_key[down_index][1]

        up_dfs_table = []
        down_dfs_table = [0]

        while up_sum < dfs_table_trans_limit and up_index < down_index \
                and i != 0:
            up_dfs_table.append(-slices_sorted_by_key[up_index][1])
            up_index += 1
            up_sum += slices_sorted_by_key[up_index][1]

        while down_sum < dfs_table_trans_limit and up_index < down_index \
                and i != (doctors - 1):
            down_dfs_table.append(slices_sorted_by_key[down_index][1])
            down_index -= 1
            down_sum += slices_sorted_by_key[down_index][1]

        dfs_table.append([up_dfs_table, down_dfs_table])

    return dfs_table


def get_deviation(dispatched_table, average_samples):

    if False:
        pass
    else:
        deviation = 0.0

        for i in range(len(dispatched_table)):
            d = dispatched_table[i]
            deviation += abs(d[1] - average_samples[i])

    return deviation


def search_by_dfs(dfs_table, dispatched_table, average_samples, deep):

    doctors = math.ceil(options.doctors)

    if deep == doctors - 1:
        deviation_new = get_deviation(dispatched_table, average_samples)
        return (dispatched_table, deviation_new)
    else:
        res_dt = []
        res_dev = 10000000

        up_group = dispatched_table[deep]
        down_group = dispatched_table[deep+1]

        up_dfs_table = dfs_table[deep][1]
        down_dfs_table = dfs_table[deep+1][0]

        up_len = len(up_dfs_table)
        down_len = len(down_dfs_table)

        up_group_value = up_group[1]
        down_group_value = down_group[1]
        up_group_down_index = up_group[0][1]
        down_group_up_index = down_group[0][0]

        # up_movation
        # print("-----Up Movation: {0} ----".format(deep))
        # print("up_dfs_table: ", up_dfs_table)
        for i in range(up_len):
            # print("deep: {0}, up_step: {1}, i: {2}".format(deep,
            #                                           up_dfs_table[i], i))
            # print("up_group: ", up_group, "down_group: ", down_group)
            up_group[1] -= up_dfs_table[i]
            down_group[1] += up_dfs_table[i]

            if up_dfs_table[i] != 0:
                up_group[0][1] -= 1
                down_group[0][0] -= 1

            # print("i: ", i, end=' ')
            # print("deep: ", deep, end = ' ')
            dt, dev = search_by_dfs(dfs_table,
                                    copy.deepcopy(dispatched_table),
                                    average_samples,
                                    deep+1)
            if dev < res_dev:
                res_dev = dev
                res_dt = dt

        # down_movation
        # print("--- Down Movation: {0} ------".format(deep))
        # print("down_dfs_table: ", down_dfs_table)

        up_group[1] = up_group_value
        down_group[1] = down_group_value
        up_group[0][1] = up_group_down_index
        down_group[0][0] = down_group_up_index

        for i in range(down_len):
            # print("deep: {0}, down_step: {1}, i: {2}".format(deep,
            #                                       down_dfs_table[i], i))
            # print("down_group: ", up_group, "down_group: ", down_group)
            up_group[1] -= down_dfs_table[i]
            down_group[1] += down_dfs_table[i]

            if down_dfs_table[i] != 0:
                up_group[0][1] += 1
                down_group[0][0] += 1

            # up_group[0][0] = initial_up_group[0][0]
            # down_group[0][1] = initial_down_group[0][1]
            # print("i: ", i, end=' ')
            # print("deep: ", deep, end = ' ')

            dt, dev = search_by_dfs(dfs_table,
                                    copy.deepcopy(dispatched_table),
                                    average_samples,
                                    deep+1)

            if dev < res_dev:
                res_dev = dev
                res_dt = dt

        return (res_dt, res_dev)


# Strategy1
def strategy1(slices_sorted_by_key, case_numbers, average_samples):

    # Get initial dispatch_table
    min_dispatched_table = get_initial_dispatched_table(slices_sorted_by_key,
                                                        case_numbers,
                                                        average_samples)

    dfs_table = get_dfs_table(min_dispatched_table, slices_sorted_by_key)

    # print(min_dispatched_table)
    print("DFS table: ", dfs_table)
    # print(get_deviation(min_dispatched_table, average_samples))

    dispatched_table_copyed = copy.deepcopy(min_dispatched_table)

    # search by DFS to get much better choise.
    dt, dev = search_by_dfs(dfs_table, dispatched_table_copyed,
                            average_samples, 0)

    dispatched_table = []

    for group in dt:
        key_range = group[0]
        group_sum = group[1]
        dispatched_table.append([[[slices_sorted_by_key[key_range[0]][0],
                                 slices_sorted_by_key[key_range[1]][0]]],
                                group_sum])

    # for k in test_dt:
    #    s = sum_segment(k[0][0], k[0][1], slices_sorted_by_key)
    #    print("[{0}, {1}], {2}".format(k[0][0], k[0][1], s))

    # print(dispatched_table)
    # print(dt)
    # print_result(dispatched_table, average_samples)
    # print(dev)

    return (dispatched_table, dev)


def is_continuous(key1, key2):
    if '-' in key1:
        key1_sub_segment = int(key1.split('-')[1])
    else:
        key1_sub_segment = int(key1)

    if '-' in key2:
        key2_sub_segment = int(key2.split('-')[1])
    else:
        key2_sub_segment = int(key2)

    # print(key1_sub_segment, key2_sub_segment)
    return key2_sub_segment - key1_sub_segment == 1


def key_list_continuous(kl):
    # print(kl)

    result = []
    length = len(kl)
    index = 0

    while index < length:
        start = index
        end = index + 1

        while end < length and is_continuous(kl[end-1], kl[end]):
            end += 1

        if start == end - 1:
            result.append(kl[start])
        else:
            result.append([kl[start], kl[end-1]])

        index = end
    # print("key_list_continuous: ", result)
    return result


def replace_tag(kl, tags):

    result_list = []

    for k in kl:
        tag = tags.get(k)
        else:
            result_list.append(k)

    return result_list


# Strategy 2
def do_strategy2(slices_sorted_by_key, average_samples):

    result_table = []
    group_index = 0
    doctors = math.ceil(options.doctors)

    def find_last_items(slices_sorted_by_key, distance, jump_count=0):
        start_index = 0
        end_index = start_index
        length = len(slices_sorted_by_key)
        segment_sum = 0
        while end_index < length:
            if abs(distance - segment_sum) < options.deviation:
                break
            elif segment_sum > distance:
                item = slices_sorted_by_key[start_index]
                segment_sum -= item[1]
                start_index += 1
            else:
                item = slices_sorted_by_key[end_index]
                segment_sum += item[1]
                end_index += 1

        # print(start_index, end_index, segment_sum)
        return start_index, end_index, segment_sum

    while group_index < doctors and slices_sorted_by_key:
        g = []
        g_sum = 0

        while slices_sorted_by_key:
            item = slices_sorted_by_key[0]
            g_sum_next = g_sum + item[1]
            if g_sum_next > average_samples[group_index]:

                start_index, end_index, segment_sum = \
                        find_last_items(slices_sorted_by_key,
                                        (average_samples[group_index] - g_sum))

                for i in range(end_index-start_index):
                    item = slices_sorted_by_key.pop(start_index)
                    g.append(item[0])

                g_sum += segment_sum
                break
            else:
                g_sum = g_sum_next
                g.append(item[0])
                slices_sorted_by_key.pop(0)

        group_index += 1
        result_table.append([g, g_sum])

    return result_table, slices_sorted_by_key


def strategy2(slices_sorted_by_key, average_samples):
    dispatched_table = []

    while slices_sorted_by_key:

        dt, slices_sorted_by_key = do_strategy2(slices_sorted_by_key,
                                                average_samples)
        # print_result(dt, average)
        # print(slices_sorted_by_key)
        # dispatched_table = merge_dispatch_table(dispatched_table, dt)
        dispatched_table = dt
        if slices_sorted_by_key:
            print("")
            print("WARNING: There are some undispatched items,",
                  "please make a decrease for DEVIATION_RANGE")
            print(slices_sorted_by_key)
            print("")
        break
    return dispatched_table


# Strategy 3
def do_strategy3(slices_sorted_by_value, average):
    group_index = 0
    result_table = []
    doctors = math.ceil(options.doctors)

    def find_next_item(slices_sorted_by_value, distance, direction=0):
        goal_item = None
        for item in slices_sorted_by_value:
            if item[1] < distance:
                goal_item = item
                break
            elif abs(item[1] - distance) < (options.deviation):
                goal_item = item
            else:
                pass
        return goal_item

    while group_index < doctors and slices_sorted_by_value:
        g = []
        g_sum = 0

        while True:

            distance = average[group_index] - g_sum

            if abs(distance) < 1:
                if g_sum == 0:  # empty table
                    item = slices_sorted_by_value[0]
                else:
                    item = None
            else:
                item = find_next_item(slices_sorted_by_value, distance)
            if item:
                g.append(item[0])
                g_sum += item[1]
                slices_sorted_by_value.remove(item)
            else:
                break

        group_index += 1
        result_table.append([g, g_sum])

    while group_index < doctors:
        result_table.append([[], 0])
        group_index += 1

    return result_table, slices_sorted_by_value


def merge_dispatch_table(old, nex):
    new = []
    doctors = math.ceil(options.doctors)

    if not old:
        for item in nex:
            new.append(item)

    if not nex:
        for item in old:
            new.append(item)

    if old and nex:
        for i in range(0, doctors):
            item_old = old[i]
            item_nex = nex[i]
            item_new = []
            item_new.append(item_old[0] + item_nex[0])
            item_new.append(item_old[1] + item_nex[1])
            new.append(item_new)
    else:
        pass

    return new


def strategy3(slices_sorted_by_value):

    dispatched_table = []

    while slices_sorted_by_value:
        length = len(slices_sorted_by_value)
        sum_samples = sum_segment(0, length-1, slices_sorted_by_value)
        average = get_average_samples(sum_samples)

        # print("-----------------")
        # print(slices_sorted_by_value)
        # print("AVERAGE: ", average)

        dt, slices_sorted_by_value = do_strategy3(slices_sorted_by_value,
                                                  average)
        # print("dt: ", dt)
        dispatched_table = merge_dispatch_table(dispatched_table, dt)

    return dispatched_table


# [G1, G2,  G3, ...]
# G1: [[q1, q2, ...], sum]
def print_result(dispatched_table_list, average, tags):

    for i in range(len(dispatched_table_list)):
        g = dispatched_table_list[i]
        slice_item_g = key_list_continuous(sorted(replace_tag(g[0], tags)))
        sum_g = g[1]
        deviation_g = sum_g - average[i]

        print("[", end='')
        for q in slice_item_g:

            if len(q) == 1:
                print("{0}, ".format(q[0]), end='')
            elif len(q) == 2:
                print("({0}=>{1}), ".format(q[0], q[1]), end='')
            else:
                print("{0}, ".format(q), end='')

        print("]", end=' ')
        print("{0} ({1:.2f})".format(sum_g, deviation_g))


def get_average_samples(sum_all_samples):
    average = sum_all_samples / (options.doctors)
    doctors_ceil = math.ceil(options.doctors)
    doctors_floor = math.floor(options.doctors)

    average_samples = []

    for i in range(doctors_floor):
        average_samples.append(average)

    for i in range(doctors_floor, doctors_ceil):
        average_samples.append(average * (doctors_ceil - options.doctors))

    return average_samples


if __name__ == "__main__":

    options = parse_args()  # global variable

    # print(options)

    slices_data_table, tags = load_slices_data(options.slice_file)

    slices_sorted_by_value = sorted(slices_data_table.items(),
                                    key=lambda d: d[1],
                                    reverse=True)
    slices_sorted_by_key = sorted(slices_data_table.items(),
                                  key=lambda d: d[0],
                                  reverse=False)

    case_numbers = len(slices_sorted_by_value)
    sum_all_samples = sum_segment(0, case_numbers-1, slices_sorted_by_value)
    average_samples = get_average_samples(sum_all_samples)

    print("Case Numbers: ", case_numbers)
    print("Sum All Samples: ", sum_all_samples)
    print("Average Samples: ", average_samples)
    print("Doctors: ", options.doctors)
    print("Strategy: ", options.strategy)
    print("Slice File:", options.slice_file)
    print("")

    if options.strategy == 1:  # strategy 1:
        dt, dev = strategy1(slices_sorted_by_key,
                            case_numbers,
                            average_samples)
        print_result(dt, average_samples, tags)
        print(dev)
    elif options.strategy == 2:  # strategy 2:
        dt = strategy2(slices_sorted_by_key, average_samples)
        print_result(dt, average_samples, tags)
        print(get_deviation(dt, average_samples))
    elif options.strategy == 3:  # strategy 3:
        dt = strategy3(slices_sorted_by_value)
        print_result(dt, average_samples, tags)
        print(get_deviation(dt, average_samples))
    else:
        pass
