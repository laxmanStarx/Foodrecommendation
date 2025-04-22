# # ai_service/main.py
# from fastapi import FastAPI
# import pandas as pd
# import psycopg2
# from sklearn.metrics.pairwise import cosine_similarity
#
# app = FastAPI()
#
# # Your DB credentials
# DB_CONFIG = {
#     "host": settings.DB_HOST,
#     "database": settings.DB_NAME,
#     "user": settings.DB_USER,
#     "password": settings.DB_PASSWORD,
#     "sslmode": settings.DB_SSLMODE,
# }
#
#
#
#
# @app.get("/recommend")
# def recommend(user_id: str):
#     try:
#         # ✅ Open connection inside route
#         conn = psycopg2.connect(**DB_CONFIG)
#
#         # ✅ Query based on your actual schema
#         df = pd.read_sql("""
#             SELECT
#                 o."userId" AS user_id,
#                 m.id AS product_id,
#                 m.category
#             FROM "Order" o
#             JOIN "OrderItem" oi ON o.id = oi."orderId"
#             JOIN "Menu" m ON oi."menuId" = m.id
#
#         """, conn)
#
#         conn.close()  # ✅ Always close connection after use
#
#
#
#         if df.empty:
#             return {"recommendations": [], "note": "No orders found in database."}
#
#         pivot = pd.crosstab(df['user_id'], df['product_id'])
#
#         if user_id not in pivot.index:
#             return {"recommendations": [], "note": "User not found or no interactions."}
#
#         print(df.head())  # See if any data was fetched at all
#         print(pivot.head())  # See the pivoted user-product matrix
#         print(pivot.index)  # List of user_ids in matrix
#
#         user_vector = pivot.loc[user_id].values.reshape(1, -1)
#         similarity = cosine_similarity(user_vector, pivot.values)[0]
#         similar_users = pivot.index[similarity.argsort()[::-1][1:6]]
#
#         similar_products = df[df['user_id'].isin(similar_users)]['product_id'].unique().tolist()
#         print(df.head())  # See if any data was fetched at all
#         print(pivot.head())  # See the pivoted user-product matrix
#         print(pivot.index)  # List of user_ids in matrix
#
#         return {"recommendations": similar_products}
#
#
#
#     except Exception as e:
#         return {"error": f"Failed to fetch data: {e}"}










# from fastapi import FastAPI
# import pandas as pd
# import psycopg2
# from sklearn.metrics.pairwise import cosine_similarity
# import json
# from datetime import datetime
#
# app = FastAPI()
#
# DB_CONFIG = {
#     "host": settings.DB_HOST,
#     "database": settings.DB_NAME,
#     "user": settings.DB_USER,
#     "password": settings.DB_PASSWORD,
#     "sslmode": settings.DB_SSLMODE,
# }
#
#
# @app.get("/recommend")
# def recommend(user_id: str):
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         cur = conn.cursor()
#
#         df = pd.read_sql("""
#             SELECT
#                 o."userId" AS user_id,
#                 m.id AS product_id,
#                 m.category
#             FROM "Order" o
#             JOIN "OrderItem" oi ON o.id = oi."orderId"
#             JOIN "Menu" m ON oi."menuId" = m.id
#         """, conn)
#
#         if df.empty:
#             conn.close()
#             return {"recommendations": [], "note": "No orders found in database."}
#
#         pivot = pd.crosstab(df['user_id'], df['product_id'])
#
#         if user_id not in pivot.index:
#             conn.close()
#             return {"recommendations": [], "note": "User not found or no interactions."}
#
#         user_vector = pivot.loc[user_id].values.reshape(1, -1)
#         similarity = cosine_similarity(user_vector, pivot.values)[0]
#         similar_users = pivot.index[similarity.argsort()[::-1][1:6]]
#
#         similar_products = df[df['user_id'].isin(similar_users)]['product_id'].unique().tolist()
#
#         # Convert to JSON string for insertion
#         products_json = json.dumps(similar_products)
#
#         # Upsert into Recommendation table
#         cur.execute("""
#             INSERT INTO "Recommendation" ("userId", "products", "createdAt", "updatedAt")
#             VALUES (%s, %s, %s, %s)
#             ON CONFLICT ("userId")
#             DO UPDATE SET "products" = EXCLUDED."products", "updatedAt" = EXCLUDED."updatedAt";
#         """, (user_id, products_json, datetime.utcnow(), datetime.utcnow()))
#
#         conn.commit()
#         cur.close()
#         conn.close()
#
#         return {"recommendations": similar_products, "note": "Stored in DB"}
#
#     except Exception as e:
#         return {"error": f"Failed to fetch or store data: {e}"}








