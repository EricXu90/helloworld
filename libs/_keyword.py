from xml.dom.minidom import parse
import xml.dom.minidom
import new

class search_Keywords( ):
    
    def keyword_number_in_file(self,keyword_file,keyword_search):
        DOMTree = xml.dom.minidom.parse(keyword_file)
        collection = DOMTree.documentElement
        keywords = collection.getElementsByTagName("keyword")
        keyword_number=0
        for keyword in keywords:
            for node in keyword.childNodes:
                if keyword_search in node.data :
                    keyword_number += 1

        return keyword_number
    
 
 
 
