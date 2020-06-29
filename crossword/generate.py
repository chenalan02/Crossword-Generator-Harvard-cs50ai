import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for node in self.domains:
            #creates a list of words per node to remove since we cannot remove the elements in a set while it is iterating
            words_to_remove= []

            for word in self.domains[node]:
                if len(word) != node.length:
                    words_to_remove.append(word)

            for word in words_to_remove:
                self.domains[node].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision= False
        #creates a list of words in the domain of node x to remove since we cannot remove the elements in a set while it is iterating
        words_to_remove= []
        #function which returns data of where the two nodes intersect/overlap
        overlap= self.crossword.overlaps[x,y]

        if overlap is not None:
            for word_x in self.domains[x]:
                consistent= False

                for word_y in self.domains[y]:
                    #a word in the domain of x is consistent if there is any word in the domain of y that has the same letter in the intersect
                    if word_x[overlap[0]] == word_y[overlap[1]]:
                        consistent= True
                #if the word is not consistent it is added to a list to be removed later
                if consistent == False:
                    words_to_remove.append(word_x)
                    revision= True
            #inconsistent words are removed from the domain of x
            for word in words_to_remove:
                self.domains[x].remove(word)

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            #creates a queue of arcs to update
            arcs= []
            for node1 in self.domains:
                for node2 in self.domains:
                    if node1 != node2:
                        #for each pair of nodes that intersect, add them as a tuple pair to a list of arcs
                        if self.crossword.overlaps[node1,node2] != None:   
                            arcs.append((node1,node2))

        while arcs != []:
            x= arcs[0][0]
            y= arcs[0][1]

            if self.revise(x, y):
                #if the domain of node x is empty after revision, this problem has no solution
                if len(self.domains[x]) == 0:
                    return False
                #if the arc is updated successfully, node x may no longer be arc consistent in respect to other nodes that it may have been before
                #we must then add the arcs between the revised x and all of its neighbors(except y as we have just checked it) to the queue
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        arcs.append((neighbor, x))
                #remove arcs from queue after revision
                arcs.pop(0)
            else:
                arcs.pop(0)
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains):
            return True

        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for node1 in assignment:
            for node2 in assignment:

                if node1 != node2:
                    #returns False if any assignmed words are the same
                    if assignment[node1] == assignment[node2]:
                        return False

                    overlap= self.crossword.overlaps[node1,node2]
                    if overlap != None:
                        #checks if words assigned to node overlaps are the same letter
                        if assignment[node1][overlap[0]] != assignment[node2][overlap[1]]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #list to store pair data of words and their constraint score
        constraint_list= []
        #function to create list of all neighbors to node var
        neighbors= self.crossword.neighbors(var)

        for neighbor in neighbors:
            overlap= self.crossword.overlaps[var, neighbor]
           
            for word_var in self.domains[var]:
                constraint_score= 0

                for word_neighbor in self.domains[neighbor]:
                    #adds constraint score for each word in the domain of neighbor nodes that are not consistent if word_var is chosen
                    if word_var[overlap[0]] != word_neighbor[overlap[1]]:
                        constraint_score += 1
                #add the pair data to list of all words
                constraint_list.append([word_var, constraint_score])
        #sorts the list in terms of constraint score
        constraint_list.sort(key= lambda x:x[1])
        #creates a list of all words in the same order as constraint_list
        return_list= map(lambda x:x.pop(0), constraint_list)
        return_list= list(return_list)
        return return_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        var_list= []
        #add unassigned variabled to a list along with the number of words left in its domain
        for var in self.domains:
            if var not in assignment:
                var_list.append((var, len(self.domains[var])))
        #sort this list by the number of words left in its domain
        var_list.sort(key= lambda x:x[1])

        #list for variables that are tied for least words left in domain
        equal_vars= [list(var_list[0])]
        for i in range(len(var_list)):
            #adds variables with same number of words left in domain
            if var_list[0][1] == var_list[i][1] and var_list[i] != var_list[0]:
                equal_vars.append(list(var_list[i]))

        
        #change the encoded information for words left in domain to the number of neighbors the variable had (highest degree)
        for i in range(len(equal_vars)):
            equal_vars[i][1]= len(self.crossword.neighbors(equal_vars[i][0]))

        #sort the list by the highest degree
        equal_vars.sort(key= lambda x:x[1])
        
        #return var with highest degree
        return equal_vars[0][0]

 
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #if a solution has been found, returns the solution, this is used for recursive purposes
        if self.assignment_complete(assignment) and self.consistent(assignment):
            return assignment
        #select the most optimal variable/node
        var = self.select_unassigned_variable(assignment)
        #assigns a word left in the domain of var and assigns it to var
        for word in self.order_domain_values(var, assignment):
            assignment[var]= word\
            #if the assignment is consistent, recursively call backtrack
            if self.consistent(assignment):
                result= self.backtrack(assignment)
                if result != False:
                    return assignment
            #if the assignment is not consistent at any point, remove the latest assignment
            assignment.pop(var)

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    print(sys.argv)

    #Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        print("++++++++++++")
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
