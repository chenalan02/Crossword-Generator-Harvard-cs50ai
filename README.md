# Crossword-Generator
Generates a crossword puzzle given a text that represent a crossword structure and a text file with a domain of possible words. These files are located in the crossword/data folder.

To run the program, you can run a code like **python generate.py data/structure1.txt data/words1.txt** in command prompt. There are 3 preset text files for structure and words each.

## Logic
A crossword puzzle can be treated as a constraint satisfaction problem where each row or column where a word needs to fill up is seen as a variable/node with unary and binary constraints. The unary constraint is the length of each word and we just remove all the words in the domain of each variable/node to satisfy this constraint. The Binary constraint is that the words chosen for a pair(arc) of variables/nodes must have the same letter in the position that they intersect. If a word in the domain of node x has no possible words in the domain of node y in which the arc is consistent, that word must be removed from the domain of node x. 

Once all arcs are consistent, we may use a search algorithm until a solution is found(or not found). Im my program I used backtracking search, where I iteratively chose a word to assign to a variable. If this assignment was possible/consistent, I would recursively call backtracking search. If the assignment is not consistent, I would remove the assignment. The function would return a list of assignments if a complete solution was found. 

I also chose the variables/nodes in order of which had the smallest number of words left in their domain. I chose the first word assignment in order of which words would limit the least amount of words in the domains of neighboring variables. These would allow my algorithm to be slightly more efficient.

## Template
This was an assignment in which I built upon a template from the Harvard CS50 online course. It can be found at https://cs50.harvard.edu/ai/2020/projects/3/crossword/
