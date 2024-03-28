#!/usr/bin/env bash
set -e 
set -x 

python train.py --model=gen --ckpt_name='gen-RAMS' \
    --dataset=RAMS \
    --train_file=data/RAMS_1.0/data/random-train.jsonl \
    --val_file=data/RAMS_1.0/data/random-dev.jsonl \
    --test_file=data/RAMS_1.0/data/random-test.jsonl \
    --train_batch_size=16 \
    --eval_batch_size=4 \
    --learning_rate=3e-5 \
    --accumulate_grad_batches=4 \
    --num_train_epochs=40 \
