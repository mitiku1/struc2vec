import argparse
import os
import pandas as pd
import numpy as np
import json
import pickle

graphs_meta = {
    "COMMON_MESSAGE_CATEGORY": {
        "weighted": False,
        "directed": False,
        "attributed": False
    },
    
    "COMMON_REACTION_TYPE_1": {
        "weighted": False,
        "directed": False,
        "attributed": False
    },
    "COMMON_REACTION_TYPE_2": {
        "weighted": False,
        "directed": False,
        "attributed": False
    },
    "COMMON_TOPIC": {
        "weighted": False,
        "directed": False,
        "attributed": False
    },
    
    
    "CONNECTED": {
        "weighted": False,
        "directed": False,
        "attributed": False
    },
    "DIRECTED": {
        "weighted": True,
        "directed": True,
        "attributed": False
    },
    "MENTION": {
        "weighted": True,
        "directed": True,
        "attributed": False
    },
    
    # "MESSAGE_CATEGORY": {
    #     "weighted": True,
    #     "directed": True,
    #     "attributed": True
    # },
    # "MESSAGE_TOPIC_TYPE": {
    #     "weighted": True,
    #     "directed": True,
    #     "attributed": True
    # },
    "NEIGHBORHOOD_POST": {
        "weighted": False,
        "directed": False,
        "attributed": False
    },

    "REPLY": {
        "weighted": True,
        "directed": True,
        "attributed": False
    },
    "RESPONSE_RATE": {
        "weighted": True,
        "directed": True,
        "attributed": False
    },
    # "SENTIMENT": {
    #     "weighted": True,
    #     "directed": True,
    #     "attributed": True
    # },
    "UNDIRECTED": {
        "weighted": True,
        "directed": False,
        "attributed": False
    },
   
}


def get_slack_id2username(slack_user_file):
    with open(slack_user_file) as data_file:
        slack_data = json.load(data_file)
    id2username = {}
    for user in slack_data:
        id2username[user["id"]] = user["name"]
    return id2username
def get_data2hash(hash_data_file):
    hash_df = pd.read_csv(hash_data_file, header=None, names = ["hash_code", "data"])
    data2hash = {}
    for index, row in hash_df.iterrows():
        data2hash[row["data"]] = row["hash_code"]
    return data2hash


def load_or_create_users_info(args):
    

    if os.path.exists(os.path.join(args.output_dir, "users.csv")):
        users_df = pd.read_csv(os.path.join(args.output_dir, "users.csv"))
        return users_df
    else:
        assert args.p_analytic_file is not None and os.path.exists(args.p_analytic_file), "Please provide the people analytics excel file path to create users info"
        assert args.slack_users_file is not None and os.path.exists(
            args.slack_users_file),  "Please provide the slack users file path to create users info"
        assert args.hash_data_file is not None and os.path.exists(
            args.hash_data_file),  "Please provide the hash_data file path to create users info"
        users = pd.read_excel(args.p_analytic_file, sheet_name="user")

        slack_id2username = get_slack_id2username(args.slack_users_file)
        slack_username2id = {value: key for key, value in slack_id2username.items()}
        
        data2hash = get_data2hash(args.hash_data_file)
        hash2data = {value: key for key, value in data2hash.items()}
        
        users_info = {"user_hashcode": [], "real_name": []}
        hashcode2real_name = {row["user_hashcode"]: row["real_name"]
                              for index, row in users.iterrows()}

        all_hashcodes = set()
        for data, hashcode in data2hash.items():
            all_hashcodes.add(hashcode)
        for hashcode, name in hashcode2real_name.items():
            all_hashcodes.add(hashcode)
        all_hashcodes = list(all_hashcodes)
        for i in range(len(all_hashcodes)):
            hashcode = all_hashcodes[i]
            if hashcode in hashcode2real_name:
                users_info["real_name"].append(
                    hashcode2real_name[hashcode])
                users_info["user_hashcode"].append(hashcode)
                    
            else:
                if hash2data[hashcode] in slack_username2id:
                    username = hash2data[hashcode]
                elif hash2data[hashcode] in slack_id2username:
                    slack_id = hash2data[hashcode]
                    username = slack_id2username[slack_id]
                else:
                    username = None
                if username is not None:
                    users_info["user_hashcode"].append(hashcode)
                    users_info["real_name"].append(username)
        output = pd.DataFrame(users_info)
        output['user_index'] = np.arange(len(output.index))
        output.to_csv(os.path.join(args.output_dir, "users.csv"), index=False)
        return output


def create_edge_adjacent_list(args, graph, users2index, weighted = False):

    edge_list = []
    adjacent_list = []
    for n1 in graph:
        n1_index = users2index[n1]
        a_list = [n1_index]
        for n2 in graph[n1]:
            n2_index = users2index[n2]
            a_list.append(n2_index)
            if weighted:
                weights = graph[n1][n2]
                if type(weights) == list:
                    if len(weights) > 0:
                        weights = np.mean(weights)
                    else:
                        weights = 0
                edge_list.append([n1_index, n2_index, weights])
            else:
                edge_list.append([n1_index, n2_index])
        adjacent_list.append(a_list)
    return edge_list, adjacent_list

def save_lists(lists, filename):
    with open(filename, "w+") as output_file:
        for l in lists:
            output_file.write(" ".join(map(str, l)) + "\n")
        



def create_graph_info(args, users_info):

    users2index = {row["user_hashcode"]:row["user_index"]
                   for index, row in users_info.iterrows()}
    for graph_file in os.listdir(args.graphs_dir):
        graph_name, _ = os.path.splitext(graph_file)
        graph_name = graph_name.upper()
        if not graph_name in graphs_meta: # Currently this does not work for attributed graphs
            continue
        if not os.path.exists(os.path.join(args.output_dir, graph_name)):
            os.makedirs(os.path.join(args.output_dir, graph_name))
        
        if args.format == "json":
            with open(os.path.join(args.graphs_dir,graph_file), "r") as g_file:
                graph = json.load(g_file)
        else:
            with open(os.path.join(args.graphs_dir,graph_file), "rb") as g_file:
                graph = pickle.load(g_file)

        edge_list, adjacent_list = create_edge_adjacent_list(
            args, graph, users2index, graphs_meta[graph_name]["weighted"])
        edge_list_filename = os.path.join(args.output_dir, graph_name, "edge-list.txt")
        adjacent_list_filename = os.path.join(args.output_dir, graph_name, "adjacent-list.txt")
        save_lists(edge_list, edge_list_filename)
        save_lists(adjacent_list, adjacent_list_filename)



def main(args):

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    users_info = load_or_create_users_info(args)
    create_graph_info(args, users_info)
    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--graphs_dir',default="resources/dataset/iCog/raw-graphs")
    parser.add_argument('-f', '--format', default='json', choices=["pkl", "json"])
    parser.add_argument('-o', '--output_dir', default="logs/iCog/preprocess")
    parser.add_argument('-p', '--p_analytic_file', required=False)
    parser.add_argument('-s', '--slack_users_file', required=False)
    parser.add_argument('--hash_data_file', required=False)
    parser.add_argument('--output-format', default='edge-list', choices=["edge-list", 'adjacent-list'], help="Output of preprocessing:-either edge-list or adjacent-list")

    args = parser.parse_args()
    main(args)
