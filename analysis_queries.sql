-- E-commerce Customer Analytics (SQLite/PostgreSQL-style SQL)
-- Adjust date functions if using a different SQL engine.
-- Assumes raw CSVs have been imported into tables with matching names.

-- 1. Order volume by month
SELECT
    strftime('%Y-%m', order_purchase_timestamp) AS purchase_month,
    COUNT(DISTINCT order_id) AS order_count
FROM olist_orders_dataset
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY strftime('%Y-%m', order_purchase_timestamp)
ORDER BY purchase_month;

-- 2. Sales by product category (item price only; excludes freight)
SELECT
    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
    ROUND(SUM(i.price), 2) AS item_sales,
    COUNT(*) AS items_sold
FROM olist_order_items_dataset AS i
JOIN olist_products_dataset AS p
    ON i.product_id = p.product_id
LEFT JOIN product_category_name_translation AS t
    ON p.product_category_name = t.product_category_name
GROUP BY COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown')
ORDER BY item_sales DESC;

-- 3. Repeat customers (use customer_unique_id rather than customer_id)
WITH customer_order_counts AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM olist_orders_dataset AS o
    JOIN olist_customers_dataset AS c
        ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    COUNT(*) AS unique_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    1.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*) AS repeat_customer_rate
FROM customer_order_counts;

-- 4. Average delivery time and late delivery rate
SELECT
    AVG(
        (julianday(order_delivered_customer_date) -
         julianday(order_purchase_timestamp))
    ) AS average_delivery_days,
    AVG(
        CASE
            WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1.0
            WHEN order_delivered_customer_date IS NOT NULL
                 AND order_estimated_delivery_date IS NOT NULL THEN 0.0
            ELSE NULL
        END
    ) AS late_delivery_rate
FROM olist_orders_dataset
WHERE order_status = 'delivered';

-- 5. Average review score by delivery timeliness
WITH delivery AS (
    SELECT
        order_id,
        CASE
            WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 'Late'
            WHEN order_delivered_customer_date IS NOT NULL
                 AND order_estimated_delivery_date IS NOT NULL THEN 'On time or early'
            ELSE 'Unknown'
        END AS delivery_group
    FROM olist_orders_dataset
),
review_per_order AS (
    SELECT order_id, AVG(review_score) AS average_review_score
    FROM olist_order_reviews_dataset
    GROUP BY order_id
)
SELECT
    d.delivery_group,
    COUNT(*) AS orders_with_review,
    ROUND(AVG(r.average_review_score), 2) AS avg_review_score
FROM delivery AS d
JOIN review_per_order AS r ON d.order_id = r.order_id
GROUP BY d.delivery_group
ORDER BY d.delivery_group;

-- 6. Customer-state contribution
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers
FROM olist_orders_dataset AS o
JOIN olist_customers_dataset AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY order_count DESC;
