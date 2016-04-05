#======================================================================#
# Program Description:
# Test Driver for search.py
# Tests if the sorted list of docIDs produced in search.py is relevant.
# Computes how many of the docIDs produced are contained in +ve and -ve.
#======================================================================#

class TestDriver():
    # Specify file paths here
    pos_query_dir = "cs3245-hw4/q1-qrels+ve-modified.txt"
    neg_query_dir = "cs3245-hw4/q1-qrels-ve.txt"
    
    def __init__(self, list_results_docID):
        self.results_list = list_results_docID
        with open(self.pos_query_dir, "r") as from_pos_query_file:
            self.true_pos_results_list = from_pos_query_file.read().splitlines()
        
        with open(self.neg_query_dir, "r") as from_neg_query_file:
            self.true_neg_results_list = from_neg_query_file.read().splitlines()        
    
    """
    Prints the test heuristic for this search process.
    [GOOD] indicates that the higher the score, the better the search engine
    [BAD] indicates that the lower the score, the better the search engine
    """
    def process_results(self):
        self.print_pretty_header()
        print "+ve: ", self.true_pos_results_list
        print "-ve: ", self.true_neg_results_list, "\n"
        
        # TODO: Tell Prof that docID EP1918442A2 is duplicated in +ve list so I removed 1 copy for this test
        print "Processed results: "
        pos_score_list = [elem for elem in self.results_list if elem in self.true_pos_results_list]
        pos_never_retrieve_list = [elem for elem in self.true_pos_results_list if elem not in pos_score_list]
        print "[GOOD] DocIDs retrieved that were in +ve: ", pos_score_list
        print "[BAD] DocIDs supposed to be retrieved but didn't     : ", pos_never_retrieve_list
        print "Score: ", len(pos_score_list), " / ", len(self.true_pos_results_list), "\n"
        
        neg_score_list = [elem for elem in self.results_list if elem in self.true_neg_results_list]
        neg_never_retrieve_list = [elem for elem in self.true_neg_results_list if elem not in neg_score_list]
        print "[BAD] DocIDs retrieved that were in -ve ", neg_score_list
        print "[GOOD] DocIDs not supposed to be retrieved and didn't: ",  neg_never_retrieve_list
        print "Score: ", len(neg_score_list), " / ", len(self.true_neg_results_list)
        self.print_pretty_footer()
        
    def print_pretty_header(self):
        print "---------------PRINTING RESULTS-----------------"
        
    def print_pretty_footer(self):
        print "-----------------END RESULTS-------------------"

