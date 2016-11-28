from Cell import Cell
from Position import Position
import statistics as stats
import random

import params as p

neighbour_offsets = [Position(-1,-1), Position( 0,-1), Position( 1,-1),
                     Position(-1, 0), Position( 0, 0), Position( 1, 0),
                     Position(-1, 1), Position( 0, 1), Position( 1, 1)]

class Surface:
    def __init__(self, width, height):
        self.population = 0
        self.width = width
        self.height = height
        self._all_cells = set()
        self.map = [];
        self.ID = 0
        for i in range(height):
            self.map.append([ None ] * width)

    def get_all(self):
        living_cells = list()
        for y in range(self.height):
            for x in range(self.width):
                if self.get(Position(x, y)) is not None:
                    living_cells.append(self.get(Position(x, y)))
        return living_cells

    def get(self, pos):
        return self.map[(self.height + pos.y) % self.height][(self.width + pos.x) % self.width]

    def set(self, pos, c):
        if c is None:
            self._all_cells.remove(self.get(pos))
        else:
            self._all_cells.add(c)
        self.map[(self.height + pos.y) % self.height][(self.width + pos.x) % self.width] = c

    def __map(self, method):
        for column in self.map:
            for c in column:
                if c is not None:
                    method(c)

    def get_scores(self):
        scores = list()
        self.__map(lambda c: scores.append(c.get_score()))
        return scores

    def get_rule_stats(self):
        """
        Get statistics about the genetic makeup of 
        the Cell's on this surface 
        """
        num_tfts = 0
        for c in self.get_all():
            if c.is_tft():
                num_tfts += 1
        return num_tfts / self.population

    def get_length_stats(self):
        """
        Return statistics about the lengths of the Gene's 
        of the Cell's on this surface 
        """
        lengths = list()
        self.__map(lambda c: lengths.append(len(c.get_gene())-1))
        mean_length = stats.mean(lengths)

        return mean_length

    def get_score_stats(self):
        """
        Get the statistics for the scores of all cells
        :return: mean, mode, stddev
        """
        scores = self.get_scores()
        if 0 == len(scores):
            return 0, 0, 0
        mean_score = stats.mean(scores)
        med_score = stats.median(scores)
        stddev_score = stats.pstdev(scores, mean_score)

        return mean_score, med_score, stddev_score

    def get_avg_defection_stats(self):
        """
        Get the statistics for the fraction of defect choice in Cells' genes
        :return: mean, mode, stddev
        """
        fraction_defect = list()
        self.__map(lambda c: fraction_defect.append(c.get_gene().get_defect_fraction()))
        if 0 == len(fraction_defect):
            return 0, 0, 0
        mean_def_fraction = stats.mean(fraction_defect)
        med_def_fraction = stats.median(fraction_defect)
        stddev_def_fraction = stats.pstdev(fraction_defect, mean_def_fraction)

        return mean_def_fraction, med_def_fraction, stddev_def_fraction

    def get_init_move_stats(self):
        """
        Get the statistics for the initial move of the Cells
        :return: mean, mode, stddev
        """
        initial_moves = list()
        self.__map(lambda c: initial_moves.append(c.get_gene().get_choice_at(1)))
        if 0 == len(initial_moves):
            return 0

        initial_move_fraction = 0
        for move in initial_moves:
            if 'd' == move:
                initial_move_fraction += 1

        return initial_move_fraction/len(initial_moves)

    def get_neighbours(self, cell):
        neighbours = set()
        for offset in neighbour_offsets:
            neighbour = self.get(cell.get_position() + offset)
            if neighbour is not None:
                neighbours.add(neighbour)
        return neighbours
    
    def get_empty_neighbour_position(self, c):
        """
        Return the _position of a neighbouring empty cell
        :param c: A cell
        :return: A random open _position from among neighbouring
        open _position, or None if there are no open positions.
        """
        candidates = []
        for offset in neighbour_offsets:
            neighbour = self.get(c.get_position() + offset)
            if neighbour is None:
                candidates.append(c.get_position() + offset)
        if len(candidates) == 0:
            return None
        return random.choice(candidates)

    def __interaction_tick(self):
        self.__map(lambda c: c.interact(self.get_neighbours(c)))
    
    def __death_tick(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map[x][y] is not None:
                    if self.map[x][y].is_dead():
                        self.map[x][y] = None
                        self.population -= 1
    
    def __reproduction_tick(self):
        ratio = 0.1 # TODO: move to paramater
        top_cells = sorted(
                self._all_cells, key=lambda c: -c.get_score())[:round(len(self._all_cells) * ratio)]
        chosen_cells = set()

        for c in top_cells:
            if c not in chosen_cells:
                # find best neighbour
                open_position = self.get_empty_neighbour_position(c)
                if open_position is None:
                    continue
                neighbours = self.get_neighbours(c)
                if 0 == len(neighbours):
                    continue
                best_neighbour = max(neighbours, key=lambda c: -c.get_score())
                if best_neighbour not in chosen_cells:
                    chosen_cells.add(c)
                    chosen_cells.add(best_neighbour)
                    self.set(open_position, Cell(
                        self.ID,
                        open_position,
                        c,
                        best_neighbour
                    ))
                    self.ID += 1
                    self.population += 1

    def __move_cell(self, c, destination):
        """ 
        Move the Cell 'c' to the its destination.  Set its current
        position to none, set its new position to destination,
        and set the map slot at 'destination' to hold the cell 'c'.
        """
        destination.x = (destination.x + self.width) % self.width
        destination.y = (destination.y + self.height) % self.height
        self.set(c.get_position(), None)
        c.set_position(destination)
        self.set(destination, c)

    def __movement_tick(self):
        """
        This method could be expanded in functionality to encourage moving
        when performing poorly.  Right now it will just have a random chance
        to move.
        :return:
        """
        move_chance = 0.1 # TODO: move to parameter
        # shuffle so that priority is not given to cells at map[0][0]
        # This could be made to favour well performing cells
        live_cells = self.get_all()
        random.shuffle(live_cells)
        for c in live_cells:
            if random.random() > move_chance:
                continue
            # find neighbouring open spots
            open_position = self.get_empty_neighbour_position(c)
            # If there is a _position, move the cell c from
            # its current _position to its new _position
            if open_position is not None:
                self.__move_cell(c, open_position)

    def __alt_movement_tick(self):
        """
        This method accomplishes the same as the __movement_tick,
        only Cells are more likely to move if they are performing
        poorly.
        """
        ratio = 0.25
        move_chance = 0.2
        # get the bottom 'ratio' cells
        all_cells = self.get_all()
        sorted_cells = sorted(all_cells, key=lambda c: c.get_score())
        bottom_cells = sorted_cells[:round(len(all_cells) * ratio)]
        # check if poorly performing cell will move
        for c in bottom_cells:
            if random.random() > move_chance:
                continue
            open_position = self.get_empty_neighbour_position(c)
            # If there is a _position, move the cell c from
            # its current _position to its new _position
            if open_position is not None:
                self.__move_cell(c, open_position)

    def get_best_x(self, ratio):
        """
        Return the best 'ratio' percent of Cells
        """
        all_cells = self.get_all()
        sorted_cells = sorted(all_cells, key=lambda c: -c.get_score())
        return sorted_cells[:round(len(all_cells) * ratio)]

    def tick(self, interactions):
        self.__clean()
        for x in range(interactions):
            self.__interaction_tick()
            self.__death_tick()
            self.__alt_movement_tick()
        self.__reproduction_tick()
       
    def __clean(self):
        """
        Clear and reset the scores of all Cells alive
        :return:
        """
        self.__map(lambda c: c.clear_interactions())
        self.__map(lambda c: c.reset_score())

    def draw(self):
        pass

    def __str__(self):
        out = "*"
        for x in range(self.width):
            out += "-----"
        out += "*\n"
        for y in range(self.height):
            out += "|"
            for x in range(self.width):
                c = self.get(Position(x, y))
                if c is None:
                    out += "     "
                else:
                    out += '{:4}'.format(c.get_id()) + " "
            out += "|\n"
        out += "*"
        for x in range(self.width):
            out += "-----"
        out += "*\n"
        out += "avg. def.:" + "{0:.4}".format(
                float(self.get_avg_defection_stats()[0])) + "\n"
        out += "init. move 'd': " + "{0:.4}".format(
                float(self.get_init_move_stats())) + "\n"
        out += "score stats: " + "{0:.4}".format(
                float(self.get_score_stats()[0])) + "\n"
        out += "population: " + str(self.population)
        return out

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        p.init(sys.argv[1])
    else:
        p.init(None)

    surface_w = p.params['surface']['width']
    surface_h = p.params['surface']['height']
    gens = p.params['generations']
    interactions = p.params['interactions']

    surface = Surface(surface_w, surface_h)

    cells = []
    for i in range(surface_w * surface_h):
        cells.append(Cell(surface.ID, Position(i // surface_w, i % surface_h)))
        surface.ID += 1
        surface.population += 1
    for cell in cells:
        surface.set(cell.get_position(), cell)

    mean_scores = list()
    mean_def_fracs = list()
    mean_init_moves = list()

    for i in range(gens):
        print(surface)
        surface.tick(interactions)
        mean_scores.append(surface.get_score_stats()[0])
        mean_def_fracs.append(surface.get_avg_defection_stats()[0])
        mean_init_moves.append(surface.get_init_move_stats())

    for c in surface.get_best_x(0.05):
        print(str(c))
    
    scores = ""
    def_frac = ""
    init_moves = ""

    for s in mean_scores:
        scores += "{0:.4}".format(float(s)) + " - "

    for d in mean_def_fracs:
        def_frac += "{0:.4}".format(float(d)) + " - "

    for m in mean_init_moves:
        init_moves += "{0:.4}".format(float(m)) + " - "

    print("scores: ")
    print(str(mean_scores.pop(0)) + " : " + str(mean_scores.pop()))
    print("def fracs: ")
    print(str(mean_def_fracs.pop(0)) + " : " + str(mean_def_fracs.pop()))
    print("init moves: ")
    print(str(mean_init_moves.pop(0)) + " : " + str(mean_init_moves.pop()))
    print("rules: " + str(surface.get_rule_stats()))