# from fastapi import FastAPI
# import pandas as pd
# import psycopg2
# from psycopg2.extras import Json
#
# from sklearn.metrics.pairwise import cosine_similarity
# from datetime import datetime
# import uuid
# import json
#
# app = FastAPI()
#
# DB_CONFIG = {
#     "host": settings.DB_HOST,
#     "database": settings.DB_NAME,
#     "user": settings.DB_USER,
#     "password": settings.DB_PASSWORD,
#     "sslmode": settings.DB_SSLMODE,
# }
#
# @app.get("/recommend")
# def recommend(user_id: str):
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         cur = conn.cursor()
#
#         # Step 1: Fetch order data
#         df = pd.read_sql("""
#             SELECT
#                 o."userId" AS user_id,
#                 m.id AS product_id,
#                 m.category
#             FROM "Order" o
#             JOIN "OrderItem" oi ON o.id = oi."orderId"
#             JOIN "Menu" m ON oi."menuId" = m.id
#         """, conn)
#
#         if df.empty:
#             return {"recommendations": [], "note": "No orders found in database."}
#
#         pivot = pd.crosstab(df['user_id'], df['product_id'])
#
#         if user_id not in pivot.index:
#             return {"recommendations": [], "note": "User not found or no interactions."}
#
#         # Step 2: Generate recommendations
#         user_vector = pivot.loc[user_id].values.reshape(1, -1)
#         similarity = cosine_similarity(user_vector, pivot.values)[0]
#         similar_users = pivot.index[similarity.argsort()[::-1][1:6]]
#
#         similar_products = df[df['user_id'].isin(similar_users)]['product_id'].unique().tolist()
#
#         # Step 3: Insert recommendations into DB
#         recommendation_id = str(uuid.uuid4())
#         products_json = json.dumps(similar_products)
#         now = datetime.utcnow()
#
#         cur.execute("""
#             # INSERT INTO "Recommendation" ("id", "userId", "products", "createdAt", "updatedAt")
#             VALUES (%s, %s, %s, %s, %s)
#
#             ON CONFLICT ("userId")
#             DO UPDATE SET "products" = EXCLUDED."products", "updatedAt" = EXCLUDED."updatedAt";
#         """, (recommendation_id, user_id, products_json, now, now))
#
#         conn.commit()
#         cur.close()
#         conn.close()
#
#         return {"recommendations": similar_products, "note": "Stored in DB"}
#
#     except Exception as e:
#         return {"error": f"Failed: {e}"}




from fastapi import FastAPI
import pandas as pd
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import json
from config import settings
import uuid

app = FastAPI()





DB_CONFIG = {
    "host": settings.DB_HOST,
    "database": settings.DB_NAME,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "sslmode": settings.DB_SSLMODE,
}

@app.get("/recommend")
def recommend(user_id: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        df = pd.read_sql("""
            SELECT 
                o."userId" AS user_id,
                m.id AS product_id,
                m.category
            FROM "Order" o
            JOIN "OrderItem" oi ON o.id = oi."orderId"
            JOIN "Menu" m ON oi."menuId" = m.id
        """, conn)

        if df.empty:
            conn.close()
            return {"recommendations": [], "note": "No orders found."}

        pivot = pd.crosstab(df['user_id'], df['product_id'])

        if user_id not in pivot.index:
            conn.close()
            return {"recommendations": [], "note": "User not found or no interactions."}

        user_vector = pivot.loc[user_id].values.reshape(1, -1)
        similarity = cosine_similarity(user_vector, pivot.values)[0]
        similar_users = pivot.index[similarity.argsort()[::-1][1:6]]
        similar_products = df[df['user_id'].isin(similar_users)]['product_id'].unique().tolist()

        # ✅ Insert into Recommendation table
        recommendation_id = str(uuid.uuid4())
        now = datetime.utcnow()
        insert_query = """
            INSERT INTO "Recommendation" (id, "userId", products, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ("userId") DO UPDATE SET
              products = EXCLUDED.products,
              "updatedAt" = EXCLUDED."updatedAt"
        """
        cursor.execute(insert_query, (
            recommendation_id,
            user_id,
            json.dumps(similar_products),
            now,
            now
        ))
        conn.commit()
        conn.close()

        return {"recommendations": similar_products}

    except Exception as e:
        return {"error": f"Failed: {e}"}







