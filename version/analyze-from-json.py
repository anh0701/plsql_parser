tree_file = "static/tree.json"

import json

def extract_info(node, table_names=None, selected_columns=None, where_conditions=None, group_by_columns=None, join_conditions=None):
    if table_names is None:
        table_names = []
    if selected_columns is None:
        selected_columns = []
    if where_conditions is None:
        where_conditions = []
    if group_by_columns is None:
        group_by_columns = []
    if join_conditions is None:
        join_conditions = []
    
    if isinstance(node, dict):
        # Kiểm tra tên bảng (tableview_name) 
        if node.get("name") == "tableview_name":
            identifier = find_deepest_child(node, "regular_id")
            if identifier:
                table_names.append(identifier)
        
        #  SELECT
        if node.get("name") == "selected_list":
            columns = find_all_deepest_children(node, "regular_id")
            selected_columns.extend(columns if columns else ['*'])
        
        #  WHERE
        if node.get("name") == "where_clause":
            condition = find_deepest_child(node, "condition")
            if condition:
                where_conditions.append(condition)
        
        #  GROUP BY
        if node.get("name") == "group_by_clause":
            columns = find_all_deepest_children(node, "regular_id")
            group_by_columns.extend(columns)
        
        #  JOIN
        if node.get("name") == "join_clause":
            join_table = find_deepest_child(node, "tableview_name")
            join_column = find_all_deepest_children(node, "regular_id")
            if join_table and join_column:
                join_conditions.append((join_table, join_column))
        
        # Đệ quy duyệt qua các node con
        for child in node.get("children", []):
            extract_info(child, table_names, selected_columns, where_conditions, group_by_columns, join_conditions)
    
    return table_names, selected_columns, where_conditions, group_by_columns, join_conditions

def find_deepest_child(node, target_name):
    if "children" in node:
        for child in node["children"]:
            result = find_deepest_child(child, target_name)
            if result:
                return result
    if node["name"] == target_name:
        return node["children"][0]["name"] if "children" in node and node["children"] else None
    return None

def find_all_deepest_children(node, target_name):
    result = []
    if "children" in node:
        for child in node["children"]:
            result.extend(find_all_deepest_children(child, target_name))
    if node["name"] == target_name:
        result.append(node["children"][0]["name"] if "children" in node and node["children"] else None)
    return result

# Đọc JSON từ file
with open(tree_file, "r", encoding="utf-8") as file:
    json_data = json.load(file)

tables, columns, conditions, group_by, joins = extract_info(json_data)

# In kết quả
print("Tên bảng:", tables)
print("Danh sách cột trong SELECT:", columns)
print("Điều kiện WHERE:", conditions)
print("Cột trong GROUP BY:", group_by)
print("Quan hệ JOIN:", joins)
