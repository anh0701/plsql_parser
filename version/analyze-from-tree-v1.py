from output.PlSqlParserListener import PlSqlParserListener
from output.PlSqlParser import PlSqlParser
import re

class SQLListener(PlSqlParserListener):
    def __init__(self):
        self.tables = set()
        print("DEBUG - SQLListener Initialized")
        self.columns = set()
        self.conditions = set()
        self.group_by = set()
        self.joins = set()
        self.order_by = set()
        self.results = []
        self.select_ctx = None
        self.join_type = set()

    def enterDml_table_expression_clause(self, ctx: PlSqlParser.Dml_table_expression_clauseContext):
        table_name = ctx.getChild(0).getText()  
        self.tables.add(table_name)

    def enterSelect_list_elements(self, ctx: PlSqlParser.select_list_elements):
        
        for child in ctx.children:
            column_name = child.getText()
    
            if column_name.upper() not in ["AS", ","]:  
                self.columns.add(column_name)

    def enterSelected_list(self, ctx: PlSqlParser.Selected_listContext):
        if "*" in ctx.getText():
            self.columns.add("*")
        # print(f"Select list: {ctx.getText()}")

    # def enterEveryRule(self, ctx):
    #     print(f"Entering rule: {type(ctx).__name__}, Text: {ctx.getText()}")
    

    def enterWhere_clause(self, ctx: PlSqlParser.Where_clauseContext):
        where_text = " ".join([child.getText() for child in ctx.children if child.getText().upper() != "WHERE"])
        conditions = [cond.strip() for cond in where_text.split("AND")]
        remaining_conditions = []

        for condition in conditions:
            left, operator, right = condition.partition("=")  # Tách điều kiện thành 2 phần

            if "(+)" in right:
                join_type = "LEFT OUTER JOIN"
                right = right.replace("(+)", "").strip()
                table_from, field_from = left.strip().split(".", 1)
                table_to, field_to = right.strip().split(".", 1)
                join_columns = {(f"{table_from}.{field_from}", f"{table_to}.{field_to}") }
                self.joins.update(join_columns)
                self.join_type.add(join_type)
                continue
            elif "(+)" in left:
                join_type = "RIGHT OUTER JOIN"
                left = left.replace("(+)", "").strip()
                table_from, field_from = right.strip().split(".", 1)
                table_to, field_to = left.strip().split(".", 1)
                join_columns = {(f"{table_from}.{field_from}", f"{table_to}.{field_to}") }
                self.joins.update(join_columns)
                self.join_type.add(join_type)
                continue
            else:
                join_type = "INNER JOIN"

            # print(f"Detected {join_type}: {left.strip()} {operator} {right.strip()}")

            if "(+)" not in left and "(+)" not in right:
                remaining_conditions.append(condition.strip())
        
        if remaining_conditions:
            self.conditions.add(" AND ".join(remaining_conditions))

        if self.conditions:
            self.enterWhprocessWhereCondition()

        if self.join_type:
            self.enterJoin_clause(ctx)

    def enterGroup_by_elements(self, ctx: PlSqlParser.Group_by_elementsContext):
        group_col = ctx.getText()
        self.group_by.add(group_col)

    def enterJoin_on_part(self, ctx: PlSqlParser.Join_on_partContext):

        full_text = ctx.getText().strip().upper()
        join_type = 'INNER JOIN'
        if 'INNER JOIN' in full_text:
            join_type = 'INNER JOIN'
        elif 'LEFT JOIN' in full_text:
            join_type = 'LEFT JOIN'
        elif 'RIGHT JOIN' in full_text:
            join_type = 'RIGHT JOIN'
        elif 'FULL JOIN' in full_text:
            join_type = 'FULL JOIN'
        elif 'JOIN' in full_text:
            join_type = 'INNER JOIN'

        print(f"Detected JOIN type: {join_type}")

        join_condition = full_text.replace("ON", "").strip()
        column_pairs = re.findall(r"(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", join_condition)
        join_columns = {(f"{t1}.{c1}", f"{t2}.{c2}") for t1, c1, t2, c2 in column_pairs}
        self.joins.update(join_columns)

        if join_type:
            self.join_type.add(join_type) 


    def enterOrder_by_elements(self, ctx: PlSqlParser.Order_by_elementsContext):
        order_col = ctx.getText()
        self.order_by.add(order_col)

        # push data to table

    def enterSelect_statement(self, ctx):  
        self.select_ctx = ctx        


    def enterJoin_clause(self, ctx):  
        for join_pair in self.joins:
            left_column, right_column = join_pair

            for join_type in self.join_type:
                join_entry  = {
                    "PURPOSE CODE": "Campaign_2",
                    "Source Data": "",
                    "Field Type": join_type,
                    "Table From": list(self.tables)[0] if self.tables else "",
                    "Table To": list(self.tables)[1] if len(self.tables) > 1 else "",
                    "Field From": left_column,
                    "Field To": right_column,
                    "Field Formula": "",
                    "Field Alias": "",
                    "Destination View": "",
                }

                if join_entry not in self.results:
                    self.results.append(join_entry)

    def enterWhprocessWhereCondition(self):
        print(f"DEBUG - Final WHERE conditions: {self.conditions}")

        field_formula = "AND ".join(self.conditions)
    
        self.results.append({
            "PURPOSE CODE": "Campaign_3",
            "Source Data": "",
            "Field Type": "WHERE",
            "Table From": list(self.tables)[0] if self.tables else "",
            "Table To": list(self.tables)[1] if len(self.tables) > 1 else "",
            "Field From": "",
            "Field To": "",
            "Field Formula":  field_formula,
            "Field Alias": "",
            "Destination View": "",
        })

    def exitSelect_statement(self, ctx):  

        field_formula = ", ".join(self.columns)

        self.results.append({
            "PURPOSE CODE": "Campaign_1",
            "Source Data": "",
            "Field Type": "SUM",
            "Table From": list(self.tables)[0] if self.tables else "",
            "Table To": list(self.tables)[1] if len(self.tables) > 1 else "",
            "Field Formula": field_formula,
            "Field Alias": "",
            "Field From": "",
            "Field To": "",
            "Destination View": "",
        })

        field_formula_group_by = ", ".join(self.group_by) if self.group_by else ""
        field_formula_order_by = ", ".join(self.order_by) if self.order_by else ""

        if self.group_by:
            self.results.append({
                "PURPOSE CODE": "Campaign_4",
                "Source Data": "",
                "Field Type": "GROUP BY",
                "Table From": list(self.tables)[0] if self.tables else "",
                "Table To": list(self.tables)[1] if len(self.tables) > 1 else "",
                "Field From": "",
                "Field To": "",
                "Field Formula": field_formula_group_by,
                "Field Alias": "",
                "Destination View": "",
            })

        if self.order_by:
            self.results.append({
                "PURPOSE CODE": "Campaign_5",
                "Source Data": "",
                "Field Type": "ORDER BY",
                "Table From": list(self.tables)[0] if self.tables else "",
                "Table To": list(self.tables)[1] if len(self.tables) > 1 else "",
                "Field From": "",
                "Field To": "",
                "Field Formula": field_formula_order_by,
                "Field Alias": "",
                "Destination View": "",
            })
    