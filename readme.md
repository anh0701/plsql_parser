1. setup

- install package


```shell

    pip install -r requirements.txt

```

2. run project

```shell
    python app.py

```

3. sql query test

```sql

SELECT c.customer_name, o.order_id, p.product_name, od.quantity  
FROM customers c  
JOIN orders o ON c.customer_id = o.customer_id  
JOIN order_details od ON o.order_id = od.order_id  
JOIN products p ON od.product_id = p.product_id  
WHERE o.order_date >= '2024-01-01'  
GROUP BY c.customer_name, o.order_id, p.product_name, od.quantity  
ORDER BY c.customer_name;
```
```sql
SELECT emp.name, emp.salary, dept.dept_name 
FROM employees emp
JOIN departments dept ON emp.dept_id = dept.id
WHERE emp.salary > 5000
GROUP BY dept.dept_name
```

```sql
SELECT e.ename, d.dname  
FROM emp e, dept d  
WHERE e.deptno = d.deptno(+);

SELECT * FROM employees

```

```sql

SELECT employee_id, first_name, last_name, 
       (SELECT department_name 
        FROM departments 
        WHERE department_id = e.department_id) AS department_name
FROM employees e
WHERE salary > 50000;


```

```sql

SELECT employees.emp_id, employees.emp_name, dept.dept_name
FROM (
    SELECT emp_id, emp_name, dept_id 
    FROM employees 
    WHERE hire_date > TO_DATE('2020-01-01', 'YYYY-MM-DD')
) employees
JOIN departments dept ON employees.dept_id = dept.dept_id
WHERE dept.dept_name = 'Sales';
```

```sql

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
```

<!-- Thu gọn code trong vsc: Ctrl K 0 -->


- PURPOSE CODE  
- Source Data  
- Field Type  
- Field Alias  
- Table From  
- Table To  
- Field From  
- Field To  
- Field Formula  
- Destination View
