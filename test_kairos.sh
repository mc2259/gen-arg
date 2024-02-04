#!/usr/bin/env bash
set -e 
set -x 
CKPT_NAME=gen-KAIROS
MODEL=constrained-gen

rm -rf checkpoints/${CKPT_NAME}-pred
python train.py --model=$MODEL --ckpt_name=${CKPT_NAME}-pred \
    --load_ckpt=checkpoints/${CKPT_NAME}/epoch=19-v1.ckpt \
    --dataset=KAIROS \
    --eval_only \
    --train_file=data/wikievents/train_keyword_wikievents.jsonl \
    --val_file=data/wikievents/dev_keyword_wikievents.jsonl \
    --test_file=data/wikievents/test_keyword_wikievents.jsonl \
    --coref_dir=data/wikievents/coref \
    --train_batch_size=4 \
    --eval_batch_size=4 \
    --learning_rate=3e-5 \
    --accumulate_grad_batches=4 \
    --num_train_epochs=3

python src/genie/scorer.py --gen-file=checkpoints/$CKPT_NAME-pred/predictions.jsonl \
--test-file=data/wikievents/test.jsonl \
--dataset=KAIROS \
--coref-file=data/wikievents/coref/test.jsonlines \
--head-only \
--coref 
