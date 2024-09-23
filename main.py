import re

def anonymize_sql_query(query):
    # Anonymize table names
    table_counter = 1
    table_mapping = {}
    def replace_table(match):
        nonlocal table_counter
        table_name = match.group(1)
        if table_name not in table_mapping:
            table_mapping[table_name] = f'table_{table_counter}'
            table_counter += 1
        return f'{match.group(0)[:match.start(1) - match.start()]}{table_mapping[table_name]}'
    
    query = re.sub(r'\bFROM\s+(\w+)', replace_table, query, flags=re.IGNORECASE)
    query = re.sub(r'\bJOIN\s+(\w+)', replace_table, query, flags=re.IGNORECASE)
    
    # Anonymize column names
    column_counter = 1
    column_mapping = {}
    alias_mapping = {}
    def replace_column(match):
        nonlocal column_counter
        column_name = match.group(1)
        if column_name not in column_mapping:
            column_mapping[column_name] = f'column_{column_counter}'
            column_counter += 1
        return f'{match.group(0)[:match.start(1) - match.start()]}{column_mapping[column_name]}'
    
    def replace_column_with_alias(match):
        column_name = match.group(1)
        alias_name = match.group(2)
        if column_name not in column_mapping:
            column_mapping[column_name] = f'column_{column_counter}'
            column_counter += 1
        alias_mapping[alias_name] = column_mapping[column_name]
        return f'{column_mapping[column_name]} AS {alias_name}'
    
    query = re.sub(r'\bSELECT\s+([\w\.]+)\s+AS\s+(\w+)', replace_column_with_alias, query, flags=re.IGNORECASE)
    query = re.sub(r'\bSELECT\s+([\w\.]+)', replace_column, query, flags=re.IGNORECASE)
    query = re.sub(r'\b,\s*([\w\.]+)', lambda m: f', {replace_column(m)}', query)
    query = re.sub(r'\b([\w\.]+)\s+AS\s+(\w+)', replace_column_with_alias, query, flags=re.IGNORECASE)
    
    # Anonymize WHERE clause
    query = re.sub(r'\bWHERE\s+([\w\.]+)', lambda m: f'WHERE {replace_column(m)}', query, flags=re.IGNORECASE)
    
    # Anonymize GROUP BY clause
    query = re.sub(r'\bGROUP\s+BY\s+([\w\.]+)', lambda m: f'GROUP BY {replace_column(m)}', query, flags=re.IGNORECASE)
    
    # Anonymize ORDER BY clause
    query = re.sub(r'\bORDER\s+BY\s+([\w\.]+)', lambda m: f'ORDER BY {replace_column(m)}', query, flags=re.IGNORECASE)
    
    return query

if __name__ == "__main__":
    sample_query = "SELECT name, age FROM users WHERE age > 30 ORDER BY name"
    anonymized_query = anonymize_sql_query(sample_query)
    print("Original Query:", sample_query)
    print("Anonymized Query:", anonymized_query)
    sample_queries = [
        "SELECT name, age FROM users WHERE age > 30 ORDER BY name",
        "SELECT u.name, u.email, o.order_id FROM users u JOIN orders o ON u.user_id = o.user_id WHERE o.amount > 100 GROUP BY u.name ORDER BY o.order_date",
        "SELECT p.product_name, c.category_name FROM products p JOIN categories c ON p.category_id = c.category_id WHERE c.category_name = 'Electronics' ORDER BY p.product_name",
        "SELECT e.first_name, e.last_name, d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id WHERE e.salary > 50000 GROUP BY d.department_name ORDER BY e.last_name",
        "SELECT s.student_name, c.course_name, sc.grade FROM students s JOIN student_courses sc ON s.student_id = sc.student_id JOIN courses c ON sc.course_id = c.course_id WHERE sc.grade >= 'B' ORDER BY s.student_name"
    ]

    for query in sample_queries:
        anonymized_query = anonymize_sql_query(query)
        print("Original Query:", query)
        print("Anonymized Query:", anonymized_query)
        print()