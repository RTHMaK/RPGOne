# pylint: disable=no-self-use,invalid-name
from deep_qa.data.dataset import Dataset, TextDataset
from deep_qa.data.instances.true_false_instance import TrueFalseInstance
from deep_qa.data.instances.labeled_background_instance import LabeledBackgroundInstance

from ..common.test_case import DeepQaTestCase


class TestDataset:
    def test_merge(self):
        instances = [TrueFalseInstance("testing", None, None), TrueFalseInstance("testing1", None, None)]
        dataset1 = Dataset(instances[:1])
        dataset2 = Dataset(instances[1:])
        merged = dataset1.merge(dataset2)
        assert merged.instances == instances


class TestTextDataset(DeepQaTestCase):
    def test_read_from_file_with_no_default_label(self):
        filename = self.TEST_DIR + 'test_dataset_file'
        with open(filename, 'w') as datafile:
            datafile.write("1\tinstance1\t0\n")
            datafile.write("2\tinstance2\t1\n")
            datafile.write("3\tinstance3\n")
        dataset = TextDataset.read_from_file(filename, TrueFalseInstance)
        assert len(dataset.instances) == 3
        instance = dataset.instances[0]
        assert instance.index == 1
        assert instance.text == "instance1"
        assert instance.label is False
        instance = dataset.instances[1]
        assert instance.index == 2
        assert instance.text == "instance2"
        assert instance.label is True
        instance = dataset.instances[2]
        assert instance.index == 3
        assert instance.text == "instance3"
        assert instance.label is None

    def test_read_labeled_background_from_file_loads_correct_instances(self):
        filename = self.TEST_DIR + 'test_dataset_file'
        with open(filename, 'w') as datafile:
            datafile.write("1\tinstance1\t0\n")
            datafile.write("2\tinstance2\t1\n")
            datafile.write("3\tinstance3\n")
        background_filename = self.TEST_DIR + 'test_dataset_background'
        with open(background_filename, 'w') as datafile:
            datafile.write("1\t2\tb1\tb2\tb3\tb4\n")
            datafile.write("2\t1,3\tb1\tb2\tb3\tb4\n")
            datafile.write("3\t0\tb5\tb6\tb7\tb8\n")
        dataset = TextDataset.read_from_file(filename, TrueFalseInstance)
        background_dataset = TextDataset.read_labeled_background_from_file(dataset, background_filename)
        assert len(background_dataset.instances) == 3
        instance = background_dataset.instances[0]
        assert isinstance(instance, LabeledBackgroundInstance)
        assert instance.instance.index == 1
        assert instance.instance.text == "instance1"
        assert instance.label == [2]
        assert instance.background == ['b1', 'b2', 'b3', 'b4']
        instance = background_dataset.instances[1]
        assert isinstance(instance, LabeledBackgroundInstance)
        assert instance.instance.index == 2
        assert instance.instance.text == "instance2"
        assert instance.label == [1, 3]
        assert instance.background == ['b1', 'b2', 'b3', 'b4']
        instance = background_dataset.instances[2]
        assert isinstance(instance, LabeledBackgroundInstance)
        assert instance.instance.index == 3
        assert instance.instance.text == "instance3"
        assert instance.label == [0]
        assert instance.background == ['b5', 'b6', 'b7', 'b8']
