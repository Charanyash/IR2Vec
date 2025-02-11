# Part of the IR2Vec Project, under the Apache License v2.0 with LLVM
# Exceptions. See the LICENSE file for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#

import config
import models
import tensorflow as tf
import numpy as np
import os
import sys
import json
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def train(arg_conf):
    con = config.Config()
    con.set_in_path(arg_conf.index_dir)
    con.set_work_threads(4)
    con.set_train_times(arg_conf.epoch)
    con.set_nbatches(nbatches=arg_conf.nbatches)
    con.set_alpha(0.001)
    con.set_margin(arg_conf.margin)
    con.set_bern(0)
    con.set_dimension(arg_conf.dim)
    con.set_ent_neg_rate(1)
    con.set_rel_neg_rate(0)
    con.set_opt_method("SGD")

    outfile = os.path.join(
        arg_conf.index_dir,
        "seedEmbedding_{}E_{}D_{}batches{}margin.json".format(
            arg_conf.epoch,
            arg_conf.dim,
            arg_conf.nbatches,
            arg_conf.margin,
        ),
    )
    con.set_out_files(outfile)
    con.init()
    # Set the knowledge embedding model
    con.set_model(models.TransE)
    # Train the model.
    con.run()
    return outfile


def findRep(src, dest, ent):
    f = open(src)
    data = json.loads(f.read())
    rep = data["ent_embeddings"]
    f.close()
    f = open(os.path.join(ent, "entity2id.txt"))
    content = f.read()
    f.close()

    f = open(dest, "w")
    entities = content.split("\n")
    toTxt = ""

    for i in range(1, int(entities[0])):
        toTxt += entities[i].split("\t")[0] + ":" + str(rep[i - 1]) + ",\n"
    toTxt += (
        entities[int(entities[0])].split("\t")[0] + ":" + str(rep[int(entities[0]) - 1])
    )
    f.write(toTxt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index_dir",
        dest="index_dir",
        metavar="DIRECTORY",
        help="Location of th directory entity2id.txt, train2id.txt and relation2id.txt",
        required=True,
    )
    parser.add_argument(
        "--epoch", dest="epoch", help="Epochs", required=False, type=int, default=1500
    )
    parser.add_argument(
        "--dim",
        dest="dim",
        help="Dimension of the embedding",
        required=False,
        type=int,
        default=300,
    )
    parser.add_argument(
        "--nbatches",
        dest="nbatches",
        help="Number of batches",
        required=False,
        type=int,
        default=100,
    )
    parser.add_argument(
        "--margin",
        dest="margin",
        help="Margin",
        required=False,
        type=float,
        default=1.0,
    )

    arg_conf = parser.parse_args()

    outfilejson = train(arg_conf)

    seedfile = os.path.join(
        arg_conf.index_dir,
        "embeddings/seedEmbedding_{}E_{}D_{}batches{}margin.txt".format(
            arg_conf.epoch, arg_conf.dim, arg_conf.nbatches, arg_conf.margin
        ),
    )

    findRep(outfilejson, seedfile, arg_conf.index_dir)

    print("Training finished...")
    print("seed file : ", seedfile)
