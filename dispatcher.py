#!/usr/bin/python3

#
# Slices Dispatcher
#
# Version: 1.0.1
#
# Changelog:
#   v1.0.1:
#
#
#
# Author: Rock <orchidrock@126.com>
# Date: 2020.7.12
#

import copy
import sys

DOCDORS = 11
SLICES_DATA_FILE = "slices.txt"

slices_data_table = {}
case_numbers = 0
sum_all_samples = 0
average_samples = 0

fluctuation_range = 20

DEVIATION_RANGE = 5

def load_slices_data(filename):

    slices_data_table.clear()

    try:
        with open(filename, "r") as fs:
            for line in fs:
                if not line.isspace():
                    k, v = line.strip().split("\t")
                    slices_data_table[k] = int(v)
    except FileNotFoundError as e:
        raise e


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


def get_initial_dispatched_table(slices_data_table_sorted, case_numbers,
                                 average_samples):
    dispatched_table = []
    up_index = 0
    down_index = 0

    for i in range(DOCDORS):
        s = 0
        while True:

            up_case = None

            if down_index >= case_numbers:
                down_case = None
            else:
                down_case = slices_data_table_sorted[down_index]

            judge = judge_by_greedy(s, up_case, down_case, average_samples)

            if i == DOCDORS - 1 and down_case is not None:
                down_index += 1
                s += down_case[1]
            elif judge == 2:
                down_index += 1
                s += down_case[1]
            else:
                dispatched_table.append([s, up_index, down_index-1])
                up_index = down_index
                break

    return dispatched_table


def get_deviation(dispatched_table):
    deviation = 0.0

    for d in dispatched_table:
        deviation += abs(d[0] - average_samples)

    return deviation


def left_move_segment(dispatched_table, slices_data_table_sorted,  deep):
    # print('L', end=' ')
    # print(slices_data_table_sorted)
    # print("left_move_segment: ",dispatched_table, deep)
    up_table_entry = dispatched_table[deep]
    down_table_entry = dispatched_table[deep+1]

    down_table_index = down_table_entry[1]
    # print(up_table_entry, down_table_entry)

    s = 0
    while True:
        next_case_samples = slices_data_table_sorted[down_table_index][1]
        if s + next_case_samples > fluctuation_range or \
           down_table_index >= case_numbers:
            break
        else:
            s += next_case_samples
            down_table_index += 1

    # print("\n")
    # print(s, down_table_index)

    # update
    up_table_entry[0] += s
    up_table_entry[2] = down_table_index - 1

    down_table_entry[0] -= s
    down_table_entry[1] = down_table_index

    # print(up_table_entry, down_table_entry)

    # sys.exit(0)
    return dispatched_table


def right_move_segment(dispatched_table, slices_data_table_sorted, deep):
    # print('R', end=' ')
    # print("right_move_segment: ",dispatched_table, deep)
    up_table_entry = dispatched_table[deep]
    down_table_entry = dispatched_table[deep+1]

    up_table_index = up_table_entry[2]
    s = 0

    # print(up_table_entry, down_table_entry, s)

    while True:
        next_case_samples = slices_data_table_sorted[up_table_index][1]
        if s + next_case_samples > fluctuation_range or up_table_index <= 0:
            break
        else:
            s += next_case_samples
            up_table_index -= 1

    # print("\n")
    # print(s, up_table_index)

    # update
    up_table_entry[0] -= s
    up_table_entry[2] = up_table_index

    down_table_entry[0] += s
    down_table_entry[1] = up_table_index + 1

    # print(up_table_entry, down_table_entry)

    return dispatched_table


def search_by_dfs(min_dispatched_table, dispatched_table,
                  slices_data_table_sorted, deep):
    if deep == DOCDORS - 1:
        deviation_new = get_deviation(dispatched_table)
        deviation_min = get_deviation(min_dispatched_table)
        # print(dispatched_table)
        # print(deviation_new, deviation_min)
        if deviation_new < deviation_min:
            return copy.deepcopy(dispatched_table)
        else:
            return min_dispatched_table
    else:

        return search_by_dfs(search_by_dfs(search_by_dfs(min_dispatched_table, dispatched_table, slices_data_table_sorted, deep+1), \
                                           right_move_segment(copy.deepcopy(dispatched_table),slices_data_table_sorted, deep),\
                                           slices_data_table_sorted, \
                                           deep+1), \
                            left_move_segment(copy.deepcopy(dispatched_table), slices_data_table_sorted, deep), \
                            slices_data_table_sorted, \
                            deep+1)


def dispatcher_simple(slices_data_table):

    # sorted_table_by_value = sorted(slices_data_table.items(), key=lambda d:d[1], reverse=True)
    slices_data_table_sorted = sorted(slices_data_table.items(), key=lambda d:d[0], reverse=False)

    # Get initial dispatch_table
    min_dispatched_table = get_initial_dispatched_table(slices_data_table_sorted, case_numbers, average_samples)
    new_dispatched_table = copy.deepcopy(min_dispatched_table)
    # print(new_dispatched_table)
    # print(min_dispatched_table)
    # print(slices_data_table_sorted)

    # search by DFS to get much better choise.
    dispatched_table = search_by_dfs(new_dispatched_table,
                                     min_dispatched_table,
                                     slices_data_table_sorted,
                                     0)

    res = []

    for d in dispatched_table:
        start_case = slices_data_table_sorted[d[1]]
        end_case = slices_data_table_sorted[d[2]]
        # print([start_case[0], end_case[0]], d[0])
        res.append([start_case[0], end_case[0], d[0]])

    return (get_deviation(dispatched_table)), res

