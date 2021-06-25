# -*- coding: utf-8 -*-

import logging

from torch import nn
from torch.ao.sparsity import BaseSparsifier

from torch.testing._internal.common_utils import TestCase

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.seq = nn.Sequential(
            nn.Linear(3, 4)
        )
        self.linear = nn.Linear(4, 3)


class ImplementedSparsifier(BaseSparsifier):
    def __init__(self, **kwargs):
        super().__init__(defaults=kwargs)

    def step(self):
        pass


class TestBaseSparsifier(TestCase):
    def test_constructor(self):
        # Cannot instantiate the base
        self.assertRaisesRegex(TypeError, 'with abstract methods step',
                               BaseSparsifier)
        # Can instantiate the model with no configs
        model = Model()
        sparsifier = ImplementedSparsifier(test=3)
        sparsifier.prepare(model, config=None)
        assert len(sparsifier.module_groups) == 2
        sparsifier.step()
        # Can instantiate the model with configs
        sparsifier = ImplementedSparsifier(test=3)
        sparsifier.prepare(model, [model.linear])
        assert len(sparsifier.module_groups) == 1
        assert sparsifier.module_groups[0]['path'] == 'linear'
        assert 'test' in sparsifier.module_groups[0]
        assert sparsifier.module_groups[0]['test'] == 3

    def test_state_dict(self):
        model = Model()
        sparsifier0 = ImplementedSparsifier(test=3)
        sparsifier0.prepare(model, [model.linear])
        state_dict = sparsifier0.state_dict()
        sparsifier1 = ImplementedSparsifier()
        sparsifier1.prepare(model, None)
        assert sparsifier0.module_groups != sparsifier1.module_groups
        sparsifier1.load_state_dict(state_dict)
        assert sparsifier0.module_groups == sparsifier1.module_groups
