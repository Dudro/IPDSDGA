import auxiliaryGenetics as ag
import random
import math

from params import params

class Gene():
    def __init__(self, gene_a=None, gene_b=None):
        """
        :type gene_a: Gene Parent A's Gene
        :type gene_b: Gene Parent B's Gene
        """

        """ list(char): The genetic sequence """
        self._code = list()
        """ int: the depth of the genetic sequence tree, or log2(len(_code)) """
        self._size_mem = params['default_memory_size']

        # produce a new genetic code if this Gene does not have 2 parents
        # If it has parents, produce the code through recombination
        if gene_a is None or gene_b is None:
            self._code = ag.ProduceRandomGene(self._size_mem)
            ag.mutate(self._code)
            self.update_mem_size()
        else:
            self._code = ag.recombinate(gene_a, gene_b)
            ag.mutate(self._code)
            self.update_mem_size()

    def get_seq(self):
        return self._code

    def get_decision(self, history):
        """
        Find the choice of this Gene's Cell depending on the
        history provided.  If the move is a 'c', get the left
        child.  If it a 'd', get the right child.  If we reach
        a leaf node, return that value
        :param history: Memory The history or moves provided
        :return: the choice dictated by the gene and history provided
        """
        offset = 1
        for x in history.get_mem_seq():
            # If c, get left child
            if 'c' == x:
                if not ag.isValidPosition(self._code, 2*offset):
                    return self.get_choice_at(offset)
                else:
                    offset = 2*offset
            # else its 'd', so get right child
            else:
                if not ag.isValidPosition(self._code, 2*offset+1):
                    return self.get_choice_at(offset)
                else:
                    offset = (2*offset)+1
        return self.get_choice_at(offset)

    def get_choice_at(self, x):
        """
        Retrieve the character at offset 'x' from this Gene's code
        :param x: (int) the offset
        :return: the character at offset 'x' in the gene
        """
        return self._code[x]

    def update_mem_size(self):
        """
        Update the size of the Gene's memory to the floor
        of the base 2 log of the length of this Gene's code
        """
        self._size_mem = int(math.log(len(self._code), 2))

    def get_defect_fraction(self):
        """
        :return: The percentage of this Gene which is 'd'
        """
        count_defect = 0
        for x in range(1, len(self._code)):
            if 'd' == self.get_choice_at(x):
                count_defect += 1
        return float(count_defect) / float(len(self._code)-1)

    def get_mem_size(self):
        """
        Retrieve and return the size of this Gene's memory
        :return: int This Gene's memory size
        """
        return self._size_mem

    def __str__(self):
        """
        Prints a string representation of all
        important information of the Gene
        :return:
        """
        display = "\nmemory size: "
        display += str(self._size_mem)
        display += "\npercent defect: "
        display += str(self.get_defect_fraction())
        display += "\ninitial move: "
        display += self.get_choice_at(1)
        display += "\ngene: "
        for x in self._code:
            display += str(x)

        return display
