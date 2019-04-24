import argparse
import os
import pandas as pd
import numpy as np


def save_tsne_embeddings(prefix, embeddings, user_index, index2username):
    embeddings_df = pd.DataFrame(data=embeddings)
    embedding_file = prefix + ".embedding"
    node_info_file = prefix + ".nodes.info"
    embeddings_df.to_csv(embedding_file, sep="\t", header=None, index=False)
    with open(node_info_file, "w+") as info_file:
        info_file.write("user_index\treal_name\n")
        for i in user_index:
            info_file.write(str(i)+"\t"+str(index2username[i])+"\n")

def generate_tsne_format_embeddings(args):
    users_df = pd.read_csv(os.path.join(args.preprocess_dir, "users.csv"))
    index2username = {row["user_index"]: row["real_name"]
                      for index, row in users_df.iterrows()}
    if not os.path.exists(os.path.join(args.output_dir, "graphs")):
        os.makedirs(os.path.join(args.output_dir, "graphs"))
    for graph_dir in os.listdir(os.path.join(args.embedding_dir, "graphs")):
        if not os.path.exists(os.path.join(args.output_dir, "graphs", graph_dir)):
            os.makedirs(os.path.join(args.output_dir, "graphs", graph_dir))
        for embedding_file in os.listdir(os.path.join(args.embedding_dir, "graphs", graph_dir)):
            embedding_df = pd.read_csv(os.path.join(args.embedding_dir, "graphs", graph_dir, embedding_file), header=None, skiprows=1, sep="\s")
            user_index = embedding_df.values[:, 0].astype(np.int32)
            embeddings = embedding_df.values[:, 1:]
            basename, _ = os.path.splitext(embedding_file)
            output_prefix = os.path.join(args.output_dir, "graphs", graph_dir, basename)
            
            save_tsne_embeddings(output_prefix, embeddings, user_index, index2username)


def main(args):
    assert os.path.exists(args.preprocess_dir), "Process dir does not exists"
    assert os.path.exists(args.embedding_dir), "Embeddings dir does not exists"
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    generate_tsne_format_embeddings(args)
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--preprocess_dir',default='logs/iCog/preprocess')
    parser.add_argument('-e', '--embedding_dir', default='logs/iCog/embeddings')
    parser.add_argument('-o', '--output_dir', default='logs/iCog/embeddings-for-tsne')

    
    args = parser.parse_args()
    main(args)
