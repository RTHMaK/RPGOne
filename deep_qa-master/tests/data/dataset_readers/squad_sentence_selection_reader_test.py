# pylint: disable=no-self-use,invalid-name
from os.path import join
import random

from overrides import overrides
import numpy

from deep_qa.data.dataset_readers.squad_sentence_selection_reader import SquadSentenceSelectionReader
from ...common.test_case import DeepQaTestCase


class TestSquadSentenceSelectionReader(DeepQaTestCase):
    @overrides
    def setUp(self):
        super(TestSquadSentenceSelectionReader, self).setUp()
        # write a SQuAD json file.
        # pylint: disable=bad-continuation
        self.sentences = [
                "Architecturally, the school has a Catholic character.",
                "Atop the Main Building's gold dome is a golden statue of the Virgin Mary.",
                "Immediately in front of the Main Building and facing it, is a copper statue of "
                    "Christ with arms upraised with the legend \\\"Venite Ad Me Omnes\\\".",
                "Next to the Main Building is the Basilica of the Sacred Heart.",
                "Immediately behind the basilica is the Grotto, a Marian place of prayer and reflection.",
                "It is a replica of the grotto at Lourdes, France where the Virgin Mary reputedly "
                    "appeared to Saint Bernadette Soubirous in 1858.",
                "At the end of the main drive (and in a direct line that connects through 3 "
                    "statues and the Gold Dome), is a simple, modern stone statue of Mary.",
                "This is another sentence.",
                "And another one.",
                "Yet another sentence 1.",
                "Yet another sentence 2.",
                "Yet another sentence 3.",
                "Yet another sentence 4.",
                "Yet another sentence 5.",
                ]
        # pylint: enable=bad-continuation
        self.passage1 = " ".join(self.sentences[:7])
        self.passage2 = " ".join(self.sentences[7:])
        self.question0 = "To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?"
        self.question1 = "What is in front of the Notre Dame Main Building?"
        self.questions = [self.question0, self.question1]
        json_string = """
        {
          "data":[
            {
              "title":"University_of_Notre_Dame",
              "paragraphs":[
                {
                  "context":"%s",
                  "qas":[
                    {
                      "answers":[
                        {
                          "answer_start":515,
                          "text":"Saint Bernadette Soubirous"
                        }
                      ],
                      "question":"%s",
                      "id":"5733be284776f41900661182"
                    },
                    {
                      "answers":[
                        {
                          "answer_start":188,
                          "text":"a copper statue of Christ"
                        }
                      ],
                      "question":"%s",
                      "id":"5733be284776f4190066117f"
                    }
                  ]
                },
                {
                  "context":"%s",
                  "qas":[ ]
                }
              ]
            }
          ]
        }
        """ % (self.passage1, self.question0, self.question1, self.passage2)
        with open(self.TEST_DIR + "squad_data.json", "w") as f:
            f.write(json_string)
        random.seed(1337)
        numpy.random.seed(1337)

    def test_reader_should_shuffle_consistently_with_the_same_seed(self):
        random.seed(1337)
        numpy.random.seed(1337)
        reader = SquadSentenceSelectionReader()
        output_filepath = reader.read_file(join(self.TEST_DIR, "squad_data.json"))
        with open(output_filepath, "r") as generated_file:
            lines = []
            for line in generated_file:
                lines.append(line.strip())
        random.seed(1337)
        numpy.random.seed(1337)
        reader = SquadSentenceSelectionReader()
        output_filepath = reader.read_file(join(self.TEST_DIR, "squad_data.json"))
        with open(output_filepath, "r") as generated_file:
            lines2 = []
            for line in generated_file:
                lines2.append(line.strip())
        assert lines == lines2

    def test_default_squad_sentence_selection_reader(self):
        # Note that the ordering of these sentences depends on a a particular shuffling of the
        # data (and thus the random seed set above), and could change if you change the number of
        # shuffles done in the code.  Sorry.
        context0 = "###".join(self.sentences[i] for i in [2, 4, 1, 3, 0, 5, 6]).replace("\\\"", "\"")
        index0 = "5"
        expected_line0 = self.question0 + "\t" + context0 + "\t" + index0

        context1 = "###".join(self.sentences[i] for i in [0, 3, 4, 6, 2, 1, 5]).replace("\\\"", "\"")
        index1 = "4"
        expected_line1 = self.question1 + "\t" + context1 + "\t" + index1

        reader = SquadSentenceSelectionReader()
        output_filepath = reader.read_file(join(self.TEST_DIR, "squad_data.json"))
        with open(output_filepath, "r") as generated_file:
            lines = []
            for line in generated_file:
                lines.append(line.strip())
        assert expected_line0 == lines[0]
        assert expected_line1 == lines[1]

    def test_negative_sentence_choices_all_work(self):
        # We're going to make sure that the other negative sentence selection methods don't crash
        # here; that's about it.
        # Note that the ordering of these sentences depends on a a particular shuffling of the
        # data (and thus the random seed set above), and could change if you change the number of
        # shuffles done in the code.
        context0 = "###".join(self.sentences[i] for i in [3, 4, 0, 13, 5, 9]).replace("\\\"", "\"")
        index0 = "4"
        expected_line0 = self.question0 + "\t" + context0 + "\t" + index0

        context1 = "###".join(self.sentences[i] for i in [4, 1, 9, 2, 7, 12]).replace("\\\"", "\"")
        index1 = "3"
        expected_line1 = self.question1 + "\t" + context1 + "\t" + index1

        reader = SquadSentenceSelectionReader(negative_sentence_selection="random-2,pad-to-5")
        output_filepath = reader.read_file(join(self.TEST_DIR, "squad_data.json"))
        with open(output_filepath, "r") as generated_file:
            lines = []
            for line in generated_file:
                lines.append(line.strip())
        assert expected_line0 == lines[0]
        assert expected_line1 == lines[1]

    def test_negative_question_choice_works(self):
        # We're going to make sure that the other negative sentence selection methods don't crash
        # here; that's about it.
        context0 = "###".join([self.question0, self.sentences[5]]).replace("\\\"", "\"")
        index0 = "1"
        expected_line0 = self.question0 + "\t" + context0 + "\t" + index0

        context1 = "###".join([self.sentences[2], self.question1]).replace("\\\"", "\"")
        index1 = "0"
        expected_line1 = self.question1 + "\t" + context1 + "\t" + index1

        reader = SquadSentenceSelectionReader(negative_sentence_selection="question")
        output_filepath = reader.read_file(join(self.TEST_DIR, "squad_data.json"))
        with open(output_filepath, "r") as generated_file:
            lines = []
            for line in generated_file:
                lines.append(line.strip())
        assert expected_line0 == lines[0]
        assert expected_line1 == lines[1]

    def test_negative_random_question_choice_works(self):
        # We're going to make sure that the other negative sentence selection methods don't crash
        # here; that's about it.
        context0 = "###".join([self.question0, self.question1, self.sentences[5]]).replace("\\\"", "\"")
        index0 = "2"
        expected_line0 = self.question0 + "\t" + context0 + "\t" + index0

        context1 = "###".join([self.question1, self.question0, self.sentences[2]]).replace("\\\"", "\"")
        index1 = "2"
        expected_line1 = self.question1 + "\t" + context1 + "\t" + index1

        reader = SquadSentenceSelectionReader(negative_sentence_selection="questions-random-2")
        output_filepath = reader.read_file(join(self.TEST_DIR, "squad_data.json"))
        with open(output_filepath, "r") as generated_file:
            lines = []
            for line in generated_file:
                lines.append(line.strip())
        assert expected_line0 == lines[0]
        assert expected_line1 == lines[1]
