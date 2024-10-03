import random
import pdb
import sys
import os 
import json 
import re
import argparse 

from tqdm import tqdm
from nltk import wordpunct_tokenize
from transformers import BartTokenizer
from torch.utils.data import DataLoader 
import pytorch_lightning as pl 

sys.path.insert(0,'./src/genie')
from data import IEDataset, my_collate
from utils import flatten, choose_earliest

random.seed(123)

MAX_LENGTH=500
MAX_TGT_LENGTH=120

class MUCDataModule(pl.LightningDataModule):
    def __init__(self, args):
        super().__init__() 
        for key in args.keys():
            self.hparams[key] = args[key]
        self.tokenizer = BartTokenizer.from_pretrained('facebook/bart-large')
        self.tokenizer.add_tokens([' <arg>', ' <tgr>', ' <sep>'])
        with open(args["scorer_dataset_config"]) as f:
            self.dataset_config = json.load(f)
        
    def create_gold_gen(self, ex, ontology_dict, is_test=False):
        '''assumes that each line only contains 1 event.
        Input: <s> Template with special <arg> placeholders </s> </s> Passage </s>
        Output: <s> Template with arguments and <arg> when no argument is found. 
        '''
        context_words = wordpunct_tokenize(ex['doctext'])
        inputs, outputs, contexts, event_types = [], [], [], []
        
        all_evt_types = self.dataset_config["event_type_names"]
        list_evt_types = [t["incident_type"] for t in ex['templates']]
        evt_types = set(list_evt_types)
        negative_evt_types = random.sample(set(all_evt_types).difference(evt_types), 
                                            k=max(self.hparams['negative'] - len(evt_types), 0))
        evt_types = evt_types.union(negative_evt_types)
        if is_test:
            negative_evt_types = list(set(all_evt_types).difference(list_evt_types))
            evt_types = all_evt_types
        evt_types = {k: [None, [], None] for k in evt_types}
        
        # print(list_evt_types)
        # print(negative_evt_types)
        # print(evt_types)
        for event_i, evt_type in enumerate(list_evt_types + negative_evt_types):
            # evt_type = event['incident_type']
            event = None
            if event_i < len(list_evt_types):
                event = ex['templates'][event_i]
            
            template = ontology_dict[evt_type]['template']
            input_template = re.sub(r'<arg\d>', '<arg>', template)
            
            space_tokenized_input_template = input_template.split(' ')
            tokenized_input_template = [] 
            for w in space_tokenized_input_template:
                tokenized_input_template.extend(self.tokenizer.tokenize(w, add_prefix_space=True))
        
            for arg_name in self.dataset_config["role_names"]:
                if event == None or arg_name not in event or len(event[arg_name]) == 0:
                    continue
                arg_text, argument_span = choose_earliest(flatten(event[arg_name]))
                arg_num = ontology_dict[evt_type][arg_name]
                # arg_text = ' '.join(context_words[argument_span[0]:argument_span[1]+1])
                template = re.sub('<{}>'.format(arg_num), arg_text, template)
            
            context = self.tokenizer.tokenize(' '.join(context_words), add_prefix_space=True)

            output_template = re.sub(r'<arg\d>','<arg>', template) 
            space_tokenized_template = output_template.split(' ')
            tokenized_template = [] 
            for w in space_tokenized_template:
                tokenized_template.extend(self.tokenizer.tokenize(w, add_prefix_space=True))
            evt_types[evt_type][0] = tokenized_input_template
            tokenized_template = ([" <sep>"] + tokenized_template) if len(evt_types[evt_type][1]) != 0 else tokenized_template
            evt_types[evt_type][1].extend(tokenized_template)
            evt_types[evt_type][2] = context
        
        for evt_type in evt_types:
            event_types.append(evt_type)
            contexts.append(evt_types[evt_type][2])
            inputs.append(evt_types[evt_type][0])
            outputs.append(evt_types[evt_type][1])
            
        assert len(contexts) == len(event_types)
        assert len(contexts) == len(inputs)
        assert len(contexts) == len(outputs)
        return inputs, outputs, contexts, event_types
        
    def load_ontology(self):
        # read ontology 
        ontology_dict ={} 
        with open('muc_ontology_cleaned.csv','r') as f:
            for lidx, line in enumerate(f):
                if lidx == 0:# header 
                    continue 
                fields = line.strip().split(',') 
                if len(fields) < 2:
                    break 
                evt_type = fields[0]
                args = fields[2:]
                
                ontology_dict[evt_type] = {
                        'template': fields[1]
                    }
                
                for i, arg in enumerate(args):
                    if arg !='':
                        ontology_dict[evt_type]['arg{}'.format(i+1)] = arg 
                        ontology_dict[evt_type][arg] = 'arg{}'.format(i+1)
        return ontology_dict 
    

    def prepare_data(self):
        if not os.path.exists('preprocessed_{}'.format(self.hparams.dataset)):
            os.makedirs('preprocessed_{}'.format(self.hparams.dataset))

        ontology_dict = self.load_ontology() 
        
        for split, f in [('train', self.hparams.train_file), ('val', self.hparams.val_file), ('test', self.hparams.test_file)]:
            with open(f, 'r') as reader,  open('preprocessed_{}/{}.jsonl'.format(self.hparams.dataset, split), 'w') as writer:
                data = json.load(reader)
                for lidx, ex in enumerate(tqdm(data.values())):
                    input_templates, output_templates, \
                        contexts, event_types = self.create_gold_gen(ex, ontology_dict, is_test=split!="train")
                    for input_template, output_template, context, evt_type in zip(input_templates, output_templates, 
                                                                                  contexts, event_types):
                        # print(input_template, output_template, evt_type)
                        input_tokens = self.tokenizer.encode_plus(input_template, context, 
                                add_special_tokens=True,
                                add_prefix_space=True,
                                max_length=MAX_LENGTH,
                                truncation='only_second',
                                padding='max_length')
                        tgt_tokens = self.tokenizer.encode_plus(output_template, 
                        add_special_tokens=True,
                        add_prefix_space=True, 
                        max_length=MAX_TGT_LENGTH,
                        truncation=True,
                        padding='max_length')
                        
                        # print(len(input_tokens['input_ids']), len(input_tokens['attention_mask']), 
                        #       len(tgt_tokens['input_ids']), len(tgt_tokens['attention_mask']))
                        # print(self.tokenizer.decode(input_tokens['input_ids']))
                        # print(self.tokenizer.decode(tgt_tokens['input_ids']))
                        # # if len(input_tokens) > 512:
                        # #     print("issue")
                        # print()

                        processed_ex = {
                            # 'idx': lidx, 
                            'doc_key': f"{ex['docid']}_{evt_type}",
                            'input_token_ids':input_tokens['input_ids'],
                            'input_attn_mask': input_tokens['attention_mask'],
                            'tgt_token_ids': tgt_tokens['input_ids'],
                            'tgt_attn_mask': tgt_tokens['attention_mask'],
                        }
                        writer.write(json.dumps(processed_ex) + '\n')

    def train_dataloader(self):
        # if self.hparams.tmp_dir:
        #     data_dir = self.hparams.tmp_dir
        # else:
        data_dir = 'preprocessed_{}'.format(self.hparams.dataset)

        dataset = IEDataset(os.path.join(data_dir, 'train.jsonl'))
        
        dataloader = DataLoader(dataset, 
            pin_memory=True, num_workers=2, 
            collate_fn=my_collate,
            batch_size=self.hparams.train_batch_size, 
            shuffle=True)
        return dataloader 

    
    def val_dataloader(self):
        # if self.hparams.tmp_dir:
        #     data_dir = self.hparams.tmp_dir
        # else:
        data_dir = 'preprocessed_{}'.format(self.hparams.dataset)

        dataset = IEDataset(os.path.join(data_dir, 'val.jsonl'))
        
        
        dataloader = DataLoader(dataset, pin_memory=True, num_workers=2, 
            collate_fn=my_collate,
            batch_size=self.hparams.eval_batch_size, shuffle=False)
        return dataloader

    def test_dataloader(self):
        # if self.hparams.tmp_dir:
        #     data_dir = self.hparams.tmp_dir
        # else:
        data_dir = 'preprocessed_{}'.format(self.hparams.dataset)

        dataset = IEDataset(os.path.join(data_dir, 'test.jsonl'))
        
        
        dataloader = DataLoader(dataset, pin_memory=True, num_workers=2, 
            collate_fn=my_collate, 
            batch_size=self.hparams.eval_batch_size, shuffle=False)

        return dataloader
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('--train-file',type=str,
                        default='../Dataset/datasets/MUC/keyword/train.json')
    parser.add_argument('--val-file', type=str, 
                        default='../Dataset/datasets/MUC/keyword/dev.json')
    parser.add_argument('--test-file', type=str, 
                        default='../Dataset/datasets/MUC/keyword/test.json')
    parser.add_argument('--tmp_dir', default='')
    parser.add_argument('--train_batch_size', type=int, 
                        default=12)
    parser.add_argument('--eval_batch_size', type=int, 
                        default=14)
    parser.add_argument('--dataset', type=str, 
                        default='MUC')
    parser.add_argument('--negative', type=int, 
                        default=3)
    parser.add_argument('--scorer_dataset_config', type=str, 
                        default="../DEGREE/degree/muc_config.json")
    
    args = parser.parse_args().__dict__
    
    dm = MUCDataModule(args=args)
    dm.prepare_data() 

    # training dataloader 
    dataloader = dm.train_dataloader() 

    for idx, batch in enumerate(dataloader):
        break 

