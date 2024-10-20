import os 
import json 
import re 
import random 
from collections import defaultdict 
import argparse 

import transformers 
from transformers import BartTokenizer
import torch 
from torch.utils.data import DataLoader
from .utils import load_ontology
import pytorch_lightning as pl 

from .data import IEDataset, my_collate

MAX_LENGTH=424 
MAX_TGT_LENGTH=72
DOC_STRIDE=256 

class RAMSDataModule(pl.LightningDataModule):
    def __init__(self, args):
        super().__init__() 
        self.hparams.update(vars(args))
        self.tokenizer = BartTokenizer.from_pretrained('facebook/bart-large')
        self.tokenizer.add_tokens([' <arg>',' <tgr>'])
    
    def get_event_type(self,ex):
        evt_type = []
        # print(type(ex))
        # print(ex[0])
        # print(ex.keys())
        # print(ex['evt_triggers'])
        for evt in ex['evt_triggers']:
            for t in evt[2]:
                evt_type.append( t[0])
        return evt_type 

    def create_gold_gen(self, ex, ontology_dict,mark_trigger=True):
        '''assumes that each line only contains 1 event.
        Input: <s> Template with special <arg> placeholders </s> </s> Passage </s>
        Output: <s> Template with arguments and <arg> when no argument is found. 
        '''
        ex = json.loads(ex)
        context_words = [w for sent in ex['sentences'] for w in sent ]
        if ('evt_triggers' not in ex.keys()):
          return "", "", self.tokenizer.tokenize(' '.join(context_words), add_prefix_space=True)
        if(self.get_event_type(ex)==[]):
           return "", "", self.tokenizer.tokenize(' '.join(context_words), add_prefix_space=True)
        evt_type = self.get_event_type(ex)[0]
        template = ontology_dict[evt_type.replace('n/a','unspecified')]['template']
        input_template = re.sub(r'<arg\d>', '<arg>', template)
        space_tokenized_input_template = input_template.split(' ')
        tokenized_input_template = [] 
        for w in space_tokenized_input_template:
            tokenized_input_template.extend(self.tokenizer.tokenize(w, add_prefix_space=True))
        if len(ex['gold_evt_links']) == 0:
            iterlist = []
        else:
            iterlist = ex['gold_evt_links'][0]
        for triple in iterlist:
            trigger_span, argument_span, arg_name = triple
            try:
                arg_num = ontology_dict[evt_type][arg_name]
            except:
                arg_num = -1
                for key in ontology_dict:
                    if arg_name in ontology_dict[key].keys():
                        arg_num = ontology_dict[key][arg_name]
                        break
            if arg_num == -1:
                arg_num = '<arg2>'
            arg_text = ' and '.join(context_words[argument_span[0]:argument_span[1]+1])
            # print(arg_text)

            template = re.sub('<{}>'.format(arg_num),arg_text , template)
            # print(template)
            

        trigger = ex['evt_triggers'][0]
        if mark_trigger:

            trigger_span_start = trigger[0]
            trigger_span_end = trigger[1] +2 # one for inclusion, one for extra start marker 
            prefix = self.tokenizer.tokenize(' '.join(context_words[:trigger[0]]), add_prefix_space=True) 
            tgt = self.tokenizer.tokenize(' '.join(context_words[trigger[0]: trigger[1]+1]), add_prefix_space=True)
            
            suffix = self.tokenizer.tokenize(' '.join(context_words[trigger[1]+1:]), add_prefix_space=True)
            context = prefix + [' <tgr>', ] + tgt + [' <tgr>', ] + suffix 
        else:
            context = self.tokenizer.tokenize(' '.join(context_words), add_prefix_space=True)
        trigger_span_start = trigger[0]
        trigger_span_end = trigger[1] +1
        trigger_text = ' '.join(context_words[trigger_span_start:trigger_span_end])
        output_template = re.sub(r'<arg\d>','<arg>', template ) 
        # output_template = trigger_text + ' trigger ' + output_template
        print("Input template", input_template)
        print('Output template', output_template)
        space_tokenized_template = output_template.split(' ')
        tokenized_template = [] 
        for w in space_tokenized_template:
            tokenized_template.extend(self.tokenizer.tokenize(w, add_prefix_space=True))
        
        return tokenized_input_template, tokenized_template, context

    

    def load_ontology(self):
        # read ontology 
        # ontology_dict = load_ontology('KAIROS')
        # keys_to_modify = []
        # for key in ontology_dict.keys():
        #     new_key = key.split(".")[0] + "." + key.split(".")[1]
        #     if new_key != key:
        #         keys_to_modify.append((key, new_key))

        # for key, new_key in keys_to_modify:
        #     ontology_dict[new_key] = ontology_dict.pop(key)

        # for key in ontology_dict.keys():
        #     args = ontology_dict[key]['roles']
        #     for i, arg in enumerate(args):
        #         if arg != '':
        #             ontology_dict[key]['arg{}'.format(i+1)] = arg 
        #             ontology_dict[key][arg] = 'arg{}'.format(i+1)
        ontology_dict ={} 
        with open('aida_ontology_cleaned.csv','r') as f:
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
        first_key, first_value = next(iter(ontology_dict.items()))
        # print("Ontology", first_key, first_value)
        return ontology_dict 

    def prepare_data(self):
        if not os.path.exists('preprocessed_data'):
            os.makedirs('preprocessed_data')

            ontology_dict = self.load_ontology() 
            
            for split,f in [('train',self.hparams.train_file), ('val',self.hparams.val_file), ('test',self.hparams.test_file)]:
                with open(f,'r') as reader,  open('preprocessed_data/{}.jsonl'.format(split), 'w') as writer:
                    for lidx, line in enumerate(reader):
                        ex = json.loads(line.strip())
                        input_template, output_template, context= self.create_gold_gen(ex, ontology_dict, self.hparams.mark_trigger)
                        
                        
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

                        processed_ex = {
                            # 'idx': lidx, 
                            'doc_key': json.loads(ex)['doc_key'],
                            'input_token_ids':input_tokens['input_ids'],
                            'input_attn_mask': input_tokens['attention_mask'],
                            'tgt_token_ids': tgt_tokens['input_ids'],
                            'tgt_attn_mask': tgt_tokens['attention_mask'],
                        }
                        writer.write(json.dumps(processed_ex) + '\n')
            


    
    def train_dataloader(self):
        dataset = IEDataset('preprocessed_data/train.jsonl')
        
        dataloader = DataLoader(dataset, 
            pin_memory=True, num_workers=2, 
            collate_fn=my_collate,
            batch_size=self.hparams.train_batch_size, 
            shuffle=True)
        return dataloader 

    
    def val_dataloader(self):
        dataset = IEDataset('preprocessed_data/val.jsonl')
        
        dataloader = DataLoader(dataset, pin_memory=True, num_workers=2, 
            collate_fn=my_collate,
            batch_size=self.hparams.eval_batch_size, shuffle=False)
        return dataloader

    def test_dataloader(self):
        dataset = IEDataset('preprocessed_data/test.jsonl')
        
        dataloader = DataLoader(dataset, pin_memory=True, num_workers=2, 
            collate_fn=my_collate, 
            batch_size=self.hparams.eval_batch_size, shuffle=False)

        return dataloader


if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('--train-file',type=str,default='data/RAMS_1.0/data/train.jsonlines')
    parser.add_argument('--val-file', type=str, default='data/RAMS_1.0/data/dev.jsonlines')
    parser.add_argument('--test-file', type=str, default='data/RAMS_1.0/data/test.jsonlines')
    parser.add_argument('--train_batch_size', type=int, default=2)
    parser.add_argument('--eval_batch_size', type=int, default=4)
    parser.add_argument('--mark-trigger', action='store_true', default=True)
    args = parser.parse_args() 

    dm = RAMSDataModule(args=args)
    dm.prepare_data() 

    # training dataloader 
    dataloader = dm.train_dataloader() 

    for idx, batch in enumerate(dataloader):
        print(batch)
        break 

    # val dataloader 