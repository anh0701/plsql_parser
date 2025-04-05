from antlr4 import CommonTokenStream, InputStream
from output.PlSqlLexer import PlSqlLexer
from output.PlSqlParser import PlSqlParser
import json

class DrawTree:
    def __init__(self):
        pass

    @staticmethod
    def parse_tree_to_dict(tree, parser):
       
        if tree.getChildCount() == 0:
            return {"name": tree.getText()} if tree.getText().strip() else None

        rule_name = parser.ruleNames[tree.getRuleIndex()] if hasattr(tree, "getRuleIndex") else "UNKNOWN"

        children = [DrawTree.parse_tree_to_dict(child, parser) for child in tree.getChildren()]
        children = list(filter(None, children))  
        return {
            "name": rule_name,
            "children": children if children else []  
        }

    @staticmethod
    def generate_parse_tree_json(sql, output_file="static/tree.json"):
        
        lexer = PlSqlLexer(InputStream(sql))
        stream = CommonTokenStream(lexer)
        parser = PlSqlParser(stream)
        tree = parser.sql_script()  

        tree_dict = DrawTree.parse_tree_to_dict(tree, parser)  
        # print("tree dict:  " + json.dumps(tree_dict, indent=4, ensure_ascii=False))
        if tree_dict:  
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(tree_dict, f, indent=4, ensure_ascii=False)
            print(f"✅ Parse tree JSON đã được tạo: {output_file}")

        return tree_dict
