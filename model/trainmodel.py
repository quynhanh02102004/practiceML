import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.cluster import KMeans

def getConnect(server, port, database, username, password):
    try:
        connection_string = f'mysql+pymysql://{username}:{password}@{server}:{port}/{database}'
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print("Error = ", e)
        return None

def closeConnection(engine):
    if engine is not None:
        engine.dispose()

def cluster_model(server='localhost', port=3306, database='sakila', username='root', password='Anh20041002',
                  n_clusters=4, offset=0, limit=256):
    """
    Hàm thực hiện phân cụm khách hàng với phân trang.

    Parameters:
    - offset: int - Vị trí bắt đầu của dữ liệu
    - limit: int - Số lượng bản ghi tối đa trả về
    """
    engine = getConnect(server, port, database, username, password)
    if engine is None:
        print("Failed to connect to database!")
        return None

    query = f"""
    SELECT 
        c.customer_id,
        COUNT(r.rental_id) / (DATEDIFF(MAX(r.rental_date), MIN(r.rental_date)) / 30.0) AS rentals_per_month,
        COUNT(DISTINCT fc.category_id) AS genre_diversity,
        AVG(f.rental_rate) AS avg_rental_rate,
        AVG(inventory_rental_count) AS avg_inventory_usage
    FROM customer c
    LEFT JOIN rental r ON c.customer_id = r.customer_id
    LEFT JOIN inventory i ON r.inventory_id = i.inventory_id
    LEFT JOIN film f ON i.film_id = f.film_id
    LEFT JOIN film_category fc ON f.film_id = fc.film_id
    LEFT JOIN (
        SELECT inventory_id, COUNT(rental_id) AS inventory_rental_count
        FROM rental
        GROUP BY inventory_id
    ) inv ON r.inventory_id = inv.inventory_id
    GROUP BY c.customer_id
    LIMIT {limit} OFFSET {offset};
    """

    df = pd.read_sql(query, engine)
    closeConnection(engine)

    if df.empty:
        return None  # Không còn dữ liệu

    df.fillna(0, inplace=True)
    df.replace([np.inf, -np.inf], 0, inplace=True)

    features = ['rentals_per_month', 'genre_diversity', 'avg_rental_rate', 'avg_inventory_usage']
    X = df[features]

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X)

    return df