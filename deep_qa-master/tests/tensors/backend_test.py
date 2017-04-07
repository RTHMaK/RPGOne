# pylint: disable=no-self-use,invalid-name
import numpy
from numpy.testing import assert_allclose
from keras import backend as K

from deep_qa.tensors.backend import cumulative_sum, hardmax
from ..common.test_case import DeepQaTestCase


class TestBackendTensorFunctions(DeepQaTestCase):
    def test_hardmax(self):
        batch_size = 3
        knowledge_length = 5
        unnormalized_attention = K.variable(numpy.random.rand(batch_size, knowledge_length))
        hardmax_output = hardmax(unnormalized_attention, knowledge_length)
        input_value = K.eval(unnormalized_attention)
        output_value = K.eval(hardmax_output)
        assert output_value.shape == (batch_size, knowledge_length)
        # Assert all elements other than the ones are zeros
        assert numpy.count_nonzero(output_value) == batch_size
        # Assert the max values in all rows are ones
        assert numpy.all(numpy.equal(numpy.max(output_value, axis=1),
                                     numpy.ones((batch_size,))))
        # Assert ones are in the right places
        assert numpy.all(numpy.equal(numpy.argmax(output_value, axis=1),
                                     numpy.argmax(input_value, axis=1)))

    def test_cumulative_sum(self):
        vector = numpy.asarray([1, 2, 3, 4, 5])
        result = K.eval(cumulative_sum(K.variable(vector)))
        assert_allclose(result, [1, 3, 6, 10, 15])

        vector = numpy.asarray([[1, 2, 3, 4, 5],
                                [1, 1, 1, 1, 1],
                                [3, 5, 0, 0, 0]])
        result = K.eval(cumulative_sum(K.variable(vector)))
        assert_allclose(result, [[1, 3, 6, 10, 15],
                                 [1, 2, 3, 4, 5],
                                 [3, 8, 8, 8, 8]])
