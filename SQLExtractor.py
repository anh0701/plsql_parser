#  chỉnh sửa in ra

from antlr4 import *
from output.PlSqlLexer import PlSqlLexer
from output.PlSqlParser import PlSqlParser
import json
import re  
from DrawTree import DrawTree

def extract_select_info(tree):
    select_info = {
        "select_fields": [],
        "from_tables": [],
        "joins": [],
        "where_conditions": [],
        "group_by_fields": [],
        "order_by_fields": []
    }

    table_alias_map = {}  

    def traverse_tree(node):
        if not hasattr(node, "getRuleIndex"):
            return

        rule_index = node.getRuleIndex()

        # SELECT fields
        if rule_index == PlSqlParser.RULE_selected_list:
            for child in node.children:
                text = child.getText().strip()
                if text and text != ",":
                    text = re.sub(r"AS\s*", " AS ", text)
                    select_info["select_fields"].append(text)

        # FROM tables (Lưu alias -> tên bảng)
        elif rule_index == PlSqlParser.RULE_from_clause:
            def extract_table_info(from_node, last_table=None):
                table_name = last_table
                alias = None

                for child in from_node.children:
                    if hasattr(child, "getRuleIndex"):
                        child_rule = child.getRuleIndex()

                        if child_rule == PlSqlParser.RULE_tableview_name:
                            table_name = child.getText().strip()
                            if table_name not in select_info["from_tables"]:
                                select_info["from_tables"].append(table_name)
                            if table_name not in table_alias_map:
                                table_alias_map[table_name] = None

                        elif child_rule == PlSqlParser.RULE_table_alias:
                            alias = child.getText().strip()
                            if alias:
                                if table_name:
                                    if table_name in table_alias_map and table_alias_map[table_name] is None:
                                        table_alias_map[table_name] = alias
                                else:
                                    for key in table_alias_map:
                                        if table_alias_map[key] is None:
                                            table_alias_map[key] = alias
                                            break

                        elif child_rule in {
                            PlSqlParser.RULE_table_ref_list,
                            PlSqlParser.RULE_table_ref,
                            PlSqlParser.RULE_table_ref_aux,
                            PlSqlParser.RULE_table_ref_aux_internal,
                            PlSqlParser.RULE_dml_table_expression_clause
                        }:
                            extract_table_info(child, table_name)

            extract_table_info(node)

        # JOIN
        elif rule_index == PlSqlParser.RULE_join_clause:
            join_data = {
                "table_from": select_info["from_tables"][0] if select_info["from_tables"] else None,
                "table_to": None,
                "join_type": "INNER",
                "join_condition": None
            }

            def extract_join_table(join_node):
                """ Duyệt sâu để lấy đúng bảng JOIN """
                for child in join_node.children:
                    if hasattr(child, "getRuleIndex"):
                        child_rule = child.getRuleIndex()

                        if child_rule == PlSqlParser.RULE_tableview_name:
                            table_name = child.getText().strip()
                            if join_data["table_to"] is None:
                                join_data["table_to"] = table_name

                        elif child_rule in {
                            PlSqlParser.RULE_table_ref_aux,
                            PlSqlParser.RULE_table_ref_aux_internal,
                            PlSqlParser.RULE_dml_table_expression_clause
                        }:
                            extract_join_table(child)

            extract_join_table(node)

            for child in node.children:
                if hasattr(child, "getRuleIndex"):
                    child_rule = child.getRuleIndex()

                    if child_rule == PlSqlParser.RULE_outer_join_type:
                        join_data["join_type"] = child.getText().upper()

                    elif child_rule == PlSqlParser.RULE_join_on_part:
                        join_condition = child.getText().replace("ON", "").strip()
                        join_condition = re.sub(r"(\w+)(=|>|<|!=)(\w+)", r"\1 \2 \3", join_condition)
                        join_data["join_condition"] = join_condition

            select_info["joins"].append(join_data)


        # WHERE conditions (Xử lý JOIN với dấu (+))
        elif rule_index == PlSqlParser.RULE_where_clause:
            where_text = " ".join([child.getText().strip() for child in node.children])

            match = re.search(r"(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)\(\+\)", where_text)
            if match:
                left_alias, left_col, right_alias, right_col = match.groups()

                table_from = next((k for k, v in table_alias_map.items() if v == left_alias), left_alias)
                table_to = next((k for k, v in table_alias_map.items() if v == right_alias), right_alias)

                join_condition = where_text.replace("WHERE", "").replace("(+)", "").strip()
                join_condition = re.sub(r"(\w+)(=|>|<|!=)(\w+)", r"\1 \2 \3", join_condition)
                join_condition = re.sub(r"AND", " AND ", join_condition)
                print(join_condition)

                join_data = {
                    "table_from": table_from,
                    "table_to": table_to,
                    "join_type": "LEFT OUTER",
                    "join_condition": join_condition
                }
                select_info["joins"].append(join_data)
            else:
                join_condition = where_text.replace("WHERE", "").strip()
                join_condition = re.sub(r"(\w+)(>=|<=|>|<|!=|LIKE|=)(\S+)", r"\1 \2 \3", join_condition)
                join_condition = re.sub(r"(\w+)(NOTIN)(\()", r"\1 NOT IN \3", join_condition)
                join_condition = re.sub(r"(\w+)(IN)(\()", r"\1 IN \3", join_condition)
                join_condition = re.sub(r"AND", " AND ", join_condition)
                select_info["where_conditions"].append(join_condition)

        # GROUP BY
        elif rule_index == PlSqlParser.RULE_group_by_clause:
            group_by_text = " ".join([child.getText().strip() for child in node.children]).replace("GROUP BY", "").strip()
            select_info["group_by_fields"].append(group_by_text)

        # ORDER BY
        elif rule_index == PlSqlParser.RULE_order_by_clause:
            order_by_text = " ".join([child.getText().strip() for child in node.children]).replace("ORDER BY", "").strip()
            select_info["order_by_fields"].append(order_by_text)

        # Duyệt tiếp các node con
        if hasattr(node, "children"):
            for child in node.children:
                traverse_tree(child)

    traverse_tree(tree)

    return select_info

# Hàm phân tích cú pháp PL/SQL
def parse_plsql(input_text):
    input_stream = InputStream(input_text)
    lexer = PlSqlLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = PlSqlParser(token_stream)
    tree = parser.select_statement()
    return tree

plsql_query = """
SELECT 
    emp.employee_id,
    emp.first_name,
    emp.last_name,
    emp.salary,
    dept.department_name,
    dept_avg.avg_salary,
    (emp.salary - dept_avg.avg_salary) AS salary_diff
FROM 
    employees emp,
    (SELECT 
        department_id,
        department_name
    FROM 
        departments
    WHERE 
        department_name LIKE 'Sales%') dept,
    (SELECT 
        department_id,
        AVG(salary) AS avg_salary
    FROM 
        employees
    GROUP BY 
        department_id) dept_avg
WHERE 
    emp.department_id = dept.department_id(+)
    AND emp.department_id = dept_avg.department_id(+)
    AND emp.salary > dept_avg.avg_salary(+);
"""

tree = parse_plsql(plsql_query)
DrawTree.generate_parse_tree_json(plsql_query)
query_details = extract_select_info(tree)
print(json.dumps(query_details, indent=4, ensure_ascii=False))
