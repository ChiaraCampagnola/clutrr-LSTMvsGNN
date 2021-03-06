# -*- coding: utf-8 -*-
# From Pasquale's repo, minor edits in parse method

import csv
import yaml
import json

import numpy as np
import torch

from collections import OrderedDict

from typing import List, Tuple, Any, Optional, Dict

Triple = Fact = Tuple[str, str, str]
Story = List[Fact]

class Instance:
    def __init__(self,
                 story: Story,
                 target: Fact,
                 nb_nodes: Optional[int] = None):
        self._story = story
        self._target = target
        self._nb_nodes = nb_nodes

    @property
    def story(self) -> Story:
        return self._story

    @property
    def target(self) -> Fact:
        return self._target

    @property
    def nb_nodes(self) -> Optional[int]:
        return self._nb_nodes

    def __str__(self) -> str:
        return f'{self.story}\t{self.target}'


class Data:
    def __init__(self,
                 train_path: str = 'data/clutrr-data/data_089907f8/1.2,1.3_train.csv',
                 test_paths: Optional[List[str]] = None):

        # Open the relations file and set up a series of lists/dicts containing types of relationships
        with open('data/clutrr-data/store/relations_store.yaml', 'r') as f:
            rs = yaml.safe_load(f)

        self.relation_to_predicate = {r['rel']: k for k, v in rs.items()
                                      for _, r in v.items() if k != 'no-relation'}

        self.relation_lst = sorted({r for r in self.relation_to_predicate.keys()})
        self.predicate_lst = sorted({p for p in self.relation_to_predicate.values()})

        self.predicate_to_relations = {p: [r for r in self.relation_lst if p == self.relation_to_predicate[r]]
                                       for p in self.predicate_lst}

        self._train_instances = Data.parse(train_path)
        entity_set = {s for i in self.train for (s, _, _) in i.story} | {o for i in self.train for (_, _, o) in i.story}

        #self._test_instances = OrderedDict()
        self._test_instances = []
        for test_path in (test_paths if test_paths is not None else []):
            i_lst = Data.parse(test_path)
            self._test_instances.extend(i_lst)
            entity_set |= {s for i in i_lst for (s, _, _) in i.story} | {o for i in i_lst for (_, _, o) in i.story}

        self.entity_lst = sorted(entity_set)

        for instance in self.train:
            for s, r, o in instance.story:
                assert s in self.entity_lst and o in self.entity_lst
                assert r in self.relation_lst
                
        # self._all_triples = self.get_all_triples()

    @property
    def train(self) -> List[Instance]:
        return self._train_instances

    @property
    def test(self) -> Dict[str, List[Instance]]:
        return self._test_instances
    
    # @property
    # def all_triples(self) -> List[Triple]:
    #     return self._all_triples

    @staticmethod
    def _to_obj(s: str) -> Any:
        return json.loads(s.replace(")", "]").replace("(", "[").replace("'", "\""))

    @staticmethod
    def parse(path: str) -> List[Instance]:
        res = []
        with open(path, newline='') as f:
            reader = csv.reader(f)
            next(reader) # Skip first line
            for row in reader:
                _, _, _, query, _, target, _, _, _, _, _, story_edges, edge_types, _, genders, _, node_mapping, _ = row
                # nb_nodes = int(node_mapping[node_mapping.rfind(":") + 2:-1]) + 1
                nb_nodes = node_mapping.count(":") # Faster and easier to understand to me, not clear on reason for the other method
                id_to_name = {i: name.split(':')[0] for i, name in enumerate(genders.split(','))}
                _story, _edge, _query = Data._to_obj(story_edges), Data._to_obj(edge_types), Data._to_obj(query)
                triples = [(id_to_name[s_id], p, id_to_name[o_id]) for (s_id, o_id), p in zip(_story, _edge)]
                target = (_query[0], target, _query[1])
                instance = Instance(triples, target, nb_nodes=nb_nodes)
                res += [instance]
        return res
    
    
    # def get_all_triples(self):
    #     '''
    #     Extract all the triples present in the data (in stories/targets, train/test)
    #     '''
    #     triples = []
        
    #     for i in range(len(self.train)):
    #         triples += self.train[i].story
    #         triples += [self.train[i].target]
        
    #     for i in range(len(self.test)):
    #         triples += self.test[i].story
    #         triples += [self.test[i].target]

    #     return triples
##