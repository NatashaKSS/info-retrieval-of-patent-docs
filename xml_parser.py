#!/usr/bin/python
# Import standard modules
import re
import sys

# Standard API for XML Parsing
import xml.etree.ElementTree as elemTree

#======================================================================#
# Program Description:
# An XML query representation.
# Parses an XML query and contains methods to retrieve attributes from that 
# XML query.
#======================================================================#

class Query:
    """
    Initializes a Query object by parsing the XML query found in query_file_dir. 
    Every Query object has a attribute-text mapping, e.g. {"title" : "Some title"}
    
    query_file_name    File name of the query, with or without trailing ".xml". Upon
                       initialization, ".xml" will be removed if contained in file name
    query_file_dir     String representation of the query file's directory on disk
    """
    def __init__(self, query_file_dir):
        # File directory containing document
        self.query_file_dir = query_file_dir
        # Title attribute of a Query
        self.title = None
        # Description attribute of a Query
        self.description = None
        self.parse_query()
    
    """
    Parses the query specified in self.query_file_dir and parses a query's "title" 
    and "description" tag.
    If the XML tag does not have any text/contents, its attribute will have a value of None
    """
    def parse_query(self):
        XML_query = elemTree.parse(self.query_file_dir)
        root = XML_query.getroot() # A tree of "<query>" and all its subdirectories
        title = root.find("title").text
        description = root.find("description").text
        
        if title is not None:
            self.title = title.strip()
        else:
            self.title = None
        
        if description is not None:
            list_of_stripped_lines = [line.strip() for line in description.splitlines()]
            self.description = " ".join(list_of_stripped_lines).strip()
        else:
            self.description = None
        
    def get_title(self):
        return self.title
        
    def get_description(self):
        return self.description
        
#======================================================================#
# Class Description:
# An XML document representation. 
# Parses an XML document specified and contains methods to retrieve attributes 
# from that XML document.
#======================================================================#

class Document:
    """
    Initializes a Document object by parsing the XML document found in doc_file_dir. 
    Every Document object has a attribute-text mapping, e.g. {"Title" : "Some title"}
    
    doc_file_name    File name of the document, with or without trailing ".xml". Upon
                     initialization, ".xml" will be removed if contained in file name
    doc_file_dir     String representation of the doc file's directory on disk
    """
    def __init__(self, doc_file_name , doc_file_dir):
        # File name of document without trailing ".xml"
        if doc_file_name.endswith(".xml"):
            self.doc_file_name = doc_file_name[:-4]; # Remove ".xml" in file name
        else:
            self.doc_file_name = doc_file_name
        # File directory containing document
        self.doc_file_dir = doc_file_dir
        # Attribute-text mapping
        self.attrib_text_map = {}
        self.parse_doc()
    
    """
    Parses the document specified in self.doc_file_dir and creates a self.attrib_text_map 
    Python dictionary representation of the XML doc, e.g. {"Title" : "Some title", ...}.
    If the XML tag does not have any text/contents, its attribute will have a value of None
    """
    def parse_doc(self):
        XML_doc = elemTree.parse(self.doc_file_dir)
        root = XML_doc.getroot() # A tree of "<doc>" and all its subdirectories
        XML_doc_str_tags = root.findall("str") # List of all "<str>" XML objects
        
        for str_tag in XML_doc_str_tags:
            str_tag_attrib = str_tag.attrib['name']
            
            if str_tag_attrib not in self.attrib_text_map.keys():
                self.attrib_text_map[str_tag_attrib] = None
            
            str_tag_text = str_tag.text
            if str_tag_text is not None:
                self.attrib_text_map[str_tag_attrib] = str_tag_text.strip()
                
    def get_title(self):
        title_tag = "Title"
        return self.get_tag_text(title_tag)
        
    def get_abstract(self):
        abstract_tag = "Abstract"
        return self.get_tag_text(abstract_tag)
    
    def get_IPC_subclass(self):
        ipc_subclass_tag = "IPC Subclass"
        return self.get_tag_text(ipc_subclass_tag)
        
    """
    Gets the text contents within a pair of XML attribute tags if the attribute
    exists, else, None is returned
    
    attrib_name    String representation of the XML tag attribute
    """
    def get_tag_text(self, attrib_name):
        if attrib_name in self.attrib_text_map.keys():
            return self.attrib_text_map[attrib_name]
        else:
            return None
    
    """
    Print a doc's tags, attributes and text within those set of tags
    Leaves an empty line if no text is found within those tags
    """
    def print_xml_format(self):
        print self.attrib_text_map

