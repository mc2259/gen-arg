#!/usr/bin/env bash
set -e 
set -x 

CKPT_NAME='gen-KAIROS'
rm -rf checkpoints/${CKPT_NAME}

# does not use informative mentions 
python3 train.py --model=constrained-gen --ckpt_name=${CKPT_NAME} \
    --dataset=KAIROS \
    --train_file=data/wikievents/processed_train_gpt4.jsonl \
    --val_file=data/wikievents/processed_dev_gpt4.jsonl \
    --test_file=data/wikievents/processed_test_gpt4.jsonl \
    --train_batch_size=2 \
    --eval_batch_size=4 \
    --learning_rate=3e-5 \
    --accumulate_grad_batches=8 \
    --num_train_epochs=2 \
    --coref_dir=data/wikievents/coref
