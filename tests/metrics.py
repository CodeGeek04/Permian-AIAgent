def calculate_accuracy(result_dict_list):
    count = 0
    for result_dict in result_dict_list:
        count += 1 if result_dict["done"] else 0
    return count / len(result_dict_list)

def calculate_latency(result_dict_list):
    lantency = [result_dict["time"] for result_dict in result_dict_list if result_dict["done"] != 0]
    if "rec_time" in result_dict_list[0]:
        rec_latency = [result_dict["rec_time"] for result_dict in result_dict_list if result_dict["done"] != 0]
        return sum(lantency) / len(lantency), sum(rec_latency) / len(rec_latency)
    else:
        return sum(lantency) / len(lantency)

def calculate_topk(result_dict_list, k=3):
    count = 0
    for result_dict in result_dict_list:
        count += 1 if result_dict[f"top@{k}"] else 0
    return count / len(result_dict_list)