# Strategy 2
def dispatcher(slices_data_table):
    sorted_table_by_value = sorted(slices_data_table.items(), key=lambda d:d[1], reverse=True)
    sorted_table_by_key = sorted(slices_data_table.items(), key=lambda d:d[0], reverse=False)

    case_numbers = len(slices_data_table)
    sum_all_samples = sum_segment(0, case_numbers-1, sorted_table_by_key)
    average_samples = sum_all_samples / DOCDORS

    dispatch_result = []
    doctor_index = 0
    for i in range(DOCDORS):
        dispatch_result.append({})

    # print(average_samples, case_numbers, dispatch_result)

    # print(sorted_table_by_key)

    for case_index in range(case_numbers):
        key = sorted_table_by_value[case_index][0]
        val = sorted_table_by_value[case_index][1]
        s = val
        dispatched_cases = [(key, val)]

        if doctor_index >= DOCDORS:
            break

        if slices_data_table.get(key):
            # core stretegies
            origin_case_index = sorted_table_by_key.index((key, val))
            # print(key, val, origin_case_index)

            up_index = origin_case_index - 1
            down_index = origin_case_index + 1

            while True:
                if up_index < 0 or up_index >= case_numbers:
                    up_case = None
                elif slices_data_table.get(sorted_table_by_key[up_index][0]) is None:
                    up_case = None
                else:
                    up_case = sorted_table_by_key[up_index]

                if down_index < 0 or down_index >= case_numbers:
                    down_case = None
                elif slices_data_table.get(sorted_table_by_key[down_index][0]) is None:
                    down_case = None
                else:
                    down_case = sorted_table_by_key[down_index]

                judge = judge_by_greedy(s, up_case, down_case, average_samples)

                if judge == 0:
                    d = dispatch_result[doctor_index]

                    d[s] = sorted(dispatched_cases, key=lambda d:d[0], reverse=False)
                    doctor_index += 1
                    break
                elif judge == 1:  # up_case
                    s += up_case[1]
                    dispatched_cases.append(up_case)
                    up_index -= 1
                    slices_data_table.pop(up_case[0])

                elif judge == 2:  # down_case
                    s += down_case[1]
                    dispatched_cases.append(down_case)
                    down_index += 1
                    slices_data_table.pop(down_case[0])
                else:
                    pass


        else:
            pass


    print(dispatch_result)


def dispatch_demo_test(slices_data_table):
    dispatch_demo = [[37713, 37733],
                      [37734, 37769],
                      [37770, 37783],
                      [37784, 37788],
                      [37789, 37795],
                      [37796, 37806],
                      [37807, 37817],
                      [37818, 37865]]
    for d in dispatch_demo:
        s = 0
        for i in range(d[0], d[1]+1):
            # print(str(i))
            v = slices_data_table.get("2020-" + str(i))
            s += int(v)
        print(s)


# Strategy 3
def do_strategy3(slices_sorted_by_value, average):

    #
    def find_next_item(slices_sorted_by_value, distance):
        goal_item = None
        # low_item = None
        # high_item = None

        for item in slices_sorted_by_value:
            if item[1] < distance:
                goal_item = item
                break
            elif abs(item[1] - distance) < DEVIATION_RANGE:
                goal_item = item
            else:
                pass

        # print("find_next_item: ", distance, goal_item)

        return goal_item

    group_index = 0
    result_table = []

    while group_index < DOCDORS and slices_sorted_by_value:
        g = []
        g_sum = 0


        while True:

            distance = average - g_sum

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

    while group_index < DOCDORS:
        result_table.append([[], 0])
        group_index += 1

    return result_table, slices_sorted_by_value


def merge_dispatch_table(old, nex):
    new = []
    if not old:
        for item in nex:
            new.append(item)

    if not nex:
        for item in old:
            new.append(item)

    if old and nex:
        for i in range(0, DOCDORS):
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
        average = sum_samples / DOCDORS

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
def print_result(dispatched_table_list, average):
    # print("length: ", len(dispatched_table_list))
    for g in dispatched_table_list:
        # print("g: ", g)
        slice_item_g = sorted(g[0])
        sum_g = g[1]
        deviation_g = sum_g - average

        print("[", end='')
        for q in slice_item_g:
            if len(q) == 1:
                print("{0}, ".format(q[0]), end='')
            elif len(q) == 2:
                print("({0}=>{1}, )".format(q[0], q[1]), end='')
            else:
                print("{0}, ".format(q), end='')

        print("]", end=' ')
        print("{0} ({1:.2f})".format(sum_g, deviation_g))


if __name__ == "__main__":
    # import sys

    if len(sys.argv) > 1:
        load_slices_data(sys.argv[1])
    else:
        load_slices_data(SLICES_DATA_FILE)


    slices_sorted_by_value = sorted(slices_data_table.items(),
                                    key=lambda d: d[1],
                                    reverse=True)

    case_numbers = len(slices_sorted_by_value)
    sum_all_samples = sum_segment(0, case_numbers-1, slices_sorted_by_value)
    average_samples = sum_all_samples / DOCDORS

    dispatched_table = strategy3(slices_sorted_by_value)

    print_result(dispatched_table, average_samples)

    # print(dispatched_table)

    # print(slices_data_table)
    # dispatch_demo_test(slices_data_table)
    # dispatcher(slices_data_table)

    # min_deviation = 1000000000
    # min_dispatched_table = []

    # for i in range(1, 20):
    #    fluctuation_range = i
    #    d, t = dispatcher_simple(slices_data_table)
    #    print("fluctuation_range: ", fluctuation_range)
    #    print("deviation: ", d)
    #    print("------------------")
    #    if d < min_deviation:
    #        min_deviation = d
    #        min_dispatched_table = t

    # for item in min_dispatched_table:
    #    k = item[2] - average_samples
