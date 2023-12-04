#!/usr/bin/env bash
set -e 
set -x 

CKPT_NAME='gen-KAIROS'
rm -rf checkpoints/${CKPT_NAME}

# does not use informative mentions 
python3 train.py --model=constrained-gen --ckpt_name=${CKPT_NAME} \
    --dataset=KAIROS \
    --train_file=data/wikievents/no-triggers_train.jsonl \
    --val_file=data/wikievents/no-triggers-dev.jsonl \
    --test_file=data/wikievents/no-triggers-test.jsonl \
    --train_batch_size=2 \
    --eval_batch_size=4 \
    --learning_rate=3e-5 \
    --accumulate_grad_batches=8 \
    --num_train_epochs=2 \
    --mark_trigger \
    --coref_dir=data/wikievents/coref
