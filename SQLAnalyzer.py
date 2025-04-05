from antlr4 import *
import json
from SQLExtractor import SQLListener
from output.PlSqlLexer import PlSqlLexer
from output.PlSqlParser import PlSqlParser
from output.PlSqlParserListener import PlSqlParserListener
from DrawTree import DrawTree

class SQLAnalyzer(PlSqlParserListener):  
    def __init__(self):
        self.results = []
        self.parse_tree_json = []
        self.listener = SQLListener()

    def analyze(self, sql):
        self.parse_tree_json = DrawTree.generate_parse_tree_json(sql)
        # print(self.parse_tree_json)
        lexer = PlSqlLexer(InputStream(sql))
        stream = CommonTokenStream(lexer)
        parser = PlSqlParser(stream)
        tree = parser.sql_script()

        walker = ParseTreeWalker()
        walker.walk(self.listener, tree)

        self.results = self.listener.results
        # print(self.results)

        return {"results": self.results, "parse_tree": self.parse_tree_json}

    