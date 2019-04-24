graphs_path="logs/iCog/preprocess/graphs"
output_path="logs/iCog/embeddings/graphs"
deepwalk_dim=64
node2vec_dim=128
struc2vec_dim=128
node2vec_num_walks=100
struc2vec_num_walks=100

# generate using deep walk

source activate watch_ys
for g_folder in "$graphs_path/"*; do
    graph=$(basename "$g_folder")
    directed=false;
    if [[ "$graph" = @(DIRECTED|MENTION|REPLY|RESPONSE_RATE) ]]; then
        directed=true;

    fi;
    echo "Creating embedding for $graph graph"
    mkdir -p "$output_path"/"$graph"/
    adjacent_list_file="$g_folder"/adjacent-list.txt
    edge_list_file="$g_folder"/edge-list.txt
    if [ $directed = true ]; then
        deepwalk --input $edge_list_file --output "$output_path"/"$graph"/deepwalk.embeddings --format edgelist --undirected 0 --representation-size $deepwalk_dim 
    else
        deepwalk --input $adjacent_list_file --output "$output_path"/"$graph"/deepwalk.embeddings --format adjlist --undirected 1 --representation-size $deepwalk_dim 
    fi
done


# generate using node2vec

source activate node2vec
i=0;
for g_folder in "$graphs_path/"*; do
    graph=$(basename "$g_folder")
    directed=false;
    weighted=false;
    if [[ "$graph" = @(DIRECTED|MENTION|REPLY|RESPONSE_RATE) ]]; then
        directed=true;
        weighted=true;
    fi;
    if [ "$graph" = "UNDIRECTED" ]; then
        weighted=true;
    fi
    echo "Creating embedding for $graph graph"
    mkdir -p "$output_path"/"$graph"/
    edge_list_file="$g_folder"/edge-list.txt
    if [ $directed = true ] && [ $weighted = true ] ; then
        python node2vec/src/main.py --input $edge_list_file --output "$output_path"/"$graph"/node2vec.embeddings  --dimensions $node2vec_dim --num-walks $node2vec_num_walks --weighted --directed;
    elif [ $directed = true ]; then 
        python node2vec/src/main.py --input $edge_list_file --output "$output_path"/"$graph"/node2vec.embeddings  --dimensions $node2vec_dim --num-walks $node2vec_num_walks --directed;
    elif [ $weighted = true ]; then
        python node2vec/src/main.py --input $edge_list_file --output "$output_path"/"$graph"/node2vec.embeddings  --dimensions $node2vec_dim --num-walks $node2vec_num_walks --weighted;
    else 
        python node2vec/src/main.py --input $edge_list_file --output "$output_path"/"$graph"/node2vec.embeddings  --dimensions $node2vec_dim --num-walks $node2vec_num_walks;
    fi
done

# generate using struc2vec

source activate node2vec
i=0;
for g_folder in "$graphs_path/"*; do
    graph=$(basename "$g_folder")
    directed=false;
    weighted=false;
    if [[ "$graph" = @(DIRECTED|MENTION|REPLY|RESPONSE_RATE) ]]; then
        directed=true;
        weighted=true;
    fi;
    if [ "$graph" = "UNDIRECTED" ]; then
        weighted=true;
    fi
    echo "Creating embedding for $graph graph"
    mkdir -p "$output_path"/"$graph"/
    edge_list_file="$g_folder"/edge-list.txt
    if [ $directed = true ] && [ $weighted = true ] ; then
        python src/main.py --input $edge_list_file --output "$output_path"/"$graph"/struc2vec.embeddings  --dimensions $struc2vec_dim --num-walks $struc2vec_num_walks --weighted --directed;
    elif [ $directed = true ]; then 
        python src/main.py --input $edge_list_file --output "$output_path"/"$graph"/struc2vec.embeddings  --dimensions $struc2vec_dim --num-walks $struc2vec_num_walks --directed;
    elif [ $weighted = true ]; then
        python src/main.py --input $edge_list_file --output "$output_path"/"$graph"/struc2vec.embeddings  --dimensions $struc2vec_dim --num-walks $struc2vec_num_walks --weighted;
    else 
        python src/main.py --input $edge_list_file --output "$output_path"/"$graph"/struc2vec.embeddings  --dimensions $struc2vec_dim --num-walks $struc2vec_num_walks;
    fi
